# Проверяющая система урока 9.2 — не меняй этот файл.
import itertools
import random
import time

from tasks import DSU, dijkstra, is_tree, mst_cost, network_delay

rnd = random.Random(92)


def _floyd(n, edges):
    INF = float("inf")
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        d[u][v] = min(d[u][v], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    return d


def test_dijkstra():
    assert dijkstra(3, [(0, 1, 4), (0, 2, 1), (2, 1, 2)], 0) == [0, 3, 1]
    assert dijkstra(3, [(0, 1, 1)], 2) == [-1, -1, 0]
    assert dijkstra(2, [(0, 1, 5), (0, 1, 2), (1, 1, 0)], 0) == [0, 2]
    for _ in range(200):
        n = rnd.randint(1, 7)
        edges = [(rnd.randrange(n), rnd.randrange(n), rnd.randint(0, 9)) for _ in range(rnd.randint(0, 15))]
        s = rnd.randrange(n)
        d = _floyd(n, edges)[s]
        assert dijkstra(n, edges, s) == [x if x != float("inf") else -1 for x in d], f"{n}, {edges}, {s}"
    n = 20_000
    edges = [(i, i + 1, 1) for i in range(n - 1)] + [(rnd.randrange(n), rnd.randrange(n), rnd.randint(1, 100)) for _ in range(80_000)]
    t0 = time.perf_counter()
    res = dijkstra(n, edges, 0)
    assert res[0] == 0 and all(0 <= x <= i for i, x in enumerate(res))
    assert time.perf_counter() - t0 < 3, "нужна куча: O((V + E) log V)"


def test_network_delay():
    assert network_delay([(2, 1, 1), (2, 3, 1), (3, 4, 1)], 4, 2) == 2
    assert network_delay([(1, 2, 1)], 2, 1) == 1
    assert network_delay([(1, 2, 1)], 2, 2) == -1
    assert network_delay([], 1, 1) == 0
    for _ in range(200):
        n = rnd.randint(1, 6)
        edges = [(rnd.randint(1, n), rnd.randint(1, n), rnd.randint(1, 9)) for _ in range(rnd.randint(0, 12))]
        k = rnd.randint(1, n)
        d = _floyd(n, [(u - 1, v - 1, w) for u, v, w in edges])[k - 1]
        want = max(d) if max(d) != float("inf") else -1
        assert network_delay(edges, n, k) == want


def test_dsu():
    d = DSU(5)
    assert d.components == 5
    assert d.union(0, 1) is True and d.union(1, 0) is False
    assert d.union(2, 3) and d.union(1, 3)
    assert d.find(0) == d.find(2) and d.find(4) != d.find(0)
    assert d.components == 2
    n = 200_000
    d = DSU(n)
    t0 = time.perf_counter()
    for i in range(n - 1):
        d.union(i, i + 1)
    for i in range(0, n, 7):
        d.find(i)
    assert d.components == 1
    assert time.perf_counter() - t0 < 2, "нужны сжатие путей и объединение по размеру"
    for _ in range(100):
        n = rnd.randint(1, 10)
        d = DSU(n)
        groups = [{i} for i in range(n)]
        for _ in range(rnd.randint(0, 12)):
            a, b = rnd.randrange(n), rnd.randrange(n)
            ga = next(g for g in groups if a in g)
            gb = next(g for g in groups if b in g)
            assert d.union(a, b) == (ga is not gb)
            if ga is not gb:
                ga |= gb
                groups.remove(gb)
        assert d.components == len(groups)


def _is_tree_slow(n, edges):
    if len(edges) != n - 1:
        return False
    adj = {i: set() for i in range(n)}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    seen, st = {0}, [0]
    while st:
        u = st.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                st.append(v)
    return len(seen) == n


def test_is_tree():
    assert is_tree(4, [(0, 1), (1, 2), (1, 3)]) is True
    assert is_tree(4, [(0, 1), (1, 2), (2, 0)]) is False
    assert is_tree(1, []) is True
    assert is_tree(2, [(0, 0)]) is False
    assert is_tree(3, [(0, 1), (0, 1)]) is False, "кратное ребро — цикл"
    for _ in range(300):
        n = rnd.randint(1, 6)
        edges = [(rnd.randrange(n), rnd.randrange(n)) for _ in range(rnd.randint(0, 6))]
        assert is_tree(n, edges) == _is_tree_slow(n, edges), f"{n}, {edges}"


def _mst_slow(n, edges):
    best = None
    for combo in itertools.combinations(edges, n - 1):
        if _is_tree_slow(n, [(a, b) for a, b, _ in combo]):
            w = sum(c[2] for c in combo)
            best = w if best is None else min(best, w)
    return -1 if best is None else best


def test_mst_cost():
    assert mst_cost(4, [(0, 1, 1), (1, 2, 2), (0, 2, 3), (2, 3, 1)]) == 4
    assert mst_cost(3, [(0, 1, 1)]) == -1
    assert mst_cost(1, []) == 0
    assert mst_cost(2, [(0, 1, -5), (0, 1, 3)]) == -5
    for _ in range(150):
        n = rnd.randint(1, 5)
        edges = [(rnd.randrange(n), rnd.randrange(n), rnd.randint(-3, 9)) for _ in range(rnd.randint(0, 7))]
        assert mst_cost(n, edges) == _mst_slow(n, edges), f"{n}, {edges}"
