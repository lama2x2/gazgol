# Урок 8.1. Стек, очередь и монотонный стек
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 81
from collections import deque  # noqa: F401


def is_valid_brackets(s: str) -> bool:
    """Правильная скобочная последовательность из ()[]{}; другие символы игнорировать.

    >>> is_valid_brackets("f(a[1]) {x}"), is_valid_brackets("([)]")
    (True, False)
    """
    raise NotImplementedError


def broken_keyboard(s: str) -> str:
    """b стирает последнюю набранную строчную букву, B — последнюю заглавную; сами b/B не печатаются.

    >>> broken_keyboard("aXbY"), broken_keyboard("ACcBd")
    ('XY', 'Acd')
    """
    raise NotImplementedError


def daily_temperatures(t: list[int]) -> list[int]:
    """Для каждого дня — через сколько дней станет строго теплее (или 0).

    >>> daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73])
    [1, 1, 4, 2, 1, 1, 0, 0]
    """
    raise NotImplementedError


class MinStack:
    """push(x), pop() → x, top() → x, get_min() → минимум; всё за O(1)."""

    def __init__(self):
        raise NotImplementedError

    def push(self, x) -> None:
        raise NotImplementedError

    def pop(self):
        raise NotImplementedError

    def top(self):
        raise NotImplementedError

    def get_min(self):
        raise NotImplementedError


def decode_string(s: str) -> str:
    """★ "3[a2[c]]" → "accaccacc", "2[ab]x" → "ababx".

    >>> decode_string("3[a2[c]]"), decode_string("10[z]")
    ('accaccacc', 'zzzzzzzzzz')
    """
    raise NotImplementedError
