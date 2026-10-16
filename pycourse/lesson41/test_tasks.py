# Проверяющая система урока 4.1 — не меняй этот файл.
import ast
import inspect
import math
import random

import pytest

import tasks
from tasks import HashMap, Money, Vector, Version


def test_version():
    v = Version.from_string("1.10.2")
    assert v == Version(1, 10, 2)
    assert Version.from_string("1.10") > Version.from_string("1.9"), "сравнивай числа, а не строки"
    assert Version(1, 2) == Version(1, 2, 0) and hash(Version(1, 2)) == hash(Version(1, 2, 0))
    assert Version(1, 2) < Version(1, 2, 1) <= Version(1, 2, 1) < Version(2)
    assert Version(3) >= Version(2, 99) and Version(3) != Version(3, 1)
    assert sorted(map(Version.from_string, ["1.10", "1.2", "1.9.9", "0.1"])) == \
        [Version(0, 1), Version(1, 2), Version(1, 9, 9), Version(1, 10)]
    assert repr(v) == "Version('1.10.2')" and str(v) == "1.10.2"
    assert len({Version(1), Version(1, 0), Version(1, 0, 0)}) == 1
    assert (Version(1) == "1") is False, "сравнение с чужим типом — NotImplemented, итог False"
    with pytest.raises(TypeError):
        Version(1) < "2"

    class Sub(Version):
        pass

    assert type(Sub.from_string("2.0")) is Sub, "from_string должен быть classmethod и создавать cls"


def test_money():
    a, b = Money(1050, "RUB"), Money(275, "RUB")
    assert a + b == Money(1325, "RUB")
    assert str(a) == "10.50 RUB" and str(Money(5, "USD")) == "0.05 USD"
    assert str(Money(-150, "RUB")) == "-1.50 RUB", "отрицательные суммы"
    assert repr(a) == "Money(1050, 'RUB')"
    assert sum([a, b, Money(1, "RUB")]) == Money(1326, "RUB"), "нужен __radd__ для sum()"
    with pytest.raises(ValueError):
        a + Money(1, "USD")
    with pytest.raises(TypeError):
        a + 5
    assert b < a and a >= b and Money(1, "RUB") != Money(1, "USD")
    assert len({Money(100, "RUB"), Money(100, "RUB"), Money(100, "USD")}) == 2
    assert not Money(0, "RUB") and Money(1, "RUB")
    assert (a == 1050) is False


def test_vector():
    v, w = Vector(1, 2, 3), Vector(4, 5, 6)
    assert len(v) == 3 and v[0] == 1 and v[-1] == 3
    assert v[1:] == Vector(2, 3) and isinstance(v[1:], Vector)
    assert list(v) == [1, 2, 3]
    assert abs(Vector(3, 4)) == pytest.approx(5.0)
    assert v * 2 == Vector(2, 4, 6) and 2 * v == Vector(2, 4, 6), "нужен __rmul__"
    assert v @ w == 32
    with pytest.raises(ValueError):
        v @ Vector(1, 2)
    with pytest.raises(TypeError):
        v * "x"
    assert repr(Vector(1, 2.5)) == "Vector(1, 2.5)"
    assert Vector(1, 2) != (1, 2) and Vector() == Vector() and not math.isnan(abs(Vector()))


def _uses_builtin_maps():
    tree = ast.parse(inspect.getsource(tasks.HashMap))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Dict, ast.Set, ast.DictComp, ast.SetComp)):
            return True
        if isinstance(node, ast.Name) and node.id in ("dict", "set", "frozenset", "defaultdict", "OrderedDict", "Counter"):
            return True
    return False


class Collide:
    """Ключ с одинаковым хешем для всех экземпляров."""

    def __init__(self, v):
        self.v = v

    def __hash__(self):
        return 42

    def __eq__(self, other):
        return isinstance(other, Collide) and self.v == other.v


def test_hashmap():
    assert not _uses_builtin_maps(), "HashMap — без dict и set внутри"
    m = HashMap()
    assert len(m) == 0 and "a" not in m and m.get("a") is None and m.get("a", 7) == 7
    m["a"] = 1
    m["b"] = 2
    m["a"] = 10
    assert len(m) == 2 and m["a"] == 10 and "b" in m
    del m["a"]
    assert "a" not in m and len(m) == 1
    with pytest.raises(KeyError):
        m["a"]
    with pytest.raises(KeyError):
        del m["zzz"]
    m[1] = "int"
    m[1.0] = "float"
    m[True] = "bool"
    assert m[1] == "bool" and len(m) == 2, "1, 1.0 и True — один ключ, как в dict"
    keys = [Collide(i) for i in range(50)]
    for i, k in enumerate(keys):
        m[k] = i
    assert all(m[Collide(i)] == i for i in range(50)), "коллизии хешей"
    assert sorted(x.v for x in m if isinstance(x, Collide)) == list(range(50))


def test_hashmap__random_vs_dict():
    rnd = random.Random(41)
    m, d = HashMap(), {}
    for _ in range(20_000):
        k = rnd.randint(0, 3000)
        op = rnd.random()
        if op < 0.6:
            m[k] = d[k] = rnd.random()
        elif op < 0.85:
            if k in d:
                del d[k]
                del m[k]
        else:
            assert (k in m) == (k in d) and m.get(k) == d.get(k)
    assert len(m) == len(d)
    assert sorted(m) == sorted(d)
    assert all(m[k] == v for k, v in d.items())
    assert hasattr(m, "_buckets") is False or len(m._buckets) >= len(d) // 2, "таблица должна расти"
