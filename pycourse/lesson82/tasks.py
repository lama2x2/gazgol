# Урок 8.2. Связные списки
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 82


class ListNode:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

    def __repr__(self):
        return f"ListNode({self.val})"


def from_list(values) -> ListNode | None:
    """Построить список из значений (готовый помощник)."""
    head = None
    for v in reversed(list(values)):
        head = ListNode(v, head)
    return head


def to_list(head: ListNode | None, limit: int = 10**7) -> list:
    """Значения списка в Python-список (готовый помощник)."""
    out = []
    while head and len(out) < limit:
        out.append(head.val)
        head = head.next
    return out


def reverse_list(head: ListNode | None) -> ListNode | None:
    """Развернуть список на месте, вернуть новую голову.

    >>> to_list(reverse_list(from_list([1, 2, 3])))
    [3, 2, 1]
    """
    raise NotImplementedError


def has_cycle(head: ListNode | None) -> bool:
    """Есть ли цикл. O(1) памяти."""
    raise NotImplementedError


def merge_two(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    """Слить два отсортированных списка, переиспользуя узлы; при равенстве — сначала из a.

    >>> to_list(merge_two(from_list([1, 2, 4]), from_list([1, 3, 4])))
    [1, 1, 2, 3, 4, 4]
    """
    raise NotImplementedError


def remove_nth_from_end(head: ListNode | None, n: int) -> ListNode | None:
    """Удалить n-й с конца узел (1 — последний), вернуть голову. 1 <= n <= длины.

    >>> to_list(remove_nth_from_end(from_list([1, 2, 3, 4, 5]), 2))
    [1, 2, 3, 5]
    """
    raise NotImplementedError


def is_palindrome_list(head: ListNode | None) -> bool:
    """★ Палиндром? O(1) памяти; после проверки список должен остаться прежним."""
    raise NotImplementedError
