# Урок 9.1. BFS, DFS и топологическая сортировка
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 91
import heapq  # noqa: F401
from collections import defaultdict, deque  # noqa: F401


def num_islands(grid: list[list[str]]) -> int:
    """Сколько островов из "1" (соседство по 4 сторонам).

    >>> num_islands([list("1100"), list("0100"), list("0011")])
    2
    """
    raise NotImplementedError


def shortest_path_grid(grid: list[list[int]]) -> int:
    """Число шагов от (0, 0) до (R-1, C-1) по клеткам 0; стена — 1; нет пути — -1.

    >>> shortest_path_grid([[0, 0, 0], [1, 1, 0], [0, 0, 0]])
    4
    """
    raise NotImplementedError


def can_finish(n: int, prereq: list[tuple[int, int]]) -> bool:
    """Курсы 0..n-1; (a, b) — «a требует b». Можно ли пройти все?

    >>> can_finish(2, [(1, 0)]), can_finish(2, [(1, 0), (0, 1)])
    (True, False)
    """
    raise NotImplementedError


def topo_order(n: int, deps: list[tuple[int, int]]) -> list[int] | None:
    """(a, b) — «a выполняется после b». Порядок 0..n-1, среди готовых — наименьшая; цикл — None.

    >>> topo_order(4, [(1, 0), (2, 0), (3, 1), (3, 2)])
    [0, 1, 2, 3]
    """
    raise NotImplementedError


def word_ladder(begin: str, end: str, words: list[str]) -> int:
    """★ Длина кратчайшей цепочки слов (в словах) от begin до end; соседи отличаются одной буквой.

    >>> word_ladder("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"])
    5
    """
    raise NotImplementedError
