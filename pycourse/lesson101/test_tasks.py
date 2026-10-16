# Проверяющая система урока 10.1 — не меняй этот файл.
import inspect
import itertools
import random
import time

import tasks
from tasks import combination_sum, generate_parentheses, n_queens, permutations, subsets

rnd = random.Random(101)


def _no_itertools():
    src = inspect.getsource(tasks).split("\n", 5)[-1]
    assert "itertools" not in src, "без itertools: смысл задачи — написать перебор самому"


def test_subsets():
    _no_itertools()
    assert subsets([1, 2, 3]) == [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
    assert subsets([]) == [[]]
    assert subsets([5]) == [[], [5]]
    a = list(range(12))
    res = subsets(a)
    assert len(res) == 4096 and len({tuple(s) for s in res}) == 4096


def test_permutations():
    _no_itertools()
    assert permutations([1, 2, 3]) == [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
    assert permutations([]) == [[]]
    for n in range(1, 7):
        a = rnd.sample(range(-20, 20), n)
        assert permutations(a) == [list(p) for p in itertools.permutations(a)]


def test_generate_parentheses():
    assert generate_parentheses(1) == ["()"]
    assert generate_parentheses(3) == ["((()))", "(()())", "(())()", "()(())", "()()()"]
    assert generate_parentheses(0) == [""]
    t0 = time.perf_counter()
    res = generate_parentheses(12)
    assert len(res) == 208012 and res == sorted(res)
    assert time.perf_counter() - t0 < 3, "генерируй только правильные, без фильтра всех строк"


def _cs_slow(c, t):
    out = set()

    def go(rem, start, path):
        if rem == 0:
            out.add(tuple(path))
            return
        for i in range(start, len(c)):
            if c[i] <= rem:
                go(rem - c[i], i, path + [c[i]])
    go(t, 0, [])
    return sorted(list(x) for x in out)


def test_combination_sum():
    assert combination_sum([2, 3, 6, 7], 7) == [[2, 2, 3], [7]]
    assert combination_sum([2, 3, 5], 8) == [[2, 2, 2, 2], [2, 3, 3], [3, 5]]
    assert combination_sum([2], 1) == []
    assert combination_sum([7, 3, 2], 7) == [[2, 2, 3], [7]], "кандидаты могут быть не отсортированы"
    for _ in range(100):
        c = rnd.sample(range(1, 12), rnd.randint(1, 5))
        t = rnd.randint(1, 20)
        assert combination_sum(c, t) == _cs_slow(sorted(c), t), f"{c}, {t}"


def test_n_queens():
    assert [n_queens(n) for n in range(1, 9)] == [1, 0, 0, 2, 10, 4, 40, 92]
    t0 = time.perf_counter()
    assert n_queens(10) == 724
    assert time.perf_counter() - t0 < 3, "проверяй столбцы и диагонали множествами за O(1)"
