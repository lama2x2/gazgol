# Проверяющая система урока 8.1 — не меняй этот файл.
import random
import re
import time

import pytest

from tasks import MinStack, broken_keyboard, daily_temperatures, decode_string, is_valid_brackets

rnd = random.Random(81)


def _valid_slow(s):
    s = "".join(c for c in s if c in "()[]{}")
    while True:
        t = s.replace("()", "").replace("[]", "").replace("{}", "")
        if t == s:
            return not s
        s = t


def test_is_valid_brackets():
    assert is_valid_brackets("") and is_valid_brackets("()[]{}") and is_valid_brackets("f(a[1]) {x}")
    assert not is_valid_brackets("([)]") and not is_valid_brackets("((") and not is_valid_brackets(")")
    assert not is_valid_brackets("}{")
    for _ in range(500):
        s = "".join(rnd.choice("()[]{}a") for _ in range(rnd.randint(0, 10)))
        assert is_valid_brackets(s) == _valid_slow(s), repr(s)


def _kb_slow(s):
    out = []
    for ch in s:
        if ch in "bB":
            want = str.islower if ch == "b" else str.isupper
            for i in range(len(out) - 1, -1, -1):
                if want(out[i]):
                    out.pop(i)
                    break
        else:
            out.append(ch)
    return "".join(out)


def test_broken_keyboard():
    assert broken_keyboard("aXbY") == "XY"
    assert broken_keyboard("ACcBd") == "Acd"
    assert broken_keyboard("bBb") == ""
    assert broken_keyboard("") == ""
    for _ in range(500):
        s = "".join(rnd.choice("aAcCbB") for _ in range(rnd.randint(0, 12)))
        assert broken_keyboard(s) == _kb_slow(s), repr(s)
    big = "Q" + "a" * 100_000 + "b" * 99_999 + "B" * 3
    t0 = time.perf_counter()
    assert broken_keyboard(big) == "a"
    assert time.perf_counter() - t0 < 1, "нужно O(n): не удаляй из середины списка"


def test_daily_temperatures():
    assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
    assert daily_temperatures([30, 30, 31]) == [2, 1, 0], "равная температура — не теплее"
    assert daily_temperatures([]) == []
    for _ in range(300):
        t = [rnd.randint(0, 5) for _ in range(rnd.randint(0, 12))]
        want = [next((j - i for j in range(i + 1, len(t)) if t[j] > t[i]), 0) for i in range(len(t))]
        assert daily_temperatures(t) == want, f"{t}"
    big = list(range(200_000, 0, -1)) + [10**6]
    t0 = time.perf_counter()
    res = daily_temperatures(big)
    assert res[0] == 200_000 and res[-1] == 0
    assert time.perf_counter() - t0 < 1.5, "нужно O(n)"


def test_min_stack():
    s = MinStack()
    s.push(5); s.push(3); s.push(7); s.push(3)
    assert s.get_min() == 3 and s.top() == 3
    assert s.pop() == 3 and s.get_min() == 3
    assert s.pop() == 7 and s.pop() == 3 and s.get_min() == 5
    assert s.pop() == 5
    with pytest.raises(IndexError):
        s.pop()
    with pytest.raises(IndexError):
        s.top()
    ref = []
    for _ in range(2000):
        if ref and rnd.random() < 0.4:
            assert s.pop() == ref.pop()
        else:
            x = rnd.randint(-50, 50)
            s.push(x)
            ref.append(x)
        if ref:
            assert s.get_min() == min(ref) and s.top() == ref[-1]


def _decode_slow(s):
    while "[" in s:
        s = re.sub(r"(\d+)\[([a-z]*)\]", lambda m: m.group(2) * int(m.group(1)), s)
    return s


def test_decode_string():
    assert decode_string("3[a2[c]]") == "accaccacc"
    assert decode_string("2[abc]3[cd]ef") == "abcabccdcdcdef"
    assert decode_string("abc") == "abc" and decode_string("") == ""
    assert decode_string("10[z]") == "z" * 10
    assert decode_string("2[]x") == "x"
    for _ in range(200):
        def gen(d):
            parts = []
            for _ in range(rnd.randint(1, 3)):
                if d < 3 and rnd.random() < 0.4:
                    parts.append(f"{rnd.randint(1, 12)}[{gen(d + 1)}]")
                else:
                    parts.append(rnd.choice("xyz") * rnd.randint(0, 2))
            return "".join(parts)
        s = gen(0)
        assert decode_string(s) == _decode_slow(s), repr(s)
    deep = "1[" * 500 + "q" + "]" * 500
    assert decode_string(deep) == "q", "глубокая вложенность"
