# Проверяющая система урока 4.2 — не меняй этот файл.
import threading
import time

import pytest

from tasks import Plugin, Positive, SingletonMeta, cached_prop


def test_positive():
    class Order:
        qty = Positive()
        price = Positive()

        def __init__(self, qty, price):
            self.qty, self.price = qty, price

    a, b = Order(2, 9.5), Order(5, 1)
    assert (a.qty, a.price, b.qty, b.price) == (2, 9.5, 5, 1), "значения должны храниться в каждом экземпляре отдельно"
    with pytest.raises(ValueError):
        a.qty = 0
    with pytest.raises(ValueError):
        Order(-1, 1)
    with pytest.raises(TypeError):
        a.price = "10"
    with pytest.raises(TypeError):
        a.qty = True
    assert a.qty == 2, "неудачное присваивание не меняет значение"
    assert isinstance(Order.qty, Positive), "доступ через класс возвращает сам дескриптор"
    assert vars(a) == {"qty": 2, "price": 9.5}, "храни значение в obj.__dict__ под именем поля"


def test_cached_prop():
    calls = []

    class Report:
        def __init__(self, rows):
            self.rows = rows

        @cached_prop
        def total(self):
            """Сумма."""
            calls.append(1)
            return sum(self.rows)

    r = Report([1, 2, 3])
    assert r.total == 6 and r.total == 6 and len(calls) == 1, "вычислять один раз"
    assert vars(r)["total"] == 6, "результат кладётся в __dict__ экземпляра"
    r2 = Report([10])
    assert r2.total == 10 and len(calls) == 2, "кэш — у каждого экземпляра свой"
    del r.total
    r.rows.append(4)
    assert r.total == 10 and len(calls) == 3, "del сбрасывает кэш"
    assert isinstance(Report.total, cached_prop)
    assert not hasattr(cached_prop, "__set__"), "должен быть non-data-дескриптором"
    r.total = 99
    assert r.total == 99


def test_plugin():
    Plugin.registry.clear()

    class Csv(Plugin, name="csv"):
        def __init__(self, sep=","):
            self.sep = sep

    class JsonExport(Plugin):
        pass

    assert Plugin.registry == {"csv": Csv, "jsonexport": JsonExport}
    p = Plugin.create("csv", ";")
    assert isinstance(p, Csv) and p.sep == ";"
    with pytest.raises(KeyError):
        Plugin.create("xml")
    with pytest.raises(ValueError):
        class Dup(Plugin, name="csv"):
            pass

    class Sub(Csv, name="tsv"):
        pass

    assert Plugin.registry["tsv"] is Sub and "registry" not in vars(Csv), "реестр — один, на Plugin"


def test_singleton():
    inits = []

    class Config(metaclass=SingletonMeta):
        def __init__(self, env="dev"):
            inits.append(env)
            self.env = env

    class Cache(metaclass=SingletonMeta):
        pass

    a = Config("prod")
    b = Config("test")
    assert a is b and a.env == "prod" and inits == ["prod"], "__init__ — один раз"
    assert Cache() is Cache() and Cache() is not a

    class Slow(metaclass=SingletonMeta):
        def __init__(self):
            time.sleep(0.05)

    got = []
    ts = [threading.Thread(target=lambda: got.append(Slow())) for _ in range(20)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert len({id(x) for x in got}) == 1, "из разных потоков должен получиться один экземпляр — нужна блокировка"
