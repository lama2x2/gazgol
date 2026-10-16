# Проверяющая система урока 11.1 — не меняй этот файл.
import math
import random
import time

from tasks import LRUCache, TTLCache, endpoint_stats, flatten_json, sync_diff

rnd = random.Random(111)


def test_lru_cache():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1
    c.put("c", 3)                       # вытесняется b: a недавно читали
    assert c.get("b") is None and c.get("a") == 1 and c.get("c") == 3 and len(c) == 2
    c.put("a", 10)                      # обновление не увеличивает размер
    c.put("d", 4)                       # вытесняется c
    assert c.get("c", "нет") == "нет" and c.get("a") == 10 and len(c) == 2
    ref, cap = [], 5
    c = LRUCache(cap)
    for _ in range(3000):
        k = rnd.randint(0, 9)
        if rnd.random() < 0.5:
            c.put(k, k * 2)
            if k in ref:
                ref.remove(k)
            ref.append(k)
            if len(ref) > cap:
                ref.pop(0)
        else:
            got = c.get(k)
            if k in ref:
                ref.remove(k)
                ref.append(k)
                assert got == k * 2
            else:
                assert got is None
    big = LRUCache(50_000)
    t0 = time.perf_counter()
    for i in range(200_000):
        big.put(i, i)
        big.get(i // 2)
    assert time.perf_counter() - t0 < 2, "операции должны быть O(1)"


class Clock:
    def __init__(self):
        self.t = 100.0

    def __call__(self):
        return self.t


def test_ttl_cache():
    clk = Clock()
    c = TTLCache(10, clock=clk)
    c.set("a", 1)
    clk.t += 5
    c.set("b", 2)
    assert c.get("a") == 1 and len(c) == 2
    clk.t += 5                          # a истёк ровно сейчас
    assert c.get("a") is None and c.get("a", "x") == "x" and len(c) == 1
    c.set("b", 3)                       # перезапись продлевает срок
    clk.t += 9
    assert c.get("b") == 3
    c.delete("b")
    c.delete("нет-такого")
    assert c.get("b") is None and len(c) == 0
    for i in range(100):
        c.set(i, i)
    clk.t += 11
    assert len(c) == 0, "len считает только живые записи"


def test_sync_diff():
    assert sync_diff({1: "a", 2: "b"}, {2: "B", 3: "c"}) == ([3], [2], [1])
    assert sync_diff({}, {}) == ([], [], [])
    assert sync_diff({1: {"x": 1}}, {1: {"x": 1}}) == ([], [], [])
    db = {i: {"name": f"n{i}", "v": i % 7} for i in range(200_000)}
    api = {i: ({"name": f"n{i}", "v": i % 7} if i % 10 else {"name": "changed"}) for i in range(50_000, 250_000)}
    t0 = time.perf_counter()
    create, update, delete = sync_diff(db, api)
    assert time.perf_counter() - t0 < 2
    assert create == list(range(200_000, 250_000)) and delete == list(range(50_000))
    assert update == [i for i in range(50_000, 200_000) if i % 10 == 0]


def test_flatten_json():
    assert flatten_json({"a": {"b": [1, {"c": 2}]}, "d": "x"}) == {"a.b.0": 1, "a.b.1.c": 2, "d": "x"}
    assert flatten_json({"e": {}, "f": [], "g": None}) == {"e": {}, "f": [], "g": None}
    assert flatten_json([10, [20]]) == {"0": 10, "1.0": 20}
    assert flatten_json(5) == {"": 5}
    assert flatten_json({"2026": {"01": True}}) == {"2026.01": True}


def _p95(xs):
    xs = sorted(xs)
    return xs[math.ceil(0.95 * len(xs)) - 1]


def test_endpoint_stats():
    lines = [
        "t GET /api/users 200 10ms", "t GET /api/users?page=2 500 30ms", "t POST /api/users 201 5ms",
        "мусор", "", "t GET /health 200 1ms", "t GET /api/users 503 20ms",
    ]
    st = endpoint_stats(lines)
    assert st[("GET", "/api/users")] == (3, 0.667, 30)
    assert st[("POST", "/api/users")] == (1, 0.0, 5) and st[("GET", "/health")] == (1, 0.0, 1)
    assert len(st) == 3
    for n in (1, 20, 100, 137):
        times = [rnd.randint(1, 500) for _ in range(n)]
        codes = [rnd.choice([200, 200, 200, 404, 500, 502]) for _ in range(n)]
        ls = [f"t GET /x {c} {ms}ms" for c, ms in zip(codes, times)]
        cnt, err, p95 = endpoint_stats(ls)[("GET", "/x")]
        assert cnt == n and err == round(sum(c >= 500 for c in codes) / n, 3) and p95 == _p95(times), f"n={n}"
