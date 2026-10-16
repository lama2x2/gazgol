# Урок 5.1. Память, сборка мусора и GIL
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 51
import tracemalloc  # noqa: F401
import weakref  # noqa: F401


class TreeNode:
    """Узел дерева: сильные ссылки на детей, слабая — на родителя.

    >>> root = TreeNode("root"); kid = TreeNode("kid"); root.add_child(kid); kid.parent is root
    True
    """

    def __init__(self, name):
        raise NotImplementedError

    def add_child(self, child: "TreeNode") -> None:
        raise NotImplementedError

    @property
    def parent(self):
        raise NotImplementedError


class WeakCache:
    """Кэш, не удерживающий объекты: get(key, factory) → объект; misses — число вызовов factory."""

    def __init__(self):
        raise NotImplementedError

    def get(self, key, factory):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError


def top_allocations(func, n=3):
    """Вызвать func() под tracemalloc и вернуть n строк-лидеров: [(номер_строки, байт), ...] по убыванию."""
    raise NotImplementedError


class Point3D:
    """★ Неизменяемая точка со __slots__: Point3D(1, 2, 3); p.x = 5 → AttributeError.

    ==, hash, repr → Point3D(1, 2, 3)
    """
