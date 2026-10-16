# Проверяющая система урока 11.2 — не меняй этот файл.
import itertools
import random
import time

import pytest

from tasks import (ATM, CannotDispense, Channel, InvalidTransition, Notification, NotificationFilter, OrderFSM,
                   RoomBooking, RoomBusy, Status)

rnd = random.Random(112)


def test_order_fsm():
    o = OrderFSM()
    assert o.status is Status.CREATED and o.history == []
    assert o.can(Status.PAID) and not o.can(Status.DELIVERED)
    o.move(Status.PAID)
    o.move(Status.SHIPPED)
    with pytest.raises(InvalidTransition):
        o.move(Status.CANCELLED)
    assert o.status is Status.SHIPPED, "при ошибке статус не меняется"
    o.move(Status.DELIVERED)
    assert o.history == [(Status.CREATED, Status.PAID), (Status.PAID, Status.SHIPPED), (Status.SHIPPED, Status.DELIVERED)]
    for s in Status:
        assert not o.can(s), "из DELIVERED никуда"
    c = OrderFSM()
    c.move(Status.CANCELLED)
    with pytest.raises(InvalidTransition):
        c.move(Status.PAID)


class Clock:
    def __init__(self):
        self.t = 1_000_000.0

    def __call__(self):
        return self.t


def N(i, ch=Channel.EMAIL, to="ann", frm="shop", text="скидка"):
    return Notification(i, ch, to, frm, text)


def test_notification_filter():
    clk = Clock()
    f = NotificationFilter(clock=clk)
    assert f.should_send(N(1)) is True, "по умолчанию всё разрешено"
    assert f.should_send(N(2)) is False, "дубликат в течение 24 часов"
    assert f.should_send(N(3, text="другой текст")) is True
    assert f.should_send(N(4, ch=Channel.SMS)) is True, "другой канал — не дубликат"
    f.set_prefs("ann", channels={Channel.PUSH}, blocked={"spam"})
    assert f.should_send(N(5, ch=Channel.EMAIL, text="новое")) is False, "канал запрещён"
    assert f.should_send(N(6, ch=Channel.PUSH, frm="spam")) is False, "отправитель заблокирован"
    assert f.should_send(N(7, ch=Channel.PUSH)) is True
    assert f.should_send(N(8, to="bob", ch=Channel.EMAIL)) is True, "настройки — у каждого свои"
    clk.t += 86_399
    assert f.should_send(N(9, ch=Channel.PUSH)) is False
    clk.t += 2
    assert f.should_send(N(10, ch=Channel.PUSH)) is True, "через 24 часа можно снова"
    g = NotificationFilter(clock=clk)
    g.set_prefs("ann", channels={Channel.SMS})
    assert g.should_send(N(11)) is False                # отклонено: EMAIL запрещён
    g.set_prefs("ann", channels=None)
    assert g.should_send(N(12)) is True, "отклонённое уведомление не попадает в окно дедупликации"


def test_room_booking():
    rb = RoomBooking(["A", "B"])
    b1 = rb.book("A", 9, 10)
    rb.book("A", 10, 11)
    with pytest.raises(RoomBusy):
        rb.book("A", 9.5, 10.5)
    with pytest.raises(RoomBusy):
        rb.book("A", 8, 12)
    with pytest.raises(ValueError):
        rb.book("C", 1, 2)
    with pytest.raises(ValueError):
        rb.book("A", 5, 5)
    assert rb.free_rooms(9, 11) == ["B"] and rb.free_rooms(11, 12) == ["A", "B"]
    rb.cancel(b1)
    assert rb.free_rooms(9, 10) == ["A", "B"]
    rb.book("A", 9, 10)
    for _ in range(300):
        rb2, ref = RoomBooking(["X"]), []
        for _ in range(10):
            s = rnd.randint(0, 20)
            e = s + rnd.randint(1, 5)
            clash = any(a < e and s < b for a, b in ref)
            if clash:
                with pytest.raises(RoomBusy):
                    rb2.book("X", s, e)
            else:
                rb2.book("X", s, e)
                ref.append((s, e))
    big = RoomBooking(["R"])
    t0 = time.perf_counter()
    order = list(range(20_000))
    rnd.shuffle(order)
    for i in order:
        big.book("R", i * 2, i * 2 + 1)
    assert time.perf_counter() - t0 < 2, "проверяй только соседей через bisect"


def _best(cass, amount):
    noms = sorted(cass)
    best = None
    for combo in itertools.product(*[range(cass[d] + 1) for d in noms]):
        if sum(c * d for c, d in zip(combo, noms)) == amount:
            if best is None or sum(combo) < sum(best):
                best = combo
    return None if best is None else sum(best)


def test_atm():
    a = ATM({50: 1, 20: 3})
    assert a.withdraw(60) == {20: 3}, "жадный алгоритм взял бы 50 и застрял"
    assert a.balance == 50
    with pytest.raises(CannotDispense):
        a.withdraw(30)
    assert a.balance == 50, "при отказе кассеты не меняются"
    a.deposit({100: 2})
    assert a.withdraw(250) == {100: 2, 50: 1} and a.balance == 0
    with pytest.raises(CannotDispense):
        a.withdraw(10)
    b = ATM({5000: 2, 2000: 3, 1000: 10, 500: 4, 100: 20})
    assert b.withdraw(7600) == {5000: 1, 2000: 1, 500: 1, 100: 1}
    for _ in range(200):
        cass = {d: rnd.randint(0, 3) for d in rnd.sample([10, 20, 50, 100, 200, 500], 3)}
        amount = rnd.choice([10, 20, 30, 40, 60, 70, 80, 120, 150, 240, 260, 310, 600])
        m = ATM(dict(cass))
        best = _best(cass, amount)
        if best is None:
            with pytest.raises(CannotDispense):
                m.withdraw(amount)
            assert m.balance == sum(d * c for d, c in cass.items())
        else:
            got = m.withdraw(amount)
            assert sum(d * c for d, c in got.items()) == amount and sum(got.values()) == best, f"{cass}, {amount}: {got}"
            assert all(c <= cass[d] for d, c in got.items()) and all(c > 0 for c in got.values())
    big = ATM({5000: 50, 2000: 50, 1000: 50, 500: 50, 200: 50, 100: 50, 50: 50})
    t0 = time.perf_counter()
    big.withdraw(123_450)
    assert time.perf_counter() - t0 < 2, "нужны отсечения"
