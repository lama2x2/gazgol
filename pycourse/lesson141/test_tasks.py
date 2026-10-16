# Проверяющая система урока 14.1 — не меняй этот файл.
import json
import sqlite3
from collections import Counter

import pytest

from tasks import SCHEMA, HashRing, IdempotentConsumer, OutboxService, TokenBucket, backoff_delays


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_token_bucket():
    clk = Clock()
    b = TokenBucket(rate=2, capacity=5, clock=clk)
    assert [b.allow() for _ in range(6)] == [True] * 5 + [False], "стартует полным, ёмкость 5"
    clk.t += 1                       # +2 токена
    assert b.allow() and b.allow() and not b.allow()
    clk.t += 100                     # не больше ёмкости
    assert sum(b.allow() for _ in range(10)) == 5
    clk.t += 1.5
    assert b.allow(cost=3) and not b.allow(cost=1)
    assert len(vars(b)) <= 6, "храни несколько чисел, а не историю запросов"


def test_backoff_delays():
    assert backoff_delays(7, base=0.1, cap=2, jitter=False) == pytest.approx([0.1, 0.2, 0.4, 0.8, 1.6, 2.0, 2.0])
    seq = iter([0.5, 0.25, 1.0, 0.0])
    assert backoff_delays(4, base=1, factor=3, cap=100, rand=lambda: next(seq)) == pytest.approx([0.5, 0.75, 9.0, 0.0])
    assert backoff_delays(0) == []


def test_idempotent_consumer():
    done = []
    fail = {"n": 2}

    def handler(m):
        if m.get("flaky") and fail["n"] > 0:
            fail["n"] -= 1
            raise ConnectionError("временная ошибка")
        done.append(m["id"])

    c = IdempotentConsumer(handler, max_ids=3)
    assert c.handle({"id": 1}) == "ok" and c.handle({"id": 1}) == "duplicate"
    for _ in range(2):
        with pytest.raises(ConnectionError):
            c.handle({"id": 2, "flaky": True})
    assert c.handle({"id": 2, "flaky": True}) == "ok", "упавшее сообщение не помечается обработанным"
    assert done == [1, 2]
    for i in range(3, 7):
        c.handle({"id": i})
    assert c.handle({"id": 6}) == "duplicate"
    assert c.handle({"id": 1}) == "ok", "старые id вытесняются: хранится не больше max_ids"
    assert len(done) == 7


def test_outbox():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    svc = OutboxService(conn)
    o1 = svc.create_order(7, 1500)
    o2 = svc.create_order(8, 300)
    with pytest.raises(sqlite3.IntegrityError):
        svc.create_order(9, -1)      # CHECK (total > 0)
    assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 2
    assert conn.execute("SELECT COUNT(*) FROM outbox").fetchone()[0] == 2, "упавший заказ — без события"
    got, broken = [], {"on": True}

    def publish(event, payload):
        if broken["on"] and payload["order_id"] == o2:
            raise ConnectionError("брокер недоступен")
        got.append((event, payload))

    assert svc.relay(publish) == 1
    assert got == [("OrderCreated", {"order_id": o1, "user_id": 7, "total": 1500})]
    broken["on"] = False
    assert svc.relay(publish) == 1 and got[-1][1]["order_id"] == o2
    assert svc.relay(publish) == 0, "отправленное повторно не публикуется"
    assert not conn.in_transaction


def test_hash_ring():
    ring = HashRing(["a", "b", "c", "d"], vnodes=150)
    keys = [f"user:{i}" for i in range(20_000)]
    before = {k: ring.get(k) for k in keys}
    load = Counter(before.values())
    assert set(load) == {"a", "b", "c", "d"}
    assert max(load.values()) < 1.4 * min(load.values()), f"распределение неровное: {load}"
    assert HashRing(["a", "b", "c", "d"], vnodes=150).get("user:42") == before["user:42"], "хеш должен быть стабильным"
    ring.add("e")
    after = {k: ring.get(k) for k in keys}
    moved = sum(before[k] != after[k] for k in keys) / len(keys)
    assert 0.1 < moved < 0.3, f"переехало {moved:.0%} ключей, ожидается около 20%"
    assert all(after[k] in (before[k], "e") for k in keys), "ключи переезжают только на новый узел"
    ring.remove("e")
    assert {k: ring.get(k) for k in keys} == before
    with pytest.raises(Exception):
        HashRing([]).get("x")
