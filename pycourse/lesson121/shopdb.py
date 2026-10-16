"""Учебная база урока 12.1: магазин и сотрудники. Не меняй этот файл.

    python3 pycourse/lesson121/shopdb.py "SELECT * FROM users LIMIT 5"   — песочница
"""
import random
import sqlite3
import sys

SCHEMA = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    created_at TEXT NOT NULL,          -- 'YYYY-MM-DD HH:MM:SS'
    banned_at TEXT                     -- NULL, если не заблокирован
);
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price INTEGER NOT NULL             -- текущая цена в рублях
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('paid', 'cancelled', 'new'))
);
CREATE TABLE order_items (
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    qty INTEGER NOT NULL,
    price INTEGER NOT NULL             -- цена на момент заказа
);
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    salary INTEGER NOT NULL,
    manager_id INTEGER REFERENCES employees(id)
);
"""

CITIES = ["Москва", "Казань", "Самара", "Пермь"]
CATS = ["книги", "электроника", "дом", "спорт", "игрушки"]
NAMES = ["Аня", "Борис", "Вера", "Глеб", "Дина", "Егор", "Женя", "Зоя", "Игорь", "Катя", "Лев", "Маша",
         "Нина", "Олег", "Петя", "Рита", "Саша", "Тимур", "Ульяна", "Фёдор", "Хасан", "Цезарь", "Чулпан",
         "Шамиль", "Эля", "Юра", "Яна", "Арсений", "Белла", "Влад"]


def seed(conn):
    rnd = random.Random(121)
    conn.executescript(SCHEMA)
    for i, name in enumerate(NAMES, 1):
        day = rnd.randint(1, 28)
        banned = f"2026-03-{rnd.randint(1, 28):02d} 12:00:00" if i % 7 == 0 else None
        conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                     (i, name, CITIES[i % len(CITIES)], f"2026-01-{day:02d} 10:00:00", banned))
    for i in range(1, 21):
        conn.execute("INSERT INTO products VALUES (?, ?, ?, ?)",
                     (i, f"товар {i}", CATS[i % len(CATS)], rnd.choice([150, 300, 450, 800, 1200, 2500])))
    order_id = 0
    for _ in range(220):
        user = rnd.randint(1, 24)                      # у пользователей 25–30 заказов нет
        order_id += 1
        ts = f"2026-{rnd.randint(2, 4):02d}-{rnd.randint(1, 28):02d} {rnd.randint(0, 23):02d}:{rnd.randint(0, 59):02d}:00"
        status = rnd.choice(["paid", "paid", "paid", "cancelled", "new"])
        conn.execute("INSERT INTO orders VALUES (?, ?, ?, ?)", (order_id, user, ts, status))
        for pid in rnd.sample(range(1, 21), rnd.randint(1, 4)):
            price = conn.execute("SELECT price FROM products WHERE id = ?", (pid,)).fetchone()[0]
            conn.execute("INSERT INTO order_items VALUES (?, ?, ?, ?)",
                         (order_id, pid, rnd.randint(1, 3), price - rnd.choice([0, 0, 50])))
    depts = ["backend", "frontend", "data", "qa"]
    for i in range(1, 26):
        dept = depts[i % 4]
        salary = rnd.choice([150, 180, 200, 200, 250, 300, 300, 350]) * 1000
        manager = None if i <= 4 else (i % 4) + 1
        conn.execute("INSERT INTO employees VALUES (?, ?, ?, ?, ?)", (i, f"сотрудник {i}", dept, salary, manager))
    conn.commit()


def connect():
    conn = sqlite3.connect(":memory:")
    seed(conn)
    return conn


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "SELECT name FROM sqlite_master WHERE type = 'table'"
    cur = connect().execute(q)
    cols = [d[0] for d in cur.description or []]
    rows = cur.fetchall()
    print(" | ".join(cols))
    for r in rows:
        print(" | ".join("NULL" if v is None else str(v) for v in r))
    print(f"({len(rows)} строк)")
