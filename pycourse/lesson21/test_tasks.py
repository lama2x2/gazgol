# Проверяющая система урока 2.1 — не меняй этот файл.
import inspect
import time

import tasks
from tasks import append_to, dedupe, deep_copy, freeze, make_grid


def test_append_to():
    assert append_to(1) == [1]
    assert append_to(2) == [2], "второй вызов без списка должен начинаться с пустого списка"
    lst = []
    assert append_to(5, lst) is lst, "переданный список нужно изменить на месте и вернуть его же"
    assert lst == [5], "пустой список, переданный явно, должен получить элемент"
    other = [1]
    append_to(2, other)
    assert other == [1, 2]
    assert append_to(3) == [3]


def test_make_grid():
    g = make_grid(3, 2, fill=".")
    assert g == [[".", "."], [".", "."], [".", "."]]
    g[0][0] = "#"
    assert g[1][0] == "." and g[2][0] == ".", "строки сетки — один и тот же список: изменение одной меняет все"
    assert make_grid(0, 5) == []
    assert make_grid(2, 0) == [[], []]
    assert len({id(r) for r in make_grid(4, 4)}) == 4


def test_deep_copy():
    src = inspect.getsource(tasks)
    assert "import copy" not in src and "from copy" not in src, "реши без модуля copy"
    a = {"x": [1, [2, {"y": {3}}]], "t": (1, [2]), "s": "str", "n": None}
    b = deep_copy(a)
    assert b == a
    assert b is not a and b["x"] is not a["x"] and b["x"][1] is not a["x"][1]
    assert b["x"][1][1] is not a["x"][1][1] and b["x"][1][1]["y"] is not a["x"][1][1]["y"]
    assert b["t"][1] is not a["t"][1], "список внутри кортежа тоже копируется"
    b["x"][1][1]["y"].add(4)
    b["t"][1].append(3)
    assert a == {"x": [1, [2, {"y": {3}}]], "t": (1, [2]), "s": "str", "n": None}
    assert isinstance(deep_copy((1, 2)), tuple) and isinstance(deep_copy({1}), set)
    assert deep_copy(5) == 5 and deep_copy([]) == []


def test_dedupe():
    assert dedupe([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert dedupe([]) == []
    assert dedupe(["a", "a"]) == ["a"]
    assert dedupe([1, True, 1.0, 2]) == [1, 2], "1, True и 1.0 равны и имеют один хеш"
    big = list(range(100_000)) * 2
    t = time.perf_counter()
    assert dedupe(big) == list(range(100_000))
    assert time.perf_counter() - t < 1.0, "слишком медленно: нужна проверка через множество, O(n)"


def test_freeze():
    assert freeze([1, [2, 3]]) == (1, (2, 3))
    assert freeze({1, 2}) == frozenset({1, 2})
    a = freeze({"a": 1, "b": [2, {"c": {3}}]})
    b = freeze({"b": [2, {"c": {3}}], "a": 1})
    assert a == b and hash(a) == hash(b), "порядок ключей не должен влиять"
    assert freeze({"a": [1]}) != freeze({"a": [2]})
    assert freeze([1, 2]) != freeze([2, 1]), "у списка порядок важен"
    cache = {freeze({"q": [1, 2]}): "ok"}
    assert cache[freeze({"q": [1, 2]})] == "ok"
    assert freeze("s") == "s" and freeze(None) is None
