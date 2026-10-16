# Проверяющая система урока 7.1 — не меняй этот файл.
import random
import time

from tasks import RangeSum, longest_balanced, longest_consecutive, subarray_sum_k, two_sum

rnd = random.Random(71)


def _two_sum_slow(nums, t):
    for j in range(len(nums)):
        for i in range(j):
            if nums[i] + nums[j] == t:
                return (i, j)
    return None


def test_two_sum():
    assert two_sum([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum([3, 2, 4], 6) == (1, 2)
    assert two_sum([3, 3], 6) == (0, 1)
    assert two_sum([5], 10) is None, "число не может составить пару само с собой"
    assert two_sum([], 1) is None
    for _ in range(400):
        a = [rnd.randint(-6, 6) for _ in range(rnd.randint(0, 10))]
        t = rnd.randint(-8, 8)
        got = two_sum(a, t)
        assert (tuple(got) if got is not None else None) == _two_sum_slow(a, t), f"two_sum({a}, {t})"
    big = list(range(200_000))
    t0 = time.perf_counter()
    assert two_sum(big, 399_997) == (199_998, 199_999)
    assert time.perf_counter() - t0 < 1, "нужно O(n)"


def _sub_slow(a, k):
    return sum(1 for i in range(len(a)) for j in range(i, len(a)) if sum(a[i:j + 1]) == k)


def test_subarray_sum_k():
    assert subarray_sum_k([1, 1, 1], 2) == 2
    assert subarray_sum_k([1, 2, 3], 3) == 2
    assert subarray_sum_k([3], 3) == 1
    assert subarray_sum_k([], 0) == 0
    for _ in range(300):
        a = [rnd.randint(-3, 3) for _ in range(rnd.randint(0, 12))]
        k = rnd.randint(-3, 3)
        assert subarray_sum_k(a, k) == _sub_slow(a, k), f"subarray_sum_k({a}, {k})"
    t0 = time.perf_counter()
    assert subarray_sum_k([0] * 3000, 0) == 3000 * 3001 // 2
    assert time.perf_counter() - t0 < 1, "нужно O(n)"


def test_longest_consecutive():
    assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4
    assert longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9
    assert longest_consecutive([]) == 0
    assert longest_consecutive([5, 5, 5]) == 1
    assert longest_consecutive([-2, -1, 1]) == 2
    big = list(range(200_000, 0, -1))
    t0 = time.perf_counter()
    assert longest_consecutive(big) == 200_000
    assert time.perf_counter() - t0 < 1, "нужно O(n): начинай счёт только с начала цепочки"


def test_range_sum():
    rs = RangeSum([1, 2, 3, 4])
    assert rs.query(0, 3) == 10 and rs.query(1, 2) == 5 and rs.query(3, 3) == 4
    a = [rnd.randint(-100, 100) for _ in range(100_000)]
    rs = RangeSum(a)
    qs = [sorted((rnd.randrange(len(a)), rnd.randrange(len(a)))) for _ in range(200_000)]
    t0 = time.perf_counter()
    got = [rs.query(l, r) for l, r in qs]
    assert time.perf_counter() - t0 < 1.5, "запрос должен работать за O(1)"
    for (l, r), g in list(zip(qs, got))[:200]:
        assert g == sum(a[l:r + 1])


def _bal_slow(b):
    best = 0
    for i in range(len(b)):
        z = o = 0
        for j in range(i, len(b)):
            z += b[j] == 0
            o += b[j] == 1
            if z == o:
                best = max(best, j - i + 1)
    return best


def test_longest_balanced():
    assert longest_balanced([0, 1, 0]) == 2
    assert longest_balanced([0, 0, 1, 0, 0, 0, 1, 1]) == 6
    assert longest_balanced([1, 1, 1]) == 0
    assert longest_balanced([]) == 0
    for _ in range(300):
        b = [rnd.randint(0, 1) for _ in range(rnd.randint(0, 14))]
        assert longest_balanced(b) == _bal_slow(b), f"longest_balanced({b})"
