# Урок 3.2. Итераторы и генераторы
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 32
import heapq  # noqa: F401 — для merge_sorted (heappush / heappop, но не heapq.merge)
from collections import Counter  # noqa: F401
from itertools import islice  # noqa: F401


class MyRange:
    """Свой range(start, stop, step=1): многоразовый, с len() и быстрым `in`.

    Классы подробно — в модуле 4; здесь нужны только __init__, __iter__, __len__, __contains__.

    >>> r = MyRange(1, 10, 3); list(r), list(r), len(r), 7 in r, 8 in r
    ([1, 4, 7], [1, 4, 7], 3, True, False)
    """

    def __init__(self, start, stop, step=1):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __contains__(self, x):
        raise NotImplementedError


def chunked(iterable, n):
    """Лениво отдавать списки по n элементов; последний может быть короче.

    >>> list(chunked(range(7), 3))
    [[0, 1, 2], [3, 4, 5], [6]]
    """
    raise NotImplementedError


def flatten(nested):
    """Генератор: разложить вложенные list/tuple любой глубины. Строки не раскладывать.

    >>> list(flatten([1, [2, (3, [4])], "ab"]))
    [1, 2, 3, 4, 'ab']
    """
    raise NotImplementedError


def top_urls(lines, k):
    """Топ-k URL по количеству запросов: [(url, count), ...] по убыванию, при равенстве — по url.

    Строка лога: "2026-01-01T10:00:00 GET /api/users 200 12ms". Строки короче трёх полей пропускать.
    """
    raise NotImplementedError


def merge_sorted(*iterables):
    """★ Лениво слить отсортированные итераторы в один отсортированный поток.

    >>> list(merge_sorted([1, 4, 9], [2, 3], [], [5]))
    [1, 2, 3, 4, 5, 9]
    """
    raise NotImplementedError
