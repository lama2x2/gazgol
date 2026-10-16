# Проверяющая система урока 2.2 — не меняй этот файл.
import random
import time

from tasks import count_distinct_windows, first_unique, group_anagrams, top_k_frequent


def test_group_anagrams():
    assert group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]) == [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]
    assert group_anagrams([]) == []
    assert group_anagrams(["", ""]) == [["", ""]]
    assert group_anagrams(["ab", "ba", "abb", "bab", "a"]) == [["ab", "ba"], ["abb", "bab"], ["a"]]
    assert group_anagrams(["aab", "abb"]) == [["aab"], ["abb"]], "одинаковый набор букв, но разные количества — не анаграммы"


def test_top_k_frequent():
    assert top_k_frequent(["b", "a", "c", "b", "a", "d"], 3) == ["a", "b", "c"]
    assert top_k_frequent(["i", "love", "py", "i", "love", "code"], 2) == ["i", "love"]
    assert top_k_frequent(["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], 4) == ["the", "is", "sunny", "day"]
    assert top_k_frequent(["z", "y", "x"], 2) == ["x", "y"], "при равной частоте — по алфавиту"
    assert top_k_frequent(["a"], 5) == ["a"]


def test_first_unique():
    assert first_unique("leetcode") == 0
    assert first_unique("loveleetcode") == 2
    assert first_unique("aabb") == -1
    assert first_unique("") == -1
    assert first_unique("z") == 0
    s = "ab" * 100_000 + "c"
    t = time.perf_counter()
    assert first_unique(s) == len(s) - 1
    assert time.perf_counter() - t < 1.0, "слишком медленно: нужен один подсчёт, а не s.count в цикле"


def _slow(nums, k):
    return [len(set(nums[i:i + k])) for i in range(len(nums) - k + 1)] if 0 < k <= len(nums) else []


def test_count_distinct_windows():
    assert count_distinct_windows([1, 2, 1, 3, 4, 2, 3], 4) == [3, 4, 4, 3]
    assert count_distinct_windows([1, 1, 1], 2) == [1, 1]
    assert count_distinct_windows([1, 2], 3) == []
    assert count_distinct_windows([5], 1) == [1]
    rnd = random.Random(22)
    for _ in range(200):
        a = [rnd.randint(0, 5) for _ in range(rnd.randint(0, 15))]
        k = rnd.randint(1, 6)
        assert count_distinct_windows(a, k) == _slow(a, k), f"count_distinct_windows({a}, {k})"
    big = [i % 1000 for i in range(200_000)]
    t = time.perf_counter()
    assert count_distinct_windows(big, 5000)[:3] == [1000, 1000, 1000]
    assert time.perf_counter() - t < 1.5, "слишком медленно: обновляй счётчик окна, а не пересчитывай set на каждом шаге"
