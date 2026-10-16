# Проверяющая система урока 8.3 — не меняй этот файл.
import random

from tasks import TreeNode, deserialize, is_valid_bst, level_order, lowest_common_ancestor, max_depth, serialize

rnd = random.Random(83)


def rand_tree(n, lo=-20, hi=20):
    if n == 0:
        return None
    k = rnd.randrange(n)
    return TreeNode(rnd.randint(lo, hi), rand_tree(k, lo, hi), rand_tree(n - 1 - k, lo, hi))


def stick(n, left=True, vals=None):
    root = None
    for i in range(n):
        v = vals(i) if vals else i
        root = TreeNode(v, root, None) if left else TreeNode(v, None, root)
    return root


def _depth(t):
    return 0 if t is None else 1 + max(_depth(t.left), _depth(t.right))


def _nodes(t):
    return [] if t is None else [t] + _nodes(t.left) + _nodes(t.right)


def test_max_depth():
    assert max_depth(None) == 0 and max_depth(TreeNode(1)) == 1
    assert max_depth(TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))) == 3
    for _ in range(200):
        t = rand_tree(rnd.randint(0, 25))
        assert max_depth(t) == _depth(t)
    assert max_depth(stick(50_000)) == 50_000, "глубокое дерево — без рекурсии"


def test_level_order():
    assert level_order(None) == []
    assert level_order(TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))) == [[3], [9, 20], [15, 7]]
    t = TreeNode(1, TreeNode(2, None, TreeNode(4)), TreeNode(3, None, TreeNode(5)))
    assert level_order(t) == [[1], [2, 3], [4, 5]]
    for _ in range(100):
        t = rand_tree(rnd.randint(1, 20))
        lv = level_order(t)
        assert len(lv) == _depth(t) and sorted(sum(lv, [])) == sorted(n.val for n in _nodes(t))
        assert lv[0] == [t.val]


def _bst_slow(t, lo=float("-inf"), hi=float("inf")):
    return t is None or (lo < t.val < hi and _bst_slow(t.left, lo, t.val) and _bst_slow(t.right, t.val, hi))


def _insert(root, v):
    if root is None:
        return TreeNode(v)
    if v < root.val:
        root.left = _insert(root.left, v)
    elif v > root.val:
        root.right = _insert(root.right, v)
    return root


def test_is_valid_bst():
    assert is_valid_bst(None) and is_valid_bst(TreeNode(2, TreeNode(1), TreeNode(3)))
    assert not is_valid_bst(TreeNode(5, TreeNode(3, None, TreeNode(7)))), "7 в левом поддереве пятёрки"
    assert not is_valid_bst(TreeNode(2, TreeNode(2))), "равные значения запрещены"
    assert not is_valid_bst(TreeNode(5, TreeNode(1), TreeNode(4, TreeNode(3), TreeNode(6))))
    for _ in range(300):
        if rnd.random() < 0.5:
            t = None
            for v in rnd.sample(range(50), rnd.randint(1, 15)):
                t = _insert(t, v)
        else:
            t = rand_tree(rnd.randint(1, 8), 0, 9)
        assert is_valid_bst(t) == _bst_slow(t)
    assert is_valid_bst(stick(30_000, left=False)) is False, "правая палка с убывающими значениями — не BST"
    deep_ok = stick(30_000, left=True, vals=lambda i: i)       # каждый следующий корень больше — левая палка
    assert is_valid_bst(deep_ok) is True, "глубокое дерево — без рекурсии"


def test_lca():
    a, b, c, d, e = (TreeNode(1) for _ in range(5))     # одинаковые значения — сравнивай узлы
    a.left, a.right = b, c
    b.left, b.right = d, e
    assert lowest_common_ancestor(a, d, e) is b
    assert lowest_common_ancestor(a, d, c) is a
    assert lowest_common_ancestor(a, b, e) is b, "узел — предок самого себя"
    assert lowest_common_ancestor(a, a, a) is a
    for _ in range(200):
        t = rand_tree(rnd.randint(1, 20))
        nodes = _nodes(t)
        p, q = rnd.choice(nodes), rnd.choice(nodes)

        def path(root, x):
            if root is None:
                return None
            if root is x:
                return [root]
            sub = path(root.left, x) or path(root.right, x)
            return [root] + sub if sub else None

        pp, pq = path(t, p), path(t, q)
        want = [x for x, y in zip(pp, pq) if x is y][-1]
        assert lowest_common_ancestor(t, p, q) is want


def _same(a, b):
    stack = [(a, b)]
    while stack:
        x, y = stack.pop()
        if x is None or y is None:
            if x is not y:
                return False
            continue
        if x.val != y.val:
            return False
        stack += [(x.left, y.left), (x.right, y.right)]
    return True


def test_serialize():
    for t in (None, TreeNode(1), TreeNode(-12, None, TreeNode(345)), TreeNode(1, TreeNode(2), TreeNode(3, TreeNode(4), TreeNode(5)))):
        s = serialize(t)
        assert isinstance(s, str) and _same(deserialize(s), t)
    for _ in range(200):
        t = rand_tree(rnd.randint(0, 30), -1000, 1000)
        assert _same(deserialize(serialize(t)), t)
    deep = stick(3000, left=rnd.random() < 0.5)
    assert _same(deserialize(serialize(deep)), deep), "глубокое дерево"
