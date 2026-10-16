# Проверяющая система урока 12.1 — не меняй этот файл.
# Ожидаемые ответы считаются на Python по тем же данным, а не готовыми SQL-запросами.
from collections import defaultdict
from datetime import datetime, timedelta

import pytest

import shopdb
import tasks


@pytest.fixture(scope="module")
def db():
    conn = shopdb.connect()
    yield conn
    conn.close()


def rows(conn, table):
    cur = conn.execute(f"SELECT * FROM {table}")
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def run(conn, q):
    try:
        return [tuple(r) for r in conn.execute(q).fetchall()]
    except Exception as e:  # noqa: BLE001
        pytest.fail(f"запрос не выполнился: {e}")


def paid_order_totals(conn):
    orders = {o["id"]: o for o in rows(conn, "orders") if o["status"] == "paid"}
    total = defaultdict(int)
    for it in rows(conn, "order_items"):
        if it["order_id"] in orders:
            total[it["order_id"]] += it["qty"] * it["price"]
    return orders, total


def test_users_without_orders(db):
    users = {o["user_id"] for o in rows(db, "orders")}
    want = sorted((u["name"],) for u in rows(db, "users") if u["id"] not in users)
    assert run(db, tasks.Q_USERS_WITHOUT_ORDERS) == want


def test_revenue_by_category(db):
    orders, _ = paid_order_totals(db)
    cat = {p["id"]: p["category"] for p in rows(db, "products")}
    rev = defaultdict(int)
    for it in rows(db, "order_items"):
        if it["order_id"] in orders:
            rev[cat[it["product_id"]]] += it["qty"] * it["price"]
    want = sorted(((c, r) for c, r in rev.items() if r > 50000), key=lambda x: -x[1])
    got = run(db, tasks.Q_REVENUE_BY_CATEGORY)
    assert got == want, "проверь: только paid, цена из order_items, HAVING > 50000, сортировка по убыванию"


def test_top2_salary(db):
    emp = rows(db, "employees")
    want = []
    for d in sorted({e["department"] for e in emp}):
        top = sorted({e["salary"] for e in emp if e["department"] == d}, reverse=True)[:2]
        want += [(d, e["name"], e["salary"]) for e in emp if e["department"] == d and e["salary"] in top]
    want.sort(key=lambda r: (r[0], -r[2], r[1]))
    assert run(db, tasks.Q_TOP2_SALARY) == want, "две наибольшие РАЗЛИЧНЫЕ зарплаты: DENSE_RANK"


def test_running_gmv(db):
    orders, total = paid_order_totals(db)
    by_day = defaultdict(int)
    for oid, t in total.items():
        by_day[orders[oid]["created_at"][:10]] += t
    want, acc = [], 0
    for day in sorted(by_day):
        acc += by_day[day]
        want.append((day, by_day[day], acc))
    assert run(db, tasks.Q_RUNNING_GMV) == want


def test_second_salary(db):
    sal = sorted({e["salary"] for e in rows(db, "employees")}, reverse=True)
    assert run(db, tasks.Q_SECOND_SALARY) == [(sal[1],)]
    extra = shopdb.connect()
    extra.execute("UPDATE employees SET salary = 100")
    assert run(extra, tasks.Q_SECOND_SALARY) == [(None,)], "если второй нет — одна строка с NULL"
    extra.execute("UPDATE employees SET salary = 500 WHERE id IN (1, 2)")
    assert run(extra, tasks.Q_SECOND_SALARY) == [(100,)], "две одинаковые максимальные — вторая различная ниже"


def test_first_week(db):
    orders, total = paid_order_totals(db)
    first = {}
    for o in orders.values():
        first[o["user_id"]] = min(first.get(o["user_id"], o["created_at"]), o["created_at"])
    rev = defaultdict(int)
    for oid, t in total.items():
        o = orders[oid]
        start = datetime.fromisoformat(first[o["user_id"]])
        if datetime.fromisoformat(o["created_at"]) < start + timedelta(days=7):
            rev[o["user_id"]] += t
    want = [(u, first[u][:10], rev[u]) for u in sorted(first)]
    assert run(db, tasks.Q_FIRST_WEEK) == want
