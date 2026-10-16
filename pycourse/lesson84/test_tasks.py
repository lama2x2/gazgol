# Проверяющая система урока 8.4 — не меняй этот файл.
import inspect
import random
import re
import statistics
import time

import pytest

import tasks
from tasks import MedianFinder, kth_largest, merge_intervals, merge_k_sorted, min_meeting_rooms

rnd = random.Random(84)


def test_kth_largest():
    src = inspect.getsource(tasks.kth_largest)
    assert "heap" in src and not re.search(r"\bsorted\(|\.sort\(", src), "реши кучей"
    assert kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
    assert kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4
    assert kth_largest([3, 3, 1], 2) == 3 and kth_largest([7], 1) == 7
    for _ in range(300):
        a = [rnd.randint(-9, 9) for _ in range(rnd.randint(1, 12))]
        k = rnd.randint(1, len(a))
        assert kth_largest(a, k) == sorted(a)[-k], f"{a}, k={k}"


def _merge_slow(iv):
    res = []
    for s, e in sorted(iv):
        if res and s <= res[-1][1]:
            res[-1][1] = max(res[-1][1], e)
        else:
            res.append([s, e])
    return res


def test_merge_intervals():
    assert merge_intervals([[1, 3], [8, 10], [2, 6], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
    assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]], "касание — пересечение"
    assert merge_intervals([[1, 10], [2, 3], [4, 5]]) == [[1, 10]], "вложенные"
    assert merge_intervals([]) == []
    src = [[5, 6], [1, 2]]
    assert merge_intervals(src) == [[1, 2], [5, 6]] and src == [[5, 6], [1, 2]], "не меняй вход"
    for _ in range(300):
        iv = []
        for _ in range(rnd.randint(0, 8)):
            s = rnd.randint(0, 15)
            iv.append([s, s + rnd.randint(0, 5)])
        got = merge_intervals([list(x) for x in iv])
        cover = {x for s, e in iv for x in range(s * 2, e * 2 + 1)}
        assert {x for s, e in got for x in range(s * 2, e * 2 + 1)} == cover, f"{iv} → {got}"
        assert all(got[i][1] < got[i + 1][0] for i in range(len(got) - 1)), f"{iv} → {got}: остались пересечения"


def test_min_meeting_rooms():
    assert min_meeting_rooms([(0, 30), (5, 10), (15, 20)]) == 2
    assert min_meeting_rooms([(7, 10), (2, 4)]) == 1
    assert min_meeting_rooms([(1, 3), (3, 5)]) == 1, "встреча освобождает комнату ровно в end"
    assert min_meeting_rooms([]) == 0
    assert min_meeting_rooms([(1, 5)] * 4) == 4
    for _ in range(300):
        ms = []
        for _ in range(rnd.randint(0, 10)):
            s = rnd.randint(0, 20)
            ms.append((s, s + rnd.randint(1, 6)))
        want = max([sum(1 for s, e in ms if s <= t < e) for t in range(30)], default=0)
        assert min_meeting_rooms(ms) == want, f"{ms}"


def test_merge_k_sorted():
    src = inspect.getsource(tasks.merge_k_sorted)
    assert "heap" in src and not re.search(r"\bsorted\(|\.sort\(", src), "реши кучей, без сортировки"
    assert merge_k_sorted([[1, 4, 5], [1, 3, 4], [2, 6]]) == [1, 1, 2, 3, 4, 4, 5, 6]
    assert merge_k_sorted([]) == [] and merge_k_sorted([[], []]) == []
    for _ in range(200):
        ls = [sorted(rnd.randint(0, 20) for _ in range(rnd.randint(0, 6))) for _ in range(rnd.randint(0, 6))]
        assert merge_k_sorted(ls) == sorted(x for l in ls for x in l)
    big = [list(range(i, 200_000, 100)) for i in range(100)]
    t0 = time.perf_counter()
    assert merge_k_sorted(big) == list(range(200_000))
    assert time.perf_counter() - t0 < 2


def test_median_finder():
    m = MedianFinder()
    with pytest.raises(ValueError):
        m.median()
    m.add(1)
    assert m.median() == 1
    m.add(2)
    assert m.median() == 1.5
    m.add(3)
    assert m.median() == 2
    m = MedianFinder()
    seen = []
    for _ in range(3000):
        x = rnd.randint(-1000, 1000)
        m.add(x)
        seen.append(x)
        if len(seen) % 97 == 0:
            assert m.median() == statistics.median(seen)
    t0 = time.perf_counter()
    m = MedianFinder()
    for i in range(100_000):
        m.add(i if i % 2 else -i)
        m.median()
    assert time.perf_counter() - t0 < 2, "add должен быть O(log n), median — O(1)"
