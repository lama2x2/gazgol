# Проверяющая система урока 5.3 — не меняй этот файл.
import asyncio
import time

import pytest

from tasks import fetch_all, gather_blocking, race, run_pipeline, with_timeout


def run(coro):
    return asyncio.run(asyncio.wait_for(coro, 10))


class Tracker:
    def __init__(self):
        self.active = self.peak = 0

    async def fetch(self, url):
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            await asyncio.sleep(0.02)
            return url.upper()
        finally:
            self.active -= 1


def test_fetch_all():
    tr = Tracker()
    urls = [f"u{i}" for i in range(30)]
    t = time.perf_counter()
    res = run(fetch_all(urls, tr.fetch, limit=5))
    took = time.perf_counter() - t
    assert res == [u.upper() for u in urls]
    assert tr.peak == 5, f"одновременно было {tr.peak} запросов, а лимит 5"
    assert took < 0.3, f"{took:.2f} c — похоже, запросы идут последовательно"
    assert run(fetch_all([], tr.fetch, 3)) == []


def test_with_timeout():
    state = {}

    async def slow():
        try:
            await asyncio.sleep(1)
            return "поздно"
        except asyncio.CancelledError:
            state["cancelled"] = True
            raise

    async def quick():
        await asyncio.sleep(0.01)
        return "вовремя"

    t = time.perf_counter()
    assert run(with_timeout(slow(), 0.05, default="нет")) == "нет"
    assert time.perf_counter() - t < 0.5
    assert state.get("cancelled"), "опоздавшая корутина должна быть отменена"
    assert run(with_timeout(quick(), 1)) == "вовремя"
    assert run(with_timeout(slow(), 0.01)) is None


def test_race():
    cancelled = []

    async def answer(v, d, fail=False):
        try:
            await asyncio.sleep(d)
        except asyncio.CancelledError:
            cancelled.append(v)
            raise
        if fail:
            raise ValueError(v)
        return v

    async def main():
        r = await race(answer("медленный", 0.2), answer("быстрый", 0.02), answer("сломанный", 0.01, fail=True))
        await asyncio.sleep(0)
        left = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        return r, left

    t = time.perf_counter()
    r, left = run(main())
    assert r == "быстрый", "падение одной задачи — не повод сдаваться"
    assert time.perf_counter() - t < 0.15
    assert cancelled == ["медленный"], "остальные задачи нужно отменить"
    assert not left, "отменённые задачи нужно дождаться"

    with pytest.raises(ExceptionGroup) as ei:
        run(race(answer("a", 0.01, True), answer("b", 0.02, True)))
    assert sorted(str(e) for e in ei.value.exceptions) == ["a", "b"]


def test_gather_blocking():
    ticks = []

    async def pulse():
        for _ in range(15):
            ticks.append(time.perf_counter())
            await asyncio.sleep(0.01)

    def blocking(v):
        def f():
            time.sleep(0.12)
            return v
        return f

    async def main():
        p = asyncio.create_task(pulse())
        res = await gather_blocking([blocking(1), blocking(2), blocking(3)])
        await p
        return res

    t = time.perf_counter()
    res = run(main())
    took = time.perf_counter() - t
    assert res == [1, 2, 3]
    assert took < 0.3, "блокирующие функции должны выполняться конкурентно"
    gaps = [b - a for a, b in zip(ticks, ticks[1:])]
    assert max(gaps[:8]) < 0.08, "пульс замер — цикл событий был заблокирован"


def test_run_pipeline():
    state = {"active": 0, "peak": 0, "qmax": 0}
    orig_queue = asyncio.Queue

    class SpyQueue(orig_queue):
        async def put(self, item):
            await super().put(item)
            state["qmax"] = max(state["qmax"], self.qsize())
            state["maxsize"] = self.maxsize

    async def work(x):
        state["active"] += 1
        state["peak"] = max(state["peak"], state["active"])
        try:
            await asyncio.sleep(0.01 * (x % 3))
            if x == 7:
                raise ValueError("семь")
            return x * 10
        finally:
            state["active"] -= 1

    asyncio.Queue = SpyQueue
    try:
        res = run(run_pipeline(range(20), work, n_workers=4))
    finally:
        asyncio.Queue = orig_queue
    assert [r for i, r in enumerate(res) if i != 7] == [i * 10 for i in range(20) if i != 7]
    assert isinstance(res[7], ValueError), "ошибка элемента — на его месте в результатах"
    assert state["peak"] <= 4 and state["peak"] >= 2, f"воркеров одновременно: {state['peak']}"
    assert state.get("maxsize") == 8, "нужна очередь asyncio.Queue(maxsize=n_workers * 2)"
    assert state["qmax"] <= 8
    assert run(run_pipeline([], work, 2)) == []
