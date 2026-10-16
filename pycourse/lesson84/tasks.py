# Урок 8.4. Кучи и интервалы
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 84
import heapq  # noqa: F401


def kth_largest(a: list[int], k: int) -> int:
    """k-й по величине элемент (с учётом повторов), кучей размера k.

    >>> kth_largest([3, 2, 1, 5, 6, 4], 2), kth_largest([3, 3, 1], 2)
    (5, 3)
    """
    raise NotImplementedError


def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """Слить пересекающиеся (и касающиеся) интервалы; результат отсортирован по началу.

    >>> merge_intervals([[1, 3], [8, 10], [2, 6], [15, 18]])
    [[1, 6], [8, 10], [15, 18]]
    """
    raise NotImplementedError


def min_meeting_rooms(meetings: list[tuple[int, int]]) -> int:
    """Минимум переговорок; встреча [start, end) освобождает комнату в момент end.

    >>> min_meeting_rooms([(0, 30), (5, 10), (15, 20)]), min_meeting_rooms([(1, 3), (3, 5)])
    (2, 1)
    """
    raise NotImplementedError


def merge_k_sorted(lists: list[list[int]]) -> list[int]:
    """Слить k отсортированных списков за O(N log k).

    >>> merge_k_sorted([[1, 4, 5], [1, 3, 4], [2, 6]])
    [1, 1, 2, 3, 4, 4, 5, 6]
    """
    raise NotImplementedError


class MedianFinder:
    """★ add(x) за O(log n), median() за O(1); пустой поток — ValueError."""

    def __init__(self):
        raise NotImplementedError

    def add(self, x: int) -> None:
        raise NotImplementedError

    def median(self) -> float:
        raise NotImplementedError
