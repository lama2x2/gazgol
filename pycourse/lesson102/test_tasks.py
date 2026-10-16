# Проверяющая система урока 10.2 — не меняй этот файл.
import functools
import itertools
import random
import time

from tasks import MOD, climb_stairs, coin_change, edit_distance, house_robber, lis_length

rnd = random.Random(102)


def test_climb_stairs():
    assert climb_stairs(1) == 1 and climb_stairs(2) == 2 and climb_stairs(4) == 5 and climb_stairs(0) == 1
    assert climb_stairs(4, steps=(1, 3)) == 3
    assert climb_stairs(5, steps=(2,)) == 0
    assert climb_stairs(10, steps=(1, 2, 3)) == 274
    t0 = time.perf_counter()
    a, b = 1, 1
    for _ in range(99_999):
        a, b = b, (a + b) % MOD
    assert climb_stairs(100_000) == b, "по модулю 10**9 + 7"
    assert time.perf_counter() - t0 < 2


def test_house_robber():
    assert house_robber([1, 2, 3, 1]) == 4 and house_robber([2, 7, 9, 3, 1]) == 12
    assert house_robber([]) == 0 and house_robber([5]) == 5
    for _ in range(300):
        h = [rnd.randint(0, 20) for _ in range(rnd.randint(0, 10))]
        best = 0
        for mask in range(1 << len(h)):
            if mask & (mask >> 1) == 0:
                best = max(best, sum(h[i] for i in range(len(h)) if mask >> i & 1))
        assert house_robber(h) == best, f"{h}"
    assert house_robber(list(range(100_000))) > 0


def test_coin_change():
    assert coin_change([1, 2, 5], 11) == 3
    assert coin_change([1, 3, 4], 6) == 2, "жадный алгоритм здесь ошибается"
    assert coin_change([2], 3) == -1 and coin_change([7], 0) == 0
    for _ in range(200):
        coins = rnd.sample(range(1, 10), rnd.randint(1, 3))
        amt = rnd.randint(0, 25)

        @functools.cache
        def slow(s):
            if s == 0:
                return 0
            opts = [slow(s - c) + 1 for c in coins if c <= s and slow(s - c) >= 0]
            return min(opts) if opts else -1
        assert coin_change(coins, amt) == slow(amt), f"{coins}, {amt}"


def _lis_slow(a):
    best = [1] * len(a)
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i]:
                best[i] = max(best[i], best[j] + 1)
    return max(best, default=0)


def test_lis_length():
    assert lis_length([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert lis_length([0, 1, 0, 3, 2, 3]) == 4 and lis_length([7, 7, 7]) == 1 and lis_length([]) == 0
    for _ in range(300):
        a = [rnd.randint(0, 9) for _ in range(rnd.randint(0, 12))]
        assert lis_length(a) == _lis_slow(a), f"{a}"
    big = [rnd.randint(0, 10**9) for _ in range(100_000)]
    t0 = time.perf_counter()
    lis_length(big)
    assert time.perf_counter() - t0 < 1.5, "нужно O(n log n)"


def _ed_slow(a, b):
    @functools.cache
    def go(i, j):
        if i == len(a):
            return len(b) - j
        if j == len(b):
            return len(a) - i
        if a[i] == b[j]:
            return go(i + 1, j + 1)
        return 1 + min(go(i + 1, j), go(i, j + 1), go(i + 1, j + 1))
    return go(0, 0)


def test_edit_distance():
    assert edit_distance("horse", "ros") == 3
    assert edit_distance("intention", "execution") == 5
    assert edit_distance("", "abc") == 3 and edit_distance("abc", "") == 3 and edit_distance("", "") == 0
    for _ in range(300):
        a = "".join(rnd.choice("ab") for _ in range(rnd.randint(0, 7)))
        b = "".join(rnd.choice("abc") for _ in range(rnd.randint(0, 7)))
        assert edit_distance(a, b) == _ed_slow(a, b), f"{a!r}, {b!r}"
    a = "".join(rnd.choice("abcd") for _ in range(2000))
    b = "".join(rnd.choice("abcd") for _ in range(2000))
    t0 = time.perf_counter()
    edit_distance(a, b)
    assert time.perf_counter() - t0 < 6, "таблица O(n·m) без лишней работы"
