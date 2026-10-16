# Проверяющая система урока 12.2 — не меняй этот файл.
import random
import sqlite3
import time

import pytest

import tasks
from tasks import ConflictError, InsufficientFunds, get_or_create_user, transfer, upsert_products, withdraw_optimistic

SCHEMA = """
CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INTEGER NOT NULL, version INTEGER NOT NULL DEFAULT 0);
CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE);
CREATE TABLE products (sku TEXT PRIMARY KEY, name TEXT NOT NULL, price INTEGER NOT NULL);
CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, status TEXT, created_at TEXT, total INTEGER);
"""


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.executescript(SCHEMA)
    c.executemany("INSERT INTO accounts(id, balance) VALUES (?, ?)", [(1, 100), (2, 50), (3, 0)])
    c.commit()
    yield c
    c.close()


def balances(c):
    return dict(c.execute("SELECT id, balance FROM accounts").fetchall())


def test_transfer(conn):
    transfer(conn, 1, 2, 30)
    assert balances(conn) == {1: 70, 2: 80, 3: 0}
    with pytest.raises(InsufficientFunds):
        transfer(conn, 3, 1, 1)
    with pytest.raises(InsufficientFunds):
        transfer(conn, 1, 2, 71)
    assert balances(conn) == {1: 70, 2: 80, 3: 0}
    with pytest.raises(ValueError):
        transfer(conn, 1, 99, 10)
    assert balances(conn) == {1: 70, 2: 80, 3: 0}, "списание должно откатиться, если зачислить некуда"
    with pytest.raises(ValueError):
        transfer(conn, 42, 1, 10)
    transfer(conn, 1, 3, 70)
    assert balances(conn) == {1: 0, 2: 80, 3: 70}
    assert not conn.in_transaction, "транзакция должна быть завершена"


def test_get_or_create(conn):
    uid, created = get_or_create_user(conn, "Ann@Example.com ")
    assert created is True
    assert get_or_create_user(conn, "ann@example.com") == (uid, False)
    uid2, created2 = get_or_create_user(conn, "bob@example.com")
    assert created2 is True and uid2 != uid
    assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 2
    assert conn.execute("SELECT email FROM users WHERE id = ?", (uid,)).fetchone()[0] == "ann@example.com"


def test_upsert_products(conn):
    upsert_products(conn, [("a", "Чайник", 1000), ("b", "Кружка", 300)])
    upsert_products(conn, [("a", "Чайник 2.0", 1200), ("c", "Ложка", 50)])
    assert conn.execute("SELECT sku, name, price FROM products ORDER BY sku").fetchall() == \
        [("a", "Чайник 2.0", 1200), ("b", "Кружка", 300), ("c", "Ложка", 50)]
    rows = [(f"s{i}", f"товар {i}", i) for i in range(50_000)]
    t0 = time.perf_counter()
    upsert_products(conn, rows)
    upsert_products(conn, [(s, n, p + 1) for s, n, p in rows])
    assert time.perf_counter() - t0 < 2, "пакетная загрузка: executemany в одной транзакции"
    assert conn.execute("SELECT COUNT(*), SUM(price) FROM products").fetchone() == (50_003, sum(range(50_000)) + 50_000 + 1550)
    assert not conn.in_transaction


def test_optimistic(conn):
    assert withdraw_optimistic(conn, 1, 30) == 70
    assert conn.execute("SELECT balance, version FROM accounts WHERE id = 1").fetchone() == (70, 1)
    with pytest.raises(InsufficientFunds):
        withdraw_optimistic(conn, 1, 71)

    calls = {"n": 0}

    def rival():                         # чужая транзакция успевает изменить строку
        calls["n"] += 1
        if calls["n"] <= 2:
            conn.execute("UPDATE accounts SET balance = balance - 5, version = version + 1 WHERE id = 1")
            conn.commit()

    assert withdraw_optimistic(conn, 1, 10, attempts=3, before_write=rival) == 50, "две чужие записи по 5, затем наша"
    assert calls["n"] == 3
    assert conn.execute("SELECT version FROM accounts WHERE id = 1").fetchone()[0] == 4

    def always():
        conn.execute("UPDATE accounts SET version = version + 1 WHERE id = 2")
        conn.commit()

    with pytest.raises(ConflictError):
        withdraw_optimistic(conn, 2, 10, attempts=3, before_write=always)
    assert conn.execute("SELECT balance FROM accounts WHERE id = 2").fetchone()[0] == 50


def test_indexes():
    c = sqlite3.connect(":memory:")
    c.executescript(SCHEMA)
    rnd = random.Random(122)
    c.executemany("INSERT INTO orders(user_id, status, created_at, total) VALUES (?, ?, ?, ?)",
                  [(rnd.randint(1, 500), rnd.choice(["paid", "new", "cancelled"]), f"2026-{rnd.randint(1, 12):02d}-{rnd.randint(1, 28):02d}",
                    rnd.randint(100, 9000)) for _ in range(20_000)])
    assert tasks.INDEXES, "добавь хотя бы один CREATE INDEX"
    for ddl in tasks.INDEXES:
        c.execute(ddl)
    c.execute("ANALYZE")
    q = "SELECT created_at, total FROM orders WHERE user_id = ? AND status = 'paid' ORDER BY created_at DESC LIMIT 20"
    plan = " | ".join(r[-1] for r in c.execute("EXPLAIN QUERY PLAN " + q, (7,)).fetchall())
    assert "COVERING INDEX" in plan, f"запрос должен читать только индекс; план: {plan}"
    assert "TEMP B-TREE" not in plan, f"осталась сортировка; план: {plan}"
    want = sorted(((d, t) for u, s, d, t in c.execute("SELECT user_id, status, created_at, total FROM orders")
                   if u == 7 and s == "paid"), key=lambda r: r[0], reverse=True)[:20]
    got = c.execute(q, (7,)).fetchall()
    assert [r[0] for r in got] == [r[0] for r in want]
