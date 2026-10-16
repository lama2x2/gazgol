# Проверяющая система урока 8.2 — не меняй этот файл.
import inspect
import random

import tasks
from tasks import ListNode, from_list, has_cycle, is_palindrome_list, merge_two, remove_nth_from_end, reverse_list, to_list

rnd = random.Random(82)


def _nodes(head):
    out = []
    while head:
        out.append(head)
        head = head.next
    return out


def test_reverse_list():
    assert reverse_list(None) is None
    one = ListNode(1)
    assert reverse_list(one) is one and one.next is None
    head = from_list([1, 2, 3, 4])
    nodes = _nodes(head)
    new = reverse_list(head)
    assert to_list(new) == [4, 3, 2, 1]
    assert _nodes(new) == nodes[::-1], "переставляй ссылки, не создавай новые узлы"
    big = from_list(range(100_000))
    assert to_list(reverse_list(big))[:3] == [99_999, 99_998, 99_997], "длинный список — без рекурсии"


def test_has_cycle():
    assert "set(" not in inspect.getsource(tasks.has_cycle) and "{" not in inspect.getsource(tasks.has_cycle), \
        "решение за O(1) памяти — без множества посещённых"
    assert has_cycle(None) is False
    assert has_cycle(from_list([1, 2, 3])) is False
    for n in range(1, 30):
        head = from_list([7] * n)
        nodes = _nodes(head)
        k = rnd.randrange(n)
        nodes[-1].next = nodes[k]
        assert has_cycle(head) is True, f"цикл длины {n - k} в списке из {n} узлов"
    self_loop = ListNode(1)
    self_loop.next = self_loop
    assert has_cycle(self_loop)


def test_merge_two():
    assert merge_two(None, None) is None
    a, b = from_list([1, 2, 4]), from_list([1, 3, 4])
    na, nb = _nodes(a), _nodes(b)
    res = _nodes(merge_two(a, b))
    assert [x.val for x in res] == [1, 1, 2, 3, 4, 4]
    assert res[0] is na[0] and res[1] is nb[0], "при равенстве — сначала узел из первого списка"
    assert res[4] is na[2] and res[5] is nb[2]
    assert set(map(id, res)) == set(map(id, na + nb)), "переиспользуй узлы"
    for _ in range(200):
        x = sorted(rnd.randint(0, 9) for _ in range(rnd.randint(0, 6)))
        y = sorted(rnd.randint(0, 9) for _ in range(rnd.randint(0, 6)))
        assert to_list(merge_two(from_list(x), from_list(y))) == sorted(x + y)


def test_remove_nth_from_end():
    assert to_list(remove_nth_from_end(from_list([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5]
    assert remove_nth_from_end(from_list([1]), 1) is None
    assert to_list(remove_nth_from_end(from_list([1, 2]), 2)) == [2], "удаление головы"
    assert to_list(remove_nth_from_end(from_list([1, 2]), 1)) == [1]
    for _ in range(200):
        a = [rnd.randint(0, 9) for _ in range(rnd.randint(1, 10))]
        n = rnd.randint(1, len(a))
        want = a[:len(a) - n] + a[len(a) - n + 1:]
        assert to_list(remove_nth_from_end(from_list(a), n)) == want, f"{a}, n={n}"


def test_is_palindrome_list():
    src = inspect.getsource(tasks.is_palindrome_list)
    assert "to_list" not in src and "append" not in src and "[]" not in src, "O(1) памяти: без копирования в массив"
    for vals in ([], [1], [1, 2], [1, 2, 1], [1, 2, 2, 1], [1, 2, 3, 1], [5, 5], [1, 0, 0]):
        head = from_list(vals)
        nodes = _nodes(head)
        assert is_palindrome_list(head) == (vals == vals[::-1]), f"{vals}"
        assert _nodes(head) == nodes and to_list(head) == vals, "список нужно вернуть в исходное состояние"
    for _ in range(200):
        a = [rnd.randint(0, 2) for _ in range(rnd.randint(0, 9))]
        head = from_list(a)
        assert is_palindrome_list(head) == (a == a[::-1]) and to_list(head) == a
