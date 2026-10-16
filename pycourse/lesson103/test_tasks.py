# Проверяющая система урока 10.3 — не меняй этот файл.
import inspect
import random
import time

import tasks
from tasks import can_jump, count_bits, erase_overlap, is_power_of_two, max_profit, single_number

rnd = random.Random(103)


def test_is_power_of_two():
    src = inspect.getsource(tasks.is_power_of_two)
    assert "for " not in src and "while " not in src and "math" not in src and "log" not in src, "битовым трюком, O(1)"
    pows = {1 << k for k in range(40)}
    for x in range(-70, 5000):
        assert is_power_of_two(x) == (x in pows), f"is_power_of_two({x})"
    assert is_power_of_two(2**1000) and not is_power_of_two(2**1000 + 2) and not is_power_of_two(-(2**10))


def test_single_number():
    src = inspect.getsource(tasks.single_number)
    assert "Counter" not in src and "set(" not in src and "dict" not in src and "{" not in src, "O(1) памяти"
    assert single_number([2, 2, 1]) == 1 and single_number([4, 1, 2, 1, 2]) == 4 and single_number([-7]) == -7
    for _ in range(200):
        pairs = rnd.sample(range(-100, 100), rnd.randint(0, 8))
        one = rnd.choice([x for x in range(-200, 200) if x not in pairs])
        a = pairs * 2 + [one]
        rnd.shuffle(a)
        assert single_number(a) == one


def test_count_bits():
    assert count_bits(0) == [0] and count_bits(5) == [0, 1, 1, 2, 1, 2]
    n = 300_000
    t0 = time.perf_counter()
    res = count_bits(n)
    assert time.perf_counter() - t0 < 1
    assert len(res) == n + 1 and all(res[i] == bin(i).count("1") for i in range(0, n, 997))


def test_max_profit():
    assert max_profit([7, 1, 5, 3, 6, 4]) == 5 and max_profit([7, 6, 4, 3, 1]) == 0
    assert max_profit([]) == 0 and max_profit([5]) == 0 and max_profit([7, 1]) == 0
    for _ in range(300):
        p = [rnd.randint(0, 20) for _ in range(rnd.randint(0, 10))]
        want = max([p[j] - p[i] for i in range(len(p)) for j in range(i + 1, len(p))] + [0])
        assert max_profit(p) == want, f"{p}"


def test_can_jump():
    assert can_jump([2, 3, 1, 1, 4]) and not can_jump([3, 2, 1, 0, 4]) and can_jump([0])
    for _ in range(300):
        a = [rnd.randint(0, 3) for _ in range(rnd.randint(1, 10))]
        reach = [False] * len(a)
        reach[0] = True
        for i in range(len(a)):
            if reach[i]:
                for j in range(i + 1, min(len(a), i + a[i] + 1)):
                    reach[j] = True
        assert can_jump(a) == reach[-1], f"{a}"
    big = [1] * 199_999 + [0]
    t0 = time.perf_counter()
    assert can_jump(big)
    assert can_jump([200_000] + [0] * 199_999)
    assert time.perf_counter() - t0 < 1, "нужно O(n)"


def _erase_slow(iv):
    n = len(iv)
    best = 0
    for mask in range(1 << n):
        chosen = sorted(iv[i] for i in range(n) if mask >> i & 1)
        if all(chosen[k][1] <= chosen[k + 1][0] for k in range(len(chosen) - 1)):
            best = max(best, len(chosen))
    return n - best


def test_erase_overlap():
    assert erase_overlap([[1, 2], [2, 3], [3, 4], [1, 3]]) == 1
    assert erase_overlap([[1, 2], [1, 2], [1, 2]]) == 2
    assert erase_overlap([[1, 2], [2, 3]]) == 0 and erase_overlap([]) == 0
    assert erase_overlap([[1, 100], [2, 3], [3, 4]]) == 1
    for _ in range(200):
        iv = []
        for _ in range(rnd.randint(0, 8)):
            s = rnd.randint(0, 10)
            iv.append([s, s + rnd.randint(1, 5)])
        assert erase_overlap([list(x) for x in iv]) == _erase_slow(iv), f"{iv}"
