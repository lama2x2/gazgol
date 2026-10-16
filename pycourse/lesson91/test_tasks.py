# Проверяющая система урока 9.1 — не меняй этот файл.
import itertools
import random
import string
import time
from collections import deque

from tasks import can_finish, num_islands, shortest_path_grid, topo_order, word_ladder

rnd = random.Random(91)


def _islands_slow(g):
    R, C = len(g), len(g[0]) if g else 0
    seen, cnt = set(), 0

    def fill(r, c):
        st = [(r, c)]
        while st:
            y, x = st.pop()
            if (y, x) in seen or not (0 <= y < R and 0 <= x < C) or g[y][x] != "1":
                continue
            seen.add((y, x))
            st += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    for r in range(R):
        for c in range(C):
            if g[r][c] == "1" and (r, c) not in seen:
                cnt += 1
                fill(r, c)
    return cnt


def test_num_islands():
    assert num_islands([list("11110"), list("11010"), list("11000"), list("00000")]) == 1
    assert num_islands([list("11000"), list("11000"), list("00100"), list("00011")]) == 3
    assert num_islands([]) == 0 and num_islands([[]]) == 0
    for _ in range(200):
        R, C = rnd.randint(1, 7), rnd.randint(1, 7)
        g = [[rnd.choice("01") for _ in range(C)] for _ in range(R)]
        assert num_islands(g) == _islands_slow(g)
    N = 500
    snake = [["1" if r % 4 != 1 and r % 4 != 3 or (r % 4 == 1 and c == N - 1) or (r % 4 == 3 and c == 0) else "0"
              for c in range(N)] for r in range(N)]
    t0 = time.perf_counter()
    assert num_islands(snake) == 1, "длинный остров-змейка — без рекурсии"
    assert time.perf_counter() - t0 < 3


def _sp_slow(g):
    R, C = len(g), len(g[0])
    if g[0][0] or g[-1][-1]:
        return -1
    d = {(0, 0): 0}
    q = deque([(0, 0)])
    while q:
        y, x = q.popleft()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < R and 0 <= nx < C and not g[ny][nx] and (ny, nx) not in d:
                d[(ny, nx)] = d[(y, x)] + 1
                q.append((ny, nx))
    return d.get((R - 1, C - 1), -1)


def test_shortest_path_grid():
    assert shortest_path_grid([[0, 0, 0], [1, 1, 0], [0, 0, 0]]) == 4
    assert shortest_path_grid([[0]]) == 0
    assert shortest_path_grid([[1]]) == -1 and shortest_path_grid([[0, 1], [1, 0]]) == -1
    for _ in range(300):
        R, C = rnd.randint(1, 7), rnd.randint(1, 7)
        g = [[int(rnd.random() < 0.3) for _ in range(C)] for _ in range(R)]
        assert shortest_path_grid(g) == _sp_slow(g), f"{g}"


def _has_cycle(n, edges):
    g = {i: [] for i in range(n)}
    for a, b in edges:
        g[b].append(a)
    color = [0] * n

    def dfs(u):
        color[u] = 1
        for v in g[u]:
            if color[v] == 1 or (color[v] == 0 and dfs(v)):
                return True
        color[u] = 2
        return False
    return any(color[i] == 0 and dfs(i) for i in range(n))


def test_can_finish():
    assert can_finish(2, [(1, 0)]) is True
    assert can_finish(2, [(1, 0), (0, 1)]) is False
    assert can_finish(3, []) is True
    assert can_finish(1, [(0, 0)]) is False, "петля — цикл"
    for _ in range(300):
        n = rnd.randint(1, 7)
        edges = [(rnd.randrange(n), rnd.randrange(n)) for _ in range(rnd.randint(0, 8))]
        assert can_finish(n, edges) == (not _has_cycle(n, edges)), f"{n}, {edges}"


def test_topo_order():
    assert topo_order(4, [(1, 0), (2, 0), (3, 1), (3, 2)]) == [0, 1, 2, 3]
    assert topo_order(3, [(0, 2), (1, 2)]) == [2, 0, 1]
    assert topo_order(3, []) == [0, 1, 2]
    assert topo_order(2, [(0, 1), (1, 0)]) is None
    for _ in range(300):
        n = rnd.randint(1, 7)
        edges = [(rnd.randrange(n), rnd.randrange(n)) for _ in range(rnd.randint(0, 8))]
        got = topo_order(n, edges)
        if _has_cycle(n, edges):
            assert got is None, f"{n}, {edges}: есть цикл"
            continue
        assert sorted(got) == list(range(n))
        pos = {v: i for i, v in enumerate(got)}
        assert all(pos[b] < pos[a] for a, b in edges), f"{edges} → {got}: зависимость позже зависящего"
        # наименьшая из готовых: перебором проверяем лексикографическую минимальность
        best = None
        for perm in itertools.permutations(range(n)):
            p = {v: i for i, v in enumerate(perm)}
            if all(p[b] < p[a] for a, b in edges):
                best = list(perm)
                break
        assert got == best, f"{n}, {edges}: ожидался {best}"


def _ladder_slow(b, e, words):
    ws = set(words)
    if e not in ws:
        return 0
    d = {b: 1}
    q = deque([b])
    while q:
        u = q.popleft()
        if u == e:
            return d[u]
        for w in ws:
            if w not in d and len(w) == len(u) and sum(x != y for x, y in zip(w, u)) == 1:
                d[w] = d[u] + 1
                q.append(w)
    return 0


def test_word_ladder():
    assert word_ladder("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5
    assert word_ladder("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0
    assert word_ladder("a", "c", ["a", "b", "c"]) == 2
    for _ in range(100):
        words = list({"".join(rnd.choice("abc") for _ in range(3)) for _ in range(12)})
        b, e = "".join(rnd.choice("abc") for _ in range(3)), rnd.choice(words)
        if b != e:
            assert word_ladder(b, e, words) == _ladder_slow(b, e, words), f"{b}->{e} {words}"
    big = list({"".join(rnd.choice(string.ascii_lowercase[:8]) for _ in range(5)) for _ in range(5000)})
    t0 = time.perf_counter()
    word_ladder(big[0], big[-1], big)
    assert time.perf_counter() - t0 < 2, "нужны шаблоны вида h*t, а не попарное сравнение слов"
