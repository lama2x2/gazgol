# Урок 9.2. Дейкстра, система непересекающихся множеств, остовное дерево
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 92
import heapq  # noqa: F401
from collections import defaultdict  # noqa: F401


def dijkstra(n: int, edges: list[tuple[int, int, int]], src: int) -> list[int]:
    """Расстояния от src до вершин 0..n-1 по ориентированным рёбрам (u, v, w >= 0); недостижимые — -1.

    >>> dijkstra(3, [(0, 1, 4), (0, 2, 1), (2, 1, 2)], 0)
    [0, 3, 1]
    """
    raise NotImplementedError


def network_delay(times: list[tuple[int, int, int]], n: int, k: int) -> int:
    """Узлы 1..n, (u, v, w) — сигнал идёт из u в v за w. За сколько дойдёт из k до всех? Иначе -1.

    >>> network_delay([(2, 1, 1), (2, 3, 1), (3, 4, 1)], 4, 2)
    2
    """
    raise NotImplementedError


class DSU:
    """find(x), union(a, b) → bool (объединились ли), components — число групп."""

    def __init__(self, n: int):
        raise NotImplementedError

    def find(self, x: int) -> int:
        raise NotImplementedError

    def union(self, a: int, b: int) -> bool:
        raise NotImplementedError

    @property
    def components(self) -> int:
        raise NotImplementedError


def is_tree(n: int, edges: list[tuple[int, int]]) -> bool:
    """Неориентированный граф на вершинах 0..n-1 — дерево?

    >>> is_tree(4, [(0, 1), (1, 2), (1, 3)]), is_tree(4, [(0, 1), (1, 2), (2, 0)])
    (True, False)
    """
    raise NotImplementedError


def mst_cost(n: int, edges: list[tuple[int, int, int]]) -> int:
    """★ Вес минимального остовного дерева (неориентированные рёбра (u, v, w)); несвязный граф — -1.

    >>> mst_cost(4, [(0, 1, 1), (1, 2, 2), (0, 2, 3), (2, 3, 1)])
    4
    """
    raise NotImplementedError
