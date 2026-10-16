# Урок 11.1. Задачи «как в продакшене»
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 111
import math  # noqa: F401
import time
from collections import OrderedDict, defaultdict  # noqa: F401


class LRUCache:
    """get(key, default=None), put(key, value); не больше capacity ключей, вытесняется давно не использованный."""

    def __init__(self, capacity: int):
        raise NotImplementedError

    def get(self, key, default=None):
        raise NotImplementedError

    def put(self, key, value) -> None:
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError


class TTLCache:
    """set(key, value), get(key, default=None), delete(key), len() — только живые записи."""

    def __init__(self, ttl: float, clock=time.monotonic):
        raise NotImplementedError

    def set(self, key, value) -> None:
        raise NotImplementedError

    def get(self, key, default=None):
        raise NotImplementedError

    def delete(self, key) -> None:
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError


def sync_diff(db: dict, api: dict) -> tuple[list, list, list]:
    """(create, update, delete) — отсортированные списки id.

    >>> sync_diff({1: "a", 2: "b"}, {2: "B", 3: "c"})
    ([3], [2], [1])
    """
    raise NotImplementedError


def flatten_json(obj) -> dict:
    """{"a": {"b": [1, {"c": 2}]}} → {"a.b.0": 1, "a.b.1.c": 2}; пустые {} и [] — как значения."""
    raise NotImplementedError


def endpoint_stats(lines) -> dict:
    """★ {(метод, путь): (запросов, доля_5xx_до_3_знаков, p95_мс)} по строкам
    "2026-10-14T10:00:00 GET /api/users?page=2 200 12ms". p95 — nearest-rank."""
    raise NotImplementedError
