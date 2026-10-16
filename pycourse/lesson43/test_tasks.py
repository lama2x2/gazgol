# Проверяющая система урока 4.3 — не меняй этот файл.
import ast
import gc
import inspect
from datetime import datetime

import pytest

import tasks
from tasks import DISCOUNTS, EventBus, Item, OrderService, calculate_total, register_discount


def test_discounts():
    assert calculate_total([1000, 500]) == 1500
    assert calculate_total([1000, 500], "black_friday") == 1050
    assert calculate_total([3000, 3000], "loyal") == 5500
    assert calculate_total([3000], "loyal") == 3000
    assert calculate_total([], "black_friday") == 0
    with pytest.raises(ValueError):
        calculate_total([1], "nope")

    @register_discount("half")
    def half(s):
        return s / 2

    assert half(10) == 5, "декоратор возвращает функцию без изменений"
    assert DISCOUNTS["half"] is half
    assert calculate_total([3, 4], "half") == 3.5, "новая скидка подключается без правки calculate_total"
    assert calculate_total([0.1, 0.2]) == 0.3
    del DISCOUNTS["half"]
    tree = ast.parse(inspect.getsource(tasks.calculate_total))
    compares = [n for n in ast.walk(tree) if isinstance(n, ast.Compare)
                and any(isinstance(c, ast.Constant) and c.value in ("black_friday", "loyal") for c in n.comparators)]
    assert not compares, "без if/elif по названиям скидок"


class FakeRepo:
    def __init__(self, fail=False):
        self.saved, self.fail = [], fail

    def save(self, order):
        if self.fail:
            raise ConnectionError("БД недоступна")
        self.saved.append(order)
        return 100 + len(self.saved)


class FakeNotifier:
    def __init__(self):
        self.sent = []

    def send(self, user_id, text):
        self.sent.append((user_id, text))


def test_order_service():
    repo, notifier = FakeRepo(), FakeNotifier()
    now = datetime(2026, 10, 14, 12, 0)
    svc = OrderService(repo, notifier, clock=lambda: now)
    oid = svc.place(7, [Item("a", 2, 100.0), Item("b", 1, 50.5)])
    assert oid == 101
    order = repo.saved[0]
    assert order.user_id == 7 and order.total == 250.5 and order.created_at == now and len(order.items) == 2
    assert notifier.sent == [(7, "Заказ 101 на 250.5 принят")]
    with pytest.raises(ValueError):
        svc.place(7, [])
    bad = OrderService(FakeRepo(fail=True), notifier, clock=lambda: now)
    with pytest.raises(ConnectionError):
        bad.place(1, [Item("x", 1, 1.0)])
    assert len(notifier.sent) == 1, "если сохранение упало — уведомлять нельзя"
    src = inspect.getsource(tasks.OrderService)
    assert "FakeRepo" not in src and "datetime.now()" not in src, "зависимости — только через конструктор"


def test_event_bus():
    bus = EventBus()
    log = []

    def on_order(x):
        log.append(("f", x))

    class Mailer:
        def on_order(self, x):
            log.append(("m", x))

    m = Mailer()
    bus.subscribe("order", on_order)
    bus.subscribe("order", m.on_order)
    assert bus.publish("order", 1) == 2
    assert log == [("f", 1), ("m", 1)]
    assert bus.publish("unknown") == 0
    del m
    gc.collect()
    log.clear()
    assert bus.publish("order", 2) == 1, "удалённый объект-подписчик должен исчезнуть из шины"
    assert log == [("f", 2)]
    bus.unsubscribe("order", on_order)
    assert bus.publish("order", 3) == 0

    m2 = Mailer()
    bus.subscribe("order", m2.on_order)
    bus.unsubscribe("order", m2.on_order)
    assert bus.publish("order", 4) == 0, "unsubscribe связанного метода"


def test_event_bus__errors():
    bus = EventBus()
    got = []

    def bad(x):
        raise ValueError("сломался")

    def good(x):
        got.append(x)

    def bad2(x):
        raise KeyError("тоже")

    for cb in (bad, good, bad2):
        bus.subscribe("e", cb)
    with pytest.raises(ExceptionGroup) as ei:
        bus.publish("e", 5)
    assert got == [5], "ошибка одного подписчика не мешает остальным"
    assert sorted(type(e).__name__ for e in ei.value.exceptions) == ["KeyError", "ValueError"]
