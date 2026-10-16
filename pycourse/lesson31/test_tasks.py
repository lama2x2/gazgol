# Проверяющая система урока 3.1 — не меняй этот файл.
import inspect

import pytest

import tasks
from tasks import RateLimitExceeded, call_count, make_counter, memoize, rate_limit, retry


def test_make_counter():
    a, b = make_counter(), make_counter()
    assert [a(), a(), a()] == [1, 2, 3]
    assert b() == 1, "счётчики должны быть независимыми"
    assert a() == 4
    assert a.__closure__, "состояние должно жить в замыкании"
    assert "global" not in inspect.getsource(tasks.make_counter)


def test_call_count():
    @call_count
    def add(a, b=0):
        """Складывает."""
        return a + b

    assert add.calls == 0
    assert add(1, b=2) == 3, "обёртка должна возвращать результат и передавать kwargs"
    assert add(5) == 5
    assert add.calls == 2
    assert add.__name__ == "add" and add.__doc__ == "Складывает.", "нужен functools.wraps"

    @call_count
    def boom():
        raise ValueError

    with pytest.raises(ValueError):
        boom()
    assert boom.calls == 1, "вызов с исключением — тоже вызов"
    assert add.calls == 2, "у каждой функции свой счётчик"


def test_memoize():
    calls = []

    @memoize
    def f(a, b=1, *, c=0):
        calls.append((a, b, c))
        return a * b + c

    assert f(2, 3) == 6 and f(2, 3) == 6
    assert len(calls) == 1
    assert f(2, b=3, c=1) == 7 and f(2, c=1, b=3) == 7
    assert len(calls) == 2, "порядок именованных аргументов не должен влиять на ключ"
    assert f(3) == 3 and len(calls) == 3
    assert isinstance(f.cache, dict) and len(f.cache) >= 3
    assert f.__name__ == "f"

    @memoize
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(300) == 222232244629420445529739893461909967206666939096499764990979600


def test_retry():
    sleeps = []
    attempts = []

    @retry(3, exceptions=(ConnectionError,), delay=0.5, sleep=sleeps.append)
    def flaky(n):
        attempts.append(n)
        if len(attempts) < 3:
            raise ConnectionError("нет связи")
        return "ok"

    assert flaky(7) == "ok"
    assert attempts == [7, 7, 7] and sleeps == [0.5, 0.5]

    attempts.clear(); sleeps.clear()

    @retry(2, exceptions=(ConnectionError,), sleep=sleeps.append)
    def always():
        attempts.append(1)
        raise ConnectionError(f"попытка {len(attempts)}")

    with pytest.raises(ConnectionError, match="попытка 2"):
        always()
    assert len(attempts) == 2 and sleeps == [0], "после последней попытки спать не нужно"

    attempts.clear(); sleeps.clear()

    @retry(5, exceptions=(ConnectionError,), sleep=sleeps.append)
    def wrong():
        attempts.append(1)
        raise KeyError("x")

    with pytest.raises(KeyError):
        wrong()
    assert len(attempts) == 1 and sleeps == [], "чужие исключения — без повторов"

    @retry(1, sleep=sleeps.append)
    def named():
        """док"""
        return 1

    assert named() == 1 and named.__name__ == "named" and named.__doc__ == "док"


class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


def test_rate_limit():
    clock = FakeClock()
    calls = []

    @rate_limit(3, 10, clock=clock)
    def ping(x):
        calls.append(x)
        return x

    assert [ping(1), ping(2), ping(3)] == [1, 2, 3]
    with pytest.raises(RateLimitExceeded):
        ping(4)
    assert calls == [1, 2, 3], "при превышении функция не вызывается"
    clock.t += 9.9
    with pytest.raises(RateLimitExceeded):
        ping(5)
    clock.t += 0.2  # 10.1 c после первых вызовов — окно освободилось
    assert ping(6) == 6
    assert ping.__name__ == "ping"


def test_rate_limit__window_edge():
    """Фиксированное окно пропустило бы 2×max_calls на стыке — скользящее нет."""
    clock = FakeClock()
    clock.t = 9.0

    @rate_limit(2, 10, clock=clock)
    def f():
        return True

    assert f() and f()          # t=9: два вызова
    clock.t = 10.5              # новая «десятка» — но в последние 10 с уже 2 вызова
    with pytest.raises(RateLimitExceeded):
        f()
    clock.t = 19.5              # вызовы в t=9 вышли из окна: 9 < 19.5 - 10
    assert f() and f()
    with pytest.raises(RateLimitExceeded):
        f()


def test_rate_limit__rejected_not_counted():
    clock = FakeClock()

    @rate_limit(1, 5, clock=clock)
    def f():
        return 1

    f()
    for _ in range(10):
        clock.t += 0.4
        with pytest.raises(RateLimitExceeded):
            f()
    clock.t += 1.1  # прошло 5.1 c с успешного вызова
    assert f() == 1, "отклонённые вызовы не должны продлевать окно"
