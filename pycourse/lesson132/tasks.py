# Урок 13.2. WSGI, ASGI, Django и FastAPI
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 132
import inspect  # noqa: F401
import json  # noqa: F401
import time
import uuid  # noqa: F401
from urllib.parse import parse_qs  # noqa: F401


def app(environ, start_response):
    """WSGI-приложение (ответы — JSON):
    GET  /health            → 200 {"status": "ok"}
    GET  /hello?name=Ann    → 200 {"hello": "Ann"}   (без name — "world")
    POST /echo  (JSON-тело) → 200 то же JSON; битый JSON → 400 {"error": "bad json"}
    другой метод на известном пути → 405 {"error": "method not allowed"} + заголовок Allow
    неизвестный путь        → 404 {"error": "not found"}
    """
    raise NotImplementedError


def timing_middleware(inner, clock=time.perf_counter):
    """WSGI-middleware: заголовки X-Request-ID (из запроса или uuid4().hex) и X-Response-Time-ms (целое);
    request_id кладётся в environ["request_id"]."""
    raise NotImplementedError


class Depends:
    """Маркер зависимости: def handler(db=Depends(get_db)): ..."""

    def __init__(self, dependency):
        self.dependency = dependency


def solve(func, overrides=None):
    """Вызвать func, вычислив все Depends рекурсивно; одна зависимость — один раз за вызов;
    зависимости-генераторы закрыть после func в обратном порядке, даже при исключении."""
    raise NotImplementedError


async def asgi_app(scope, receive, send):
    """★ ASGI: GET /health → {"status": "ok"}; POST /echo → тело как есть (JSON), 404 иначе.
    Обработай lifespan (startup/shutdown)."""
    raise NotImplementedError
