# Урок 10.3. Жадные алгоритмы и битовые трюки
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 103


def is_power_of_two(x: int) -> bool:
    """Степень двойки? O(1), без циклов и math.

    >>> is_power_of_two(16), is_power_of_two(0), is_power_of_two(-8)
    (True, False, False)
    """
    raise NotImplementedError


def single_number(nums: list[int]) -> int:
    """Все числа по два раза, одно — один раз. O(n) времени, O(1) памяти.

    >>> single_number([4, 1, 2, 1, 2])
    4
    """
    raise NotImplementedError


def count_bits(n: int) -> list[int]:
    """[число единичных битов i для i в 0..n] за O(n).

    >>> count_bits(5)
    [0, 1, 1, 2, 1, 2]
    """
    raise NotImplementedError


def max_profit(prices: list[int]) -> int:
    """Лучшая прибыль от одной покупки и последующей продажи (или 0).

    >>> max_profit([7, 1, 5, 3, 6, 4]), max_profit([7, 6, 4, 3, 1])
    (5, 0)
    """
    raise NotImplementedError


def can_jump(a: list[int]) -> bool:
    """Из i можно прыгнуть на 1..a[i] вперёд. Дойдём от 0 до последнего индекса?

    >>> can_jump([2, 3, 1, 1, 4]), can_jump([3, 2, 1, 0, 4])
    (True, False)
    """
    raise NotImplementedError


def erase_overlap(intervals: list[list[int]]) -> int:
    """★ Минимум интервалов удалить, чтобы остальные не пересекались (касание — можно).

    >>> erase_overlap([[1, 2], [2, 3], [3, 4], [1, 3]])
    1
    """
    raise NotImplementedError
