# Проверяющая система урока 5.2 — не меняй этот файл.
import inspect
import random
import sys
import threading
import time

import pytest

import tasks
from tasks import Account, BoundedBuffer, ThreadSafeCounter, parallel_map, parallel_sum_squares, transfer


def _run_threads(target, n, timeout=20):
    ts = [threading.Thread(target=target, args=(i,), daemon=True) for i in range(n)]
    for t in ts:
        t.start()
    deadline = time.monotonic() + timeout
    for t in ts:
        t.join(max(0, deadline - time.monotonic()))
    assert not any(t.is_alive() for t in ts), "потоки не завершились — похоже на взаимную блокировку"


def test_counter():
    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    try:
        c = ThreadSafeCounter()

        def work(_):
            for _ in range(20_000):
                c.increment()
        _run_threads(work, 16)
        assert c.value == 16 * 20_000
        c.increment(5)
        assert c.value == 320_005
    finally:
        sys.setswitchinterval(old)
    assert "Lock" in inspect.getsource(tasks.ThreadSafeCounter)


def test_parallel_map():
    src = inspect.getsource(tasks.parallel_map)
    assert "concurrent" not in src and "Executor" not in src, "реши на threading без concurrent.futures"
    active, peak, lock = [0], [0], threading.Lock()

    def slow(x):
        with lock:
            active[0] += 1
            peak[0] = max(peak[0], active[0])
        time.sleep(random.uniform(0.005, 0.02))
        with lock:
            active[0] -= 1
        return x * x

    items = list(range(40))
    t = time.perf_counter()
    assert parallel_map(slow, items, workers=8) == [x * x for x in items]
    assert time.perf_counter() - t < 0.4, "похоже, задачи выполняются последовательно"
    assert 2 <= peak[0] <= 8, f"одновременно работало {peak[0]} вызовов, а должно быть не больше 8"
    assert parallel_map(slow, [], workers=3) == []

    def boom(x):
        if x == 5:
            raise ValueError("пять")
        return x

    with pytest.raises(ValueError, match="пять"):
        parallel_map(boom, range(10), workers=3)


def test_bounded_buffer():
    src = inspect.getsource(tasks.BoundedBuffer)
    assert "Queue" not in src and "Condition" in src, "сделай на Condition, без queue.Queue"
    b = BoundedBuffer(2)
    b.put(1)
    b.put(2)
    assert len(b) == 2
    with pytest.raises(TimeoutError):
        b.put(3, timeout=0.05)
    assert b.get() == 1 and b.get() == 2
    with pytest.raises(TimeoutError):
        b.get(timeout=0.05)

    buf = BoundedBuffer(3)
    out, N = [], 2000

    def producer(i):
        for k in range(N):
            buf.put((i, k))

    def consumer(_):
        for _ in range(N):
            out.append(buf.get(timeout=5))

    ts = [threading.Thread(target=producer, args=(i,)) for i in range(2)] + \
         [threading.Thread(target=consumer, args=(i,)) for i in range(2)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(20)
    assert not any(t.is_alive() for t in ts)
    assert sorted(out) == sorted((i, k) for i in range(2) for k in range(N))
    for i in range(2):
        mine = [k for j, k in out if j == i]
        assert mine == sorted(mine), "порядок элементов одного производителя должен сохраняться (FIFO)"


def test_transfer():
    accs = [Account(1000) for _ in range(4)]
    a, b = accs[0], accs[1]
    transfer(a, b, 300)
    assert (a.balance, b.balance) == (700, 1300)
    with pytest.raises(ValueError):
        transfer(a, b, 701)
    with pytest.raises(ValueError):
        transfer(a, a, 1)
    assert (a.balance, b.balance) == (700, 1300)

    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    try:
        def work(i):
            rnd = random.Random(i)
            for _ in range(3000):
                x, y = rnd.sample(accs, 2)
                try:
                    transfer(x, y, rnd.randint(1, 50))
                except ValueError:
                    pass
        _run_threads(work, 8, timeout=15)
    finally:
        sys.setswitchinterval(old)
    assert sum(acc.balance for acc in accs) == 4000, "общая сумма должна сохраниться"
    assert all(acc.balance >= 0 for acc in accs)


def test_process_pool():
    assert parallel_sum_squares(10) == 285
    assert parallel_sum_squares(1, workers=3) == 0
    assert parallel_sum_squares(0) == 0
    n = 200_003
    assert parallel_sum_squares(n, workers=4) == sum(i * i for i in range(n))
    assert "ProcessPoolExecutor" in inspect.getsource(tasks.parallel_sum_squares)
