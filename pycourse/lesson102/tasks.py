# Урок 10.2. Динамическое программирование
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 102
from bisect import bisect_left  # noqa: F401 — для lis_length

MOD = 10**9 + 7


def climb_stairs(n: int, steps=(1, 2)) -> int:
    """Число способов подняться на n ступенек шагами из steps, по модулю MOD.

    >>> climb_stairs(4), climb_stairs(4, steps=(1, 3))
    (5, 3)
    """
    raise NotImplementedError


def house_robber(houses: list[int]) -> int:
    """Максимальная сумма без двух соседних домов.

    >>> house_robber([2, 7, 9, 3, 1])
    12
    """
    raise NotImplementedError


def coin_change(coins: list[int], amount: int) -> int:
    """Минимальное число монет на сумму amount или -1.

    >>> coin_change([1, 3, 4], 6), coin_change([2], 3)
    (2, -1)
    """
    raise NotImplementedError


def lis_length(a: list[int]) -> int:
    """Длина наибольшей строго возрастающей подпоследовательности, O(n log n).

    >>> lis_length([10, 9, 2, 5, 3, 7, 101, 18])
    4
    """
    raise NotImplementedError


def edit_distance(a: str, b: str) -> int:
    """★ Расстояние Левенштейна: вставки, удаления, замены.

    >>> edit_distance("horse", "ros"), edit_distance("intention", "execution")
    (3, 5)
    """
    raise NotImplementedError
