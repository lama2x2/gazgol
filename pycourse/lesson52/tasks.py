# Урок 5.2. Потоки и процессы
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 52
import itertools
import queue  # noqa: F401
import threading  # noqa: F401
from collections import deque  # noqa: F401
from concurrent.futures import ProcessPoolExecutor  # noqa: F401 — только для parallel_sum_squares


class ThreadSafeCounter:
    """increment(n=1) из многих потоков; value — текущее значение."""

    def __init__(self):
        raise NotImplementedError

    def increment(self, n: int = 1) -> None:
        raise NotImplementedError

    @property
    def value(self) -> int:
        raise NotImplementedError


def parallel_map(func, items, workers=4):
    """Результаты func(x) в исходном порядке; не больше `workers` потоков; без concurrent.futures.
    Если какой-то вызов упал — после завершения всех потоков пробросить первое исключение."""
    raise NotImplementedError


class BoundedBuffer:
    """Очередь ёмкости capacity на threading.Condition (без queue.Queue).

    put(x, timeout=None) ждёт места, get(timeout=None) ждёт элемента; не дождались — TimeoutError.
    """

    def __init__(self, capacity: int):
        raise NotImplementedError

    def put(self, item, timeout=None) -> None:
        raise NotImplementedError

    def get(self, timeout=None):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError


_ids = itertools.count()


class Account:
    def __init__(self, balance: int):
        self.id = next(_ids)
        self.balance = balance
        self.lock = threading.Lock()


def transfer(a: Account, b: Account, amount: int) -> None:
    """★ Перевести amount с a на b из многих потоков без deadlock.
    Недостаточно средств или a is b — ValueError."""
    raise NotImplementedError


def parallel_sum_squares(n: int, workers: int = 4) -> int:
    """sum(i * i for i in range(n)), посчитанная частями в ProcessPoolExecutor."""
    raise NotImplementedError
