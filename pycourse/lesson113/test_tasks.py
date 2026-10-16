# Проверяющая система урока 11.3 — не меняй этот файл.
import asyncio
import time

import pytest

from tasks import fetch_all, merge_settings, paginate, parse_duration, top_words


def test_paginate():
    items = list(range(25))
    p1 = paginate(items, 1)
    assert p1["items"] == list(range(10)) and p1["total_pages"] == 3 and p1["has_next"] is True
    p3 = paginate(items, 3)
    assert p3["items"] == [20, 21, 22, 23, 24] and p3["has_next"] is False
    assert paginate(items, 4)["items"] == [] and paginate(items, 4)["has_next"] is False
    assert paginate(list(range(20)), 2)["total_pages"] == 2 and paginate(list(range(20)), 2)["has_next"] is False
    assert paginate([], 1) == {"items": [], "page": 1, "total_pages": 0, "has_next": False}
    for bad in ((items, 0), (items, -1), (items, 1, 0)):
        with pytest.raises(ValueError):
            paginate(*bad)


def test_merge_settings():
    defaults = {"db": {"host": "localhost", "pool": {"min": 1, "max": 5}}, "debug": False}
    snapshot = {"db": {"host": "localhost", "pool": {"min": 1, "max": 5}}, "debug": False}
    res = merge_settings(defaults, {"db": {"pool": {"max": 20}}, "debug": True})
    assert res == {"db": {"host": "localhost", "pool": {"min": 1, "max": 20}}, "debug": True}, "слияние на любую глубину"
    assert defaults == snapshot, "входные словари нельзя менять"
    res["db"]["host"] = "changed"
    assert defaults["db"]["host"] == "localhost", "результат не должен делить вложенные словари со входом"
    assert merge_settings({"a": {"x": 1}}, {"a": 5}) == {"a": 5}
    assert merge_settings({"a": 5}, {"a": {"x": 1}}) == {"a": {"x": 1}}
    assert merge_settings({"a": 1}) == {"a": 1}
    over = {"n": {"k": 1}}
    merge_settings({}, over)["n"]["k"] = 99
    assert over == {"n": {"k": 1}}


def test_parse_duration():
    assert parse_duration("1h30m15s") == 5415
    assert parse_duration("90s") == 90 and parse_duration("1h") == 3600 and parse_duration("15m") == 900
    assert parse_duration("10s2h") == 7210 and parse_duration("120m") == 7200
    for bad in ("", "abc", "10", "5x", "1h 30m", "h1", "1h30"):
        with pytest.raises(ValueError):
            parse_duration(bad)


def test_top_words():
    assert top_words("Go go  GO, python!", 2) == ["go", "python"]
    assert top_words("b a c a b", 3) == ["a", "b", "c"], "при равной частоте — по алфавиту"
    assert top_words("the cat and the hat\nthe end", 2, stop=frozenset({"the"})) == ["and", "cat"]
    assert top_words("  ... !!! ", 3) == [], "пустые слова не считаются"
    assert top_words("Один, один; ДВА: два два", 1) == ["два"]


def test_fetch_all():
    state = {"active": 0, "peak": 0, "calls": {}}

    async def fetch(url):
        state["calls"][url] = state["calls"].get(url, 0) + 1
        state["active"] += 1
        state["peak"] = max(state["peak"], state["active"])
        try:
            await asyncio.sleep(0.02)
            if url.startswith("flaky") and state["calls"][url] < 3:
                raise ConnectionError(url)
            if url.startswith("dead"):
                raise TimeoutError(url)
            return url.upper()
        finally:
            state["active"] -= 1

    urls = [f"u{i}" for i in range(12)] + ["flaky1", "dead1"]
    t0 = time.perf_counter()
    res = asyncio.run(asyncio.wait_for(fetch_all(urls, fetch, limit=4, retries=2, delay=0.01), 10))
    took = time.perf_counter() - t0
    assert res[:12] == [f"U{i}" for i in range(12)] and res[12] == "FLAKY1"
    assert isinstance(res[13], TimeoutError), "на месте упавшего URL — исключение"
    assert len(res) == len(urls)
    assert state["calls"]["u0"] == 1, "после успеха повторять не нужно"
    assert state["calls"]["dead1"] == 3, "попыток должно быть retries + 1"
    assert state["peak"] <= 4 and state["peak"] >= 3, f"одновременно {state['peak']}, лимит 4"
    assert took < 0.4, f"{took:.2f} c — похоже, запросы идут последовательно"
