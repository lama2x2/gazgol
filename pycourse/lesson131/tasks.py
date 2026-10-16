# Урок 13.1. HTTP, REST и сеть
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 131
import base64  # noqa: F401
import hashlib  # noqa: F401
import hmac  # noqa: F401
import json  # noqa: F401
import re  # noqa: F401
import time
from dataclasses import dataclass
from urllib.parse import parse_qs, urlsplit  # noqa: F401


@dataclass
class Request:
    method: str
    path: str
    query: dict[str, list[str]]
    headers: dict[str, str]          # ключи в нижнем регистре
    body: bytes


def parse_request(raw: bytes) -> Request:
    """Разобрать HTTP/1.1-запрос. Битый запрос — ValueError.

    >>> r = parse_request(b"GET /a?x=1&x=2 HTTP/1.1\\r\\nHost: h:80\\r\\n\\r\\n"); r.path, r.query, r.headers
    ('/a', {'x': ['1', '2']}, {'host': 'h:80'})
    """
    raise NotImplementedError


class NotFound(Exception):
    pass


class MethodNotAllowed(Exception):
    def __init__(self, allowed: set[str]):
        super().__init__(f"разрешены: {sorted(allowed)}")
        self.allowed = allowed


class Router:
    """add(method, "/users/{id:int}/orders/{name}", handler); resolve(method, path) → (handler, params)."""

    def __init__(self):
        raise NotImplementedError

    def add(self, method: str, pattern: str, handler) -> None:
        raise NotImplementedError

    def resolve(self, method: str, path: str):
        raise NotImplementedError


class IdempotencyConflict(Exception):
    pass


class IdempotencyStore:
    """run(key, body: bytes, handler) → ответ handler(); повтор с тем же ключом и телом — сохранённый ответ."""

    def __init__(self, ttl: float = 86_400, clock=time.monotonic):
        raise NotImplementedError

    def run(self, key: str, body: bytes, handler):
        raise NotImplementedError


class InvalidToken(Exception):
    pass


class TokenExpired(InvalidToken):
    pass


def jwt_encode(payload: dict, secret: bytes) -> str:
    """★ JWT HS256: base64url(header).base64url(payload).base64url(подпись), без '='."""
    raise NotImplementedError


def jwt_decode(token: str, secret: bytes, now: float | None = None) -> dict:
    """★ Проверить подпись и exp (если есть), вернуть payload. now — текущее время (по умолчанию time.time())."""
    raise NotImplementedError
