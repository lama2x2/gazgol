# Урок 3.1. Области видимости, замыкания и декораторы
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 31
import functools  # noqa: F401 — пригодится wraps
import time
from collections import deque  # noqa: F401


def make_counter():
    """Вернуть функцию, которая при каждом вызове возвращает 1, 2, 3, …

    >>> c = make_counter(); c(), c(), c()
    (1, 2, 3)
    """
    raise NotImplementedError


def call_count(func):
    """Декоратор: считает вызовы в атрибуте wrapper.calls, сохраняет __name__ и __doc__.

    >>> @call_count
    ... def f(x): return x
    >>> f(1); f(2); f.calls
    2
    """
    raise NotImplementedError


def memoize(func):
    """Декоратор-кэш без lru_cache. Кэш доступен как wrapper.cache (dict).

    Ключ учитывает позиционные и именованные аргументы; порядок kwargs не важен.
    """
    raise NotImplementedError


def retry(times, exceptions=(Exception,), delay=0, sleep=time.sleep):
    """Декоратор с параметрами: до `times` попыток вызвать функцию.

    - исключение из `exceptions` → sleep(delay) и новая попытка (после последней не спать);
    - другие исключения пробрасываются сразу;
    - если все попытки провалились — пробросить последнее исключение.
    """
    raise NotImplementedError


class RateLimitExceeded(Exception):
    """Слишком много вызовов."""


def rate_limit(max_calls, period, clock=time.monotonic):
    """★ Декоратор: не больше max_calls успешных вызовов за любые period секунд
    (скользящее окно). Лишний вызов → RateLimitExceeded, функция не вызывается.
    """
    raise NotImplementedError
