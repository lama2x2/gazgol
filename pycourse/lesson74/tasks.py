# Урок 7.4. Бинарный поиск: по массиву и по ответу
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 74
# Модуль bisect в этом уроке не используй — смысл в том, чтобы написать поиск самому.


def lower_bound(a: list[int], x: int) -> int:
    """Первая позиция i, где a[i] >= x; если таких нет — len(a).

    >>> lower_bound([1, 2, 2, 4], 2), lower_bound([1, 2, 2, 4], 3), lower_bound([1, 2], 9)
    (1, 3, 2)
    """
    raise NotImplementedError


def search_range(a: list[int], x: int) -> tuple[int, int]:
    """Первая и последняя позиции x в отсортированном a или (-1, -1). O(log n).

    >>> search_range([5, 7, 7, 8, 8, 10], 8), search_range([5, 7], 6)
    ((3, 4), (-1, -1))
    """
    raise NotImplementedError


def search_rotated(a: list[int], x: int) -> int:
    """Индекс x в повёрнутом отсортированном массиве без повторов или -1. O(log n).

    >>> search_rotated([4, 5, 6, 7, 0, 1, 2], 0), search_rotated([4, 5, 6, 7, 0, 1, 2], 3)
    (4, -1)
    """
    raise NotImplementedError


def min_ship_capacity(weights: list[int], days: int) -> int:
    """Минимальная грузоподъёмность, чтобы перевезти грузы по порядку за days дней.

    >>> min_ship_capacity([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5)
    15
    """
    raise NotImplementedError


def find_valley(a) -> int:
    """★ Индекс любого локального минимума за O(log n). Соседние элементы различны,
    за границами массива — +∞. a поддерживает len() и a[i].

    >>> find_valley([5, 3, 4]) , find_valley([1, 2, 3])
    (1, 0)
    """
    raise NotImplementedError
