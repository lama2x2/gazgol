# Урок 7.3. Скользящее окно
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 73
from collections import Counter  # noqa: F401


def max_sum_window(a: list[int], k: int) -> int | None:
    """Максимальная сумма окна длины k; k <= 0 или k > len(a) — None.

    >>> max_sum_window([1, 4, 2, 10, 2, 3, 1, 0, 20], 4)
    24
    """
    raise NotImplementedError


def longest_unique_substring(s: str) -> int:
    """Длина самой длинной подстроки без повторяющихся символов.

    >>> longest_unique_substring("abcabcbb"), longest_unique_substring("abba")
    (3, 2)
    """
    raise NotImplementedError


def max_sum_two_distinct(a: list[int]) -> int:
    """Максимальная сумма подотрезка, где не больше двух разных значений (числа >= 0).

    >>> max_sum_two_distinct([1, 2, 1, 3, 3, 3, 1])
    11
    """
    raise NotImplementedError


def count_unique_subarrays(a: list[int]) -> int:
    """Сколько непрерывных подотрезков, где все значения различны.

    >>> count_unique_subarrays([1, 2, 1, 3])
    8
    """
    raise NotImplementedError


def min_window(s: str, t: str) -> str:
    """★ Самая короткая (при равенстве — самая левая) подстрока s, содержащая все символы t с кратностью.

    >>> min_window("ADOBECODEBANC", "ABC"), min_window("a", "aa")
    ('BANC', '')
    """
    raise NotImplementedError
