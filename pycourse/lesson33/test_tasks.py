# Проверяющая система урока 3.3 — не меняй этот файл.
import inspect

import pytest

import tasks
from tasks import ConfigError, Suppress, Timer, Transaction, parse_config, temp_attr


class Clock:
    def __init__(self, *ticks):
        self.ticks = list(ticks)

    def __call__(self):
        return self.ticks.pop(0)


def test_timer():
    with Timer(Clock(10.0, 12.5)) as t:
        assert t.elapsed is None
    assert t.elapsed == pytest.approx(2.5)
    t2 = Timer(Clock(1.0, 4.0))
    with pytest.raises(ZeroDivisionError):
        with t2:
            1 / 0
    assert t2.elapsed == pytest.approx(3.0), "elapsed нужен и при исключении"
    with Timer() as real:
        sum(range(1000))
    assert 0 <= real.elapsed < 1


def test_suppress():
    with Suppress(KeyError):
        {}["x"]
    with Suppress(LookupError):
        [][1]                               # IndexError — подкласс LookupError
    with Suppress(ValueError, TypeError):
        int("x")
    with pytest.raises(ZeroDivisionError):
        with Suppress(KeyError):
            1 / 0
    with Suppress(KeyError):
        pass                                # без исключения — без ошибок
    after = []
    with Suppress(KeyError):
        after.append(1)
        {}["k"]
        after.append(2)
    assert after == [1], "после исключения тело не продолжается"


def test_temp_attr():
    class Cfg:
        debug = False

    cfg = Cfg()
    cfg.level = 1
    with temp_attr(cfg, "level", 5):
        assert cfg.level == 5
    assert cfg.level == 1
    with pytest.raises(RuntimeError):
        with temp_attr(cfg, "level", 9):
            raise RuntimeError
    assert cfg.level == 1, "восстанови значение и при исключении"
    with temp_attr(cfg, "new", "x"):
        assert cfg.new == "x"
    assert not hasattr(cfg, "new"), "атрибута не было — удали его"
    with temp_attr(cfg, "debug", True):
        assert cfg.debug is True
    assert cfg.debug is False and "debug" not in vars(cfg), "атрибут класса не должен остаться в экземпляре"
    assert "@contextmanager" in inspect.getsource(tasks), "сделай через @contextmanager"


def test_parse_config():
    assert parse_config("a = 1\n# комментарий\n\nb=20") == {"a": 1, "b": 20}
    assert parse_config("") == {}
    assert parse_config("  x  =  -7  ") == {"x": -7}
    with pytest.raises(ConfigError, match="строка 2") as ei:
        parse_config("a=1\nb=два\nc=3")
    assert isinstance(ei.value.__cause__, ValueError), "нужна цепочка raise ... from e"
    with pytest.raises(ConfigError, match="строка 3"):
        parse_config("a=1\n\nбез равно")
    assert issubclass(ConfigError, Exception)


def test_transaction():
    acc = {"alice": 100, "bob": 50}
    ref = acc
    with Transaction(acc) as d:
        d["alice"] -= 30
        d["bob"] += 30
    assert acc == {"alice": 70, "bob": 80}
    with pytest.raises(ValueError):
        with Transaction(acc) as d:
            d["alice"] -= 500
            d["carol"] = 1
            raise ValueError("недостаточно средств")
    assert acc == {"alice": 70, "bob": 80}, "откат при исключении"
    assert acc is ref, "восстанавливай тот же объект словаря"
    with pytest.raises(KeyError):
        with Transaction(acc) as d:
            del d["bob"]
            d["zzz"]
    assert acc == {"alice": 70, "bob": 80}
