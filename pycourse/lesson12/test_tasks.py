# Проверяющая система урока 1.2 — не меняй этот файл.
import random

import pytest

from tasks import clock_angle, compress_ranges, is_monotonic, longest_non_decreasing, max_dist_to_closest


@pytest.mark.parametrize("nums, want", [
    ([1, 4, 5, 2, 3, 9, 8, 11, 0], "0-5,8-9,11"),
    ([], ""),
    ([7], "7"),
    ([1, 2, 3], "1-3"),
    ([5, 3, 1], "1,3,5"),
    ([2, 2, 3, 3], "2-3"),
    ([-3, -2, -1, 1], "-3--1,1"),
    ([10, 1, 2, 8, 9, 20], "1-2,8-10,20"),
])
def test_compress_ranges(nums, want):
    orig = list(nums)
    assert compress_ranges(nums) == want, f"compress_ranges({orig})"
    assert nums == orig, "входной список нельзя менять"


def _slow_lnd(a):
    best = 0
    for i in range(len(a)):
        j = i
        while j + 1 < len(a) and a[j + 1] >= a[j]:
            j += 1
        best = max(best, j - i + 1)
    return best


@pytest.mark.parametrize("nums, want", [
    ([1, 2, 2, 1, 5, 6, 7, 0], 4),
    ([], 0),
    ([5], 1),
    ([2, 2, 2], 3),
    ([5, 4, 3], 1),
    ([3, 1, 2, 3, 4], 4),
])
def test_longest_non_decreasing(nums, want):
    assert longest_non_decreasing(nums) == want, f"longest_non_decreasing({nums})"


def test_longest_non_decreasing__random():
    rnd = random.Random(12)
    for _ in range(300):
        a = [rnd.randint(-3, 3) for _ in range(rnd.randint(0, 12))]
        assert longest_non_decreasing(a) == _slow_lnd(a), f"longest_non_decreasing({a})"


@pytest.mark.parametrize("h, m, want", [
    (3, 0, 90), (3, 30, 75), (12, 0, 0), (0, 0, 0), (9, 0, 90),
    (6, 0, 180), (15, 0, 90), (23, 59, 5.5), (12, 30, 165),
])
def test_clock_angle(h, m, want):
    assert clock_angle(h, m) == pytest.approx(want), f"clock_angle({h}, {m})"


@pytest.mark.parametrize("nums, want", [
    ([1, 2, 2, 3], True), ([3, 3, 1], True), ([1, 3, 2], False),
    ([], True), ([4], True), ([2, 2, 2], True), ([1, 1, 2, 1], False), ([-1, -5, -10], True),
])
def test_is_monotonic(nums, want):
    assert is_monotonic(nums) is want, f"is_monotonic({nums})"


def _slow_seat(seats):
    best = 0
    people = [i for i, s in enumerate(seats) if s]
    for i, s in enumerate(seats):
        if not s:
            best = max(best, min(abs(i - p) for p in people))
    return best


@pytest.mark.parametrize("seats, want", [
    ([1, 0, 0, 0, 1, 0, 1], 2),
    ([1, 0, 0, 0], 3),
    ([0, 0, 0, 1], 3),
    ([0, 1], 1),
    ([1, 0, 1], 1),
    ([1, 0, 0, 1], 1),
    ([0, 0, 1, 0, 0, 0, 0, 1, 0], 2),
])
def test_max_dist_to_closest(seats, want):
    assert max_dist_to_closest(seats) == want, f"max_dist_to_closest({seats})"


def test_max_dist_to_closest__random():
    rnd = random.Random(849)
    for _ in range(300):
        n = rnd.randint(2, 14)
        s = [rnd.randint(0, 1) for _ in range(n)]
        s[rnd.randrange(n)] = 1
        z = rnd.randrange(n)
        if s[z]:
            s[z] = 0
            if not any(s):
                s[(z + 1) % n] = 1
        assert max_dist_to_closest(s) == _slow_seat(s), f"max_dist_to_closest({s})"
