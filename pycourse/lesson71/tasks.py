# Урок 7.1. Хеш-таблицы и префиксные суммы
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 71
from collections import defaultdict  # noqa: F401


def two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    """(i, j), i < j, nums[i] + nums[j] == target; наименьший j, при нём наименьший i; нет — None.

    >>> two_sum([2, 7, 11, 15], 9), two_sum([3, 3], 6), two_sum([1, 2], 7)
    ((0, 1), (0, 1), None)
    """
    raise NotImplementedError


def subarray_sum_k(nums: list[int], k: int) -> int:
    """Сколько непрерывных подотрезков имеют сумму k.

    >>> subarray_sum_k([1, 1, 1], 2), subarray_sum_k([1, -1, 0], 0)
    (2, 3)
    """
    raise NotImplementedError


def longest_consecutive(nums: list[int]) -> int:
    """Длина самой длинной последовательности подряд идущих целых (в любом порядке), O(n).

    >>> longest_consecutive([100, 4, 200, 1, 3, 2])
    4
    """
    raise NotImplementedError


class RangeSum:
    """RangeSum(nums).query(l, r) — сумма nums[l..r] включительно за O(1).

    >>> RangeSum([1, 2, 3, 4]).query(1, 2)
    5
    """

    def __init__(self, nums: list[int]):
        raise NotImplementedError

    def query(self, l: int, r: int) -> int:
        raise NotImplementedError


def longest_balanced(bits: list[int]) -> int:
    """★ Длина самого длинного подотрезка, где нулей и единиц поровну.

    >>> longest_balanced([0, 1, 0]), longest_balanced([0, 0, 1, 0, 0, 0, 1, 1])
    (2, 6)
    """
    raise NotImplementedError
