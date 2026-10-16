# Урок 3.3. Контекстные менеджеры и исключения
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 33
import time
from contextlib import contextmanager  # noqa: F401


class Timer:
    """with Timer() as t: ...  →  t.elapsed (секунды). До выхода из блока elapsed = None."""

    def __init__(self, clock=time.perf_counter):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError


class Suppress:
    """Свой contextlib.suppress: with Suppress(KeyError, ValueError): ..."""

    def __init__(self, *exc_types):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError


def temp_attr(obj, name, value):
    """Контекстный менеджер (через @contextmanager): временно obj.name = value,
    на выходе — вернуть старое значение или удалить атрибут, если его не было."""
    raise NotImplementedError


class ConfigError(Exception):
    """Ошибка в конфиге."""


def parse_config(text: str) -> dict[str, int]:
    """Строки «ключ = целое». Пустые строки и строки, начинающиеся с #, пропускать.

    Ошибка → ConfigError(f"строка {n}: ...") ; для нечислового значения — с `from` исходной ValueError.

    >>> parse_config("a = 1\\n# комментарий\\n\\nb=20")
    {'a': 1, 'b': 20}
    """
    raise NotImplementedError


class Transaction:
    """★ with Transaction(d) as data: ... — при исключении вернуть d в состояние до входа."""

    def __init__(self, data: dict):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError
