# Проверяющая система урока 7.4 — не меняй этот файл.
import bisect
import inspect
import random

import tasks
from tasks import find_valley, lower_bound, min_ship_capacity, search_range, search_rotated

rnd = random.Random(74)


class Counting(list):
    """Список, который считает обращения по индексу."""

    reads = 0

    def __getitem__(self, i):
        Counting.reads += 1
        return super().__getitem__(i)


def test_lower_bound():
    assert "bisect" not in inspect.getsource(tasks).split("def lower_bound")[1], "без bisect"
    assert lower_bound([], 5) == 0
    assert lower_bound([1, 2, 2, 4], 2) == 1 and lower_bound([1, 2, 2, 4], 3) == 3 and lower_bound([1, 2], 9) == 2
    for _ in range(500):
        a = sorted(rnd.randint(0, 9) for _ in range(rnd.randint(0, 10)))
        x = rnd.randint(-1, 10)
        assert lower_bound(a, x) == bisect.bisect_left(a, x), f"lower_bound({a}, {x})"
    big = Counting(range(10**6))
    Counting.reads = 0
    assert lower_bound(big, 765_432) == 765_432
    assert Counting.reads < 60, f"обращений к массиву: {Counting.reads} — это не O(log n)"


def test_search_range():
    assert search_range([5, 7, 7, 8, 8, 10], 8) == (3, 4)
    assert search_range([5, 7, 7, 8, 8, 10], 6) == (-1, -1)
    assert search_range([], 0) == (-1, -1)
    assert search_range([1], 1) == (0, 0)
    for _ in range(500):
        a = sorted(rnd.randint(0, 5) for _ in range(rnd.randint(0, 10)))
        x = rnd.randint(-1, 6)
        want = (a.index(x), len(a) - 1 - a[::-1].index(x)) if x in a else (-1, -1)
        assert tuple(search_range(a, x)) == want, f"search_range({a}, {x})"
    same = Counting([7] * 10**6)
    Counting.reads = 0
    assert tuple(search_range(same, 7)) == (0, 10**6 - 1)
    assert Counting.reads < 120, f"обращений: {Counting.reads} — нужно O(log n), без расширения в стороны"


def test_search_rotated():
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1
    assert search_rotated([1], 0) == -1 and search_rotated([1], 1) == 0
    assert search_rotated([], 1) == -1
    assert search_rotated([3, 1], 1) == 1
    for _ in range(500):
        n = rnd.randint(1, 12)
        base = sorted(rnd.sample(range(30), n))
        k = rnd.randrange(n)
        a = base[k:] + base[:k]
        x = rnd.randint(-1, 30)
        want = a.index(x) if x in a else -1
        assert search_rotated(a, x) == want, f"search_rotated({a}, {x})"
    big = list(range(10**6))
    big = Counting(big[300_000:] + big[:300_000])
    Counting.reads = 0
    assert search_rotated(big, 5) == 700_005
    assert Counting.reads < 200, f"обращений: {Counting.reads} — это не O(log n)"


def _ship_slow(w, days):
    cap = max(w)
    while True:
        d, cur = 1, 0
        for x in w:
            if cur + x > cap:
                d, cur = d + 1, 0
            cur += x
        if d <= days:
            return cap
        cap += 1


def test_min_ship_capacity():
    assert min_ship_capacity([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15
    assert min_ship_capacity([3, 2, 2, 4, 1, 4], 3) == 6
    assert min_ship_capacity([1, 2, 3, 1, 1], 4) == 3
    assert min_ship_capacity([10], 3) == 10
    for _ in range(200):
        w = [rnd.randint(1, 9) for _ in range(rnd.randint(1, 9))]
        d = rnd.randint(1, len(w))
        assert min_ship_capacity(w, d) == _ship_slow(w, d), f"min_ship_capacity({w}, {d})"
    assert min_ship_capacity([10**6] * 1000 + [1], 1) == 10**9 + 1


def test_find_valley():
    for a in ([5, 3, 4], [1, 2, 3], [3, 2, 1], [7], [2, 1, 3, 0, 5]):
        i = find_valley(a)
        left = a[i - 1] if i > 0 else float("inf")
        right = a[i + 1] if i + 1 < len(a) else float("inf")
        assert a[i] < left and a[i] < right, f"find_valley({a}) = {i} — это не впадина"
    for _ in range(400):
        n = rnd.randint(1, 15)
        a = rnd.sample(range(-50, 50), n)
        i = find_valley(a)
        assert 0 <= i < n
        assert (i == 0 or a[i] < a[i - 1]) and (i == n - 1 or a[i] < a[i + 1]), f"find_valley({a}) = {i}"
    big = Counting(list(range(10**6, 0, -1)))
    Counting.reads = 0
    i = find_valley(big)
    assert i == 10**6 - 1
    assert Counting.reads < 100, f"обращений: {Counting.reads} — нужно O(log n)"
