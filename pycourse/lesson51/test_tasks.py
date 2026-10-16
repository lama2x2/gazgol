# Проверяющая система урока 5.1 — не меняй этот файл.
import gc
import weakref

import pytest

from tasks import Point3D, TreeNode, WeakCache, top_allocations


def test_tree_node():
    gc.collect()
    gc.disable()
    try:
        root = TreeNode("root")
        a, b = TreeNode("a"), TreeNode("b")
        root.add_child(a)
        a.add_child(b)
        assert a.parent is root and b.parent is a and root.parent is None
        assert root.children == [a] and a.children == [b]
        refs = [weakref.ref(x) for x in (root, a, b)]
        del a, b
        assert refs[2]().parent.parent is root
        del root
        assert all(r() is None for r in refs), "дерево должно освободиться без gc: ссылка на родителя — слабая"
    finally:
        gc.enable()


class Obj:
    def __init__(self, k):
        self.k = k


def test_weak_cache():
    c = WeakCache()
    x = c.get("a", lambda: Obj("a"))
    y = c.get("a", lambda: Obj("другой"))
    assert x is y and x.k == "a" and c.misses == 1
    z = c.get("b", lambda: Obj("b"))
    assert c.misses == 2 and len(c) == 2
    del x, y
    gc.collect()
    assert len(c) == 1, "объект без внешних ссылок должен исчезнуть из кэша"
    w = c.get("a", lambda: Obj("новый"))
    assert w.k == "новый" and c.misses == 3
    assert z.k == "b"


def _alloc():
    small = [0] * 1000
    big = [0] * 300_000           # эта строка — лидер
    mid = bytearray(200_000)
    return small, big, mid


def test_top_allocations():
    start = _alloc.__code__.co_firstlineno
    res = top_allocations(_alloc, n=3)
    assert len(res) == 3 and all(isinstance(l, int) and isinstance(s, int) for l, s in res)
    assert res[0][0] == start + 2, f"лидер — строка с big, получили {res}"
    assert res[0][1] >= 2_000_000 and res[0][1] >= res[1][1] >= res[2][1]
    assert {res[1][0], res[2][0]} >= {start + 3}

    def boom():
        raise RuntimeError

    with pytest.raises(RuntimeError):
        top_allocations(boom)
    import tracemalloc
    assert not tracemalloc.is_tracing(), "tracemalloc нужно остановить и при исключении"


def test_point3d():
    p = Point3D(1, 2, 3)
    assert (p.x, p.y, p.z) == (1, 2, 3)
    assert not hasattr(p, "__dict__") and Point3D.__slots__ == ("x", "y", "z")
    with pytest.raises(AttributeError):
        p.x = 5
    with pytest.raises(AttributeError):
        p.w = 1
    with pytest.raises(AttributeError):
        del p.y
    assert p.x == 1
    assert p == Point3D(1, 2, 3) and p != Point3D(3, 2, 1) and (p == (1, 2, 3)) is False
    assert len({p, Point3D(1, 2, 3), Point3D(0, 0, 0)}) == 2
    assert repr(p) == "Point3D(1, 2, 3)"
