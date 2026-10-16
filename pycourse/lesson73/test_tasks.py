# Проверяющая система урока 7.3 — не меняй этот файл.
import random
import time
from collections import Counter

from tasks import count_unique_subarrays, longest_unique_substring, max_sum_two_distinct, max_sum_window, min_window

rnd = random.Random(73)


def test_max_sum_window():
    assert max_sum_window([1, 4, 2, 10, 2, 3, 1, 0, 20], 4) == 24
    assert max_sum_window([-1, -2, -3], 2) == -3
    assert max_sum_window([5], 1) == 5
    assert max_sum_window([1, 2], 3) is None and max_sum_window([1, 2], 0) is None
    for _ in range(300):
        a = [rnd.randint(-9, 9) for _ in range(rnd.randint(1, 12))]
        k = rnd.randint(1, len(a))
        assert max_sum_window(a, k) == max(sum(a[i:i + k]) for i in range(len(a) - k + 1)), f"{a}, {k}"
    big = list(range(200_000))
    t0 = time.perf_counter()
    assert max_sum_window(big, 50_000) == sum(range(150_000, 200_000))
    assert time.perf_counter() - t0 < 1, "нужно O(n): не пересчитывай сумму окна"


def _lus_slow(s):
    return max([j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1) if len(set(s[i:j])) == j - i], default=0)


def test_longest_unique_substring():
    assert longest_unique_substring("abcabcbb") == 3
    assert longest_unique_substring("bbbbb") == 1
    assert longest_unique_substring("pwwkew") == 3
    assert longest_unique_substring("abba") == 2
    assert longest_unique_substring("") == 0
    for _ in range(300):
        s = "".join(rnd.choice("abcd") for _ in range(rnd.randint(0, 12)))
        assert longest_unique_substring(s) == _lus_slow(s), repr(s)


def _two_slow(a):
    best = 0
    for i in range(len(a)):
        for j in range(i, len(a)):
            if len(set(a[i:j + 1])) <= 2:
                best = max(best, sum(a[i:j + 1]))
    return best


def test_max_sum_two_distinct():
    assert max_sum_two_distinct([1, 2, 1, 3, 3, 3, 1]) == 11
    assert max_sum_two_distinct([]) == 0
    assert max_sum_two_distinct([7]) == 7
    assert max_sum_two_distinct([5, 5, 5]) == 15
    for _ in range(300):
        a = [rnd.randint(0, 5) for _ in range(rnd.randint(0, 12))]
        assert max_sum_two_distinct(a) == _two_slow(a), f"{a}"
    big = [rnd.randint(0, 3) for _ in range(200_000)]
    t0 = time.perf_counter()
    max_sum_two_distinct(big)
    assert time.perf_counter() - t0 < 1.5, "нужно O(n)"


def _cus_slow(a):
    return sum(1 for i in range(len(a)) for j in range(i, len(a)) if len(set(a[i:j + 1])) == j - i + 1)


def test_count_unique_subarrays():
    assert count_unique_subarrays([1, 2, 1, 3]) == 8
    assert count_unique_subarrays([]) == 0
    assert count_unique_subarrays([4, 4, 4]) == 3
    for _ in range(300):
        a = [rnd.randint(0, 4) for _ in range(rnd.randint(0, 12))]
        assert count_unique_subarrays(a) == _cus_slow(a), f"{a}"
    t0 = time.perf_counter()
    assert count_unique_subarrays(list(range(100_000))) == 100_000 * 100_001 // 2
    assert time.perf_counter() - t0 < 1, "нужно O(n)"


def _mw_slow(s, t):
    need = Counter(t)
    best = ""
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if not need - Counter(s[i:j]):
                if not best or j - i < len(best):
                    best = s[i:j]
                break
    return best


def test_min_window():
    assert min_window("ADOBECODEBANC", "ABC") == "BANC"
    assert min_window("a", "a") == "a"
    assert min_window("a", "aa") == ""
    assert min_window("aa", "aa") == "aa"
    assert min_window("abc", "") in ("", "a")
    for _ in range(300):
        s = "".join(rnd.choice("abc") for _ in range(rnd.randint(0, 12)))
        t = "".join(rnd.choice("abc") for _ in range(rnd.randint(1, 3)))
        assert min_window(s, t) == _mw_slow(s, t), f"min_window({s!r}, {t!r})"
    s = "".join(rnd.choice("abcdefgh") for _ in range(200_000)) + "xyz"
    t0 = time.perf_counter()
    assert min_window(s, "zyx") == "xyz"
    assert time.perf_counter() - t0 < 2, "нужно O(n)"
