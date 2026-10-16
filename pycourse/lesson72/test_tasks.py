# Проверяющая система урока 7.2 — не меняй этот файл.
import inspect
import itertools
import random
import time

import tasks
from tasks import is_palindrome, merge_unique, remove_duplicates, three_sum, trap_water

rnd = random.Random(72)


def test_merge_unique():
    src = inspect.getsource(tasks.merge_unique)
    assert "set(" not in src and "sorted(" not in src and ".sort(" not in src, "без set и sorted — двумя указателями"
    assert merge_unique([1, 2, 2, 5], [2, 3, 5, 7]) == [1, 2, 3, 5, 7]
    assert merge_unique([], []) == []
    assert merge_unique([1, 1, 1], []) == [1]
    assert merge_unique([], [0, 0, 4]) == [0, 4]
    assert merge_unique([-3, 0], [-5, 10, 10]) == [-5, -3, 0, 10]
    for _ in range(300):
        a = sorted(rnd.randint(-5, 5) for _ in range(rnd.randint(0, 8)))
        b = sorted(rnd.randint(-5, 5) for _ in range(rnd.randint(0, 8)))
        assert merge_unique(a, b) == sorted(set(a) | set(b)), f"merge_unique({a}, {b})"


def test_is_palindrome():
    assert is_palindrome("A man, a plan, a canal: Panama") is True
    assert is_palindrome("race a car") is False
    assert is_palindrome("") is True and is_palindrome(" .,!") is True
    assert is_palindrome("0P") is False
    assert is_palindrome("Аргентина манит негра") is True
    assert is_palindrome("ab_a") is True
    for _ in range(300):
        s = "".join(rnd.choice("aAb1 ,.") for _ in range(rnd.randint(0, 9)))
        clean = [c.lower() for c in s if c.isalnum()]
        assert is_palindrome(s) == (clean == clean[::-1]), repr(s)


def test_remove_duplicates():
    a = [1, 1, 2, 3, 3, 3, 7]
    ref = a
    k = remove_duplicates(a)
    assert k == 4 and a[:4] == [1, 2, 3, 7] and a is ref
    assert remove_duplicates([]) == 0
    b = [5]
    assert remove_duplicates(b) == 1 and b[:1] == [5]
    for _ in range(200):
        a = sorted(rnd.randint(0, 6) for _ in range(rnd.randint(0, 12)))
        want = sorted(set(a))
        k = remove_duplicates(a)
        assert k == len(want) and a[:k] == want


def _three_slow(nums):
    return sorted({tuple(sorted(c)) for c in itertools.combinations(nums, 3) if sum(c) == 0})


def test_three_sum():
    assert three_sum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]]
    assert three_sum([0, 0, 0, 0]) == [[0, 0, 0]]
    assert three_sum([1, 2]) == []
    for _ in range(200):
        a = [rnd.randint(-6, 6) for _ in range(rnd.randint(0, 12))]
        assert [tuple(t) for t in three_sum(a)] == _three_slow(a), f"three_sum({a})"
    big = [rnd.randint(-10**5, 10**5) for _ in range(1500)]
    t0 = time.perf_counter()
    three_sum(big)
    assert time.perf_counter() - t0 < 3, "нужно O(n²)"


def _trap_slow(h):
    return sum(max(0, min(max(h[:i + 1]), max(h[i:])) - h[i]) for i in range(len(h)))


def test_trap_water():
    assert trap_water([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    assert trap_water([4, 2, 0, 3, 2, 5]) == 9
    assert trap_water([]) == 0 and trap_water([5]) == 0 and trap_water([1, 2, 3]) == 0
    for _ in range(300):
        h = [rnd.randint(0, 6) for _ in range(rnd.randint(0, 12))]
        assert trap_water(h) == _trap_slow(h), f"trap_water({h})"
    big = [rnd.randint(0, 10**4) for _ in range(200_000)]
    t0 = time.perf_counter()
    trap_water(big)
    assert time.perf_counter() - t0 < 1.5, "нужно O(n)"
