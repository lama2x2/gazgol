# Урок 14.2. System design и поведенческое интервью
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 142
import string
import threading  # noqa: F401
import time
from urllib.parse import urlsplit  # noqa: F401

ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase   # 0-9a-zA-Z


def base62_encode(n: int) -> str:
    """>>> base62_encode(0), base62_encode(61), base62_encode(62)
    ('0', 'Z', '10')
    """
    raise NotImplementedError


def base62_decode(s: str) -> int:
    """>>> base62_decode("10")
    62
    """
    raise NotImplementedError


class ClockMovedBackwards(Exception):
    pass


class Snowflake:
    """next_id() -> int: 41 бит миллисекунд от epoch | 10 бит узла | 12 бит счётчика."""

    EPOCH_MS = 1_767_225_600_000          # 2026-01-01 UTC

    def __init__(self, node: int, clock=lambda: int(time.time() * 1000)):
        raise NotImplementedError

    def next_id(self) -> int:
        raise NotImplementedError


class UrlShortener:
    """★ shorten(url, alias=None, ttl=None) -> code; resolve(code) -> url (+1 переход); stats(code) -> переходы."""

    def __init__(self, clock=time.monotonic):
        raise NotImplementedError

    def shorten(self, url: str, alias: str | None = None, ttl: float | None = None) -> str:
        raise NotImplementedError

    def resolve(self, code: str) -> str:
        raise NotImplementedError

    def stats(self, code: str) -> int:
        raise NotImplementedError
