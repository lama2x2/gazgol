# Урок 2.2. Коллекции изнутри: list, dict, set, collections
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 22
from collections import Counter, defaultdict, deque  # noqa: F401 — пригодятся


def group_anagrams(words: list[str]) -> list[list[str]]:
    """Сгруппировать анаграммы. Группы — в порядке первого появления, слова в группе — в порядке входа.

    >>> group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
    """
    raise NotImplementedError


def top_k_frequent(words: list[str], k: int) -> list[str]:
    """k самых частых слов: по убыванию частоты, при равенстве — по алфавиту.

    >>> top_k_frequent(["b", "a", "c", "b", "a", "d"], 3)
    ['a', 'b', 'c']
    """
    raise NotImplementedError


def first_unique(s: str) -> int:
    """Индекс первого символа, который встречается ровно один раз, или -1.

    >>> first_unique("leetcode"), first_unique("aabb")
    (0, -1)
    """
    raise NotImplementedError


def count_distinct_windows(nums: list[int], k: int) -> list[int]:
    """Сколько разных чисел в каждом окне длины k.

    >>> count_distinct_windows([1, 2, 1, 3, 4, 2, 3], 4)
    [3, 4, 4, 3]
    """
    raise NotImplementedError
