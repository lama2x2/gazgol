# Проверяющая система урока 3.2 — не меняй этот файл.
import inspect
import itertools
import random
import tracemalloc
import types

import pytest

import tasks
from tasks import MyRange, chunked, flatten, merge_sorted, top_urls


@pytest.mark.parametrize("args", [(0, 5), (1, 10, 3), (10, 0, -2), (5, 5), (5, 0), (0, 5, -1), (-3, 4, 2), (9, -1, -3), (0, 1)])
def test_my_range(args):
    r = MyRange(*args)
    want = list(range(*args))
    assert list(r) == want, f"list(MyRange{args})"
    assert list(r) == want, "второй проход пуст — __iter__ должен каждый раз отдавать новый итератор"
    assert len(r) == len(want), f"len(MyRange{args})"
    for x in range(-5, 12):
        assert (x in r) == (x in range(*args)), f"{x} in MyRange{args}"
    it1, it2 = iter(r), iter(r)
    if want:
        assert next(it1) == want[0] and next(it2) == want[0], "итераторы должны быть независимыми"


def test_my_range__big():
    r = MyRange(0, 10**15, 2)
    assert 10**12 in r and 10**12 + 1 not in r and 10**15 not in r, "__contains__ должен работать за O(1)"
    assert len(r) == 5 * 10**14
    with pytest.raises(ValueError):
        MyRange(0, 5, 0)


def test_chunked():
    assert list(chunked(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]]
    assert list(chunked([], 4)) == []
    assert list(chunked("abcd", 2)) == [["a", "b"], ["c", "d"]]
    first = list(itertools.islice(chunked(itertools.count(), 2), 3))
    assert first == [[0, 1], [2, 3], [4, 5]], "должно работать с бесконечным итератором"
    assert isinstance(chunked([1], 1), types.GeneratorType) or hasattr(chunked([1], 1), "__next__")


def test_flatten():
    res = flatten([1, [2, (3, [4])], "ab", [[[]]], [[5, [6]]]])
    assert isinstance(res, types.GeneratorType), "flatten должен быть генератором"
    assert list(res) == [1, 2, 3, 4, "ab", 5, 6]
    assert list(flatten([])) == []
    assert list(flatten(["x", ["yz"]])) == ["x", "yz"], "строки не раскладываются"
    deep = [0]
    for i in range(1, 50):
        deep = [deep, i]
    assert list(flatten(deep)) == list(range(50))


def _log(n, rnd):
    urls = ["/api/users", "/api/items", "/health", "/api/orders", "/login"] + [f"/item/{i}" for i in range(50)]
    weights = [50, 30, 10, 30, 5] + [1] * 50
    for i in range(n):
        if i % 997 == 0:
            yield ""
        elif i % 1009 == 0:
            yield "битая"
        else:
            u = rnd.choices(urls, weights)[0]
            yield f"2026-01-01T10:{i % 60:02d}:00 GET {u} 200 {i % 90}ms"


def test_top_urls():
    lines = ["t GET /a 200 1ms", "t GET /b 200 1ms", "t POST /a 201 3ms", "", "t GET /c 500 9ms", "t GET /b 200 1ms", "x y"]
    assert top_urls(lines, 2) == [("/a", 2), ("/b", 2)]
    assert top_urls(lines, 10) == [("/a", 2), ("/b", 2), ("/c", 1)]
    assert top_urls([], 3) == []
    big = top_urls(_log(20_000, random.Random(7)), 2)
    assert [u for u, _ in big] == ["/api/users", "/api/items"] or [u for u, _ in big] == ["/api/users", "/api/orders"]
    assert big[0][1] > big[1][1] > 0


def test_top_urls__streaming():
    n = 200_000
    tracemalloc.start()
    try:
        res = top_urls(_log(n, random.Random(1)), 3)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert [u for u, _ in res][:1] == ["/api/users"]
    assert peak < 8 * 1024 * 1024, f"пик памяти {peak // 1024 // 1024} МБ: лог нельзя загружать целиком"


def test_merge_sorted():
    src = inspect.getsource(tasks.merge_sorted)
    assert "heapq.merge" not in src and "sorted(" not in src.replace("merge_sorted(", ""), "без heapq.merge и sorted"
    assert list(merge_sorted([1, 4, 9], [2, 3], [], [5])) == [1, 2, 3, 4, 5, 9]
    assert list(merge_sorted()) == []
    assert list(merge_sorted([], [])) == []
    rnd = random.Random(3)
    for _ in range(100):
        parts = [sorted(rnd.randint(0, 20) for _ in range(rnd.randint(0, 6))) for _ in range(rnd.randint(1, 5))]
        assert list(merge_sorted(*parts)) == sorted(x for p in parts for x in p), f"merge_sorted{tuple(parts)}"
    evens, odds = itertools.count(0, 2), itertools.count(1, 2)
    assert list(itertools.islice(merge_sorted(evens, odds), 7)) == [0, 1, 2, 3, 4, 5, 6], "ленивое слияние бесконечных"
    tagged = list(merge_sorted([(1, "a")], [(1, "b")], [(0, "c")]))
    assert tagged == [(0, "c"), (1, "a"), (1, "b")]

    class K:
        def __init__(self, v): self.v = v
        def __lt__(self, o): return self.v < o.v
        def __eq__(self, o): return self.v == o.v
    out = [k.v for k in merge_sorted([K(1), K(3)], [K(1), K(2)])]
    assert out == [1, 1, 2, 3], "при равных значениях нельзя сравнивать сами итераторы"
