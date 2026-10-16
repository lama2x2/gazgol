# Урок 8.3. Деревья: обходы, BST, LCA
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 83
from collections import deque  # noqa: F401


class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right

    def __repr__(self):
        return f"TreeNode({self.val})"


def max_depth(root: TreeNode | None) -> int:
    """Высота дерева (число уровней), без рекурсии."""
    raise NotImplementedError


def level_order(root: TreeNode | None) -> list[list]:
    """Значения по уровням слева направо.

    >>> level_order(TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7))))
    [[3], [9, 20], [15, 7]]
    """
    raise NotImplementedError


def is_valid_bst(root: TreeNode | None) -> bool:
    """BST со строгими неравенствами? Без рекурсии."""
    raise NotImplementedError


def lowest_common_ancestor(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    """Наименьший общий предок узлов p и q (оба есть в дереве; узел — предок самого себя)."""
    raise NotImplementedError


def serialize(root: TreeNode | None) -> str:
    """★ Дерево → строка."""
    raise NotImplementedError


def deserialize(data: str) -> TreeNode | None:
    """★ Строка → дерево; deserialize(serialize(t)) воспроизводит t."""
    raise NotImplementedError
