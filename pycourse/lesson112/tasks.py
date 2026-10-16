# Урок 11.2. Бизнес-логика: банкомат, уведомления, бронирование
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 112
import bisect  # noqa: F401
import itertools  # noqa: F401
import time
from dataclasses import dataclass
from enum import Enum

# ---------------------------------------------------------------- статусы заказа


class Status(Enum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class InvalidTransition(Exception):
    pass


class OrderFSM:
    """status, history: list[(old, new)], can(new) -> bool, move(new).
    Переходы: CREATED → PAID | CANCELLED; PAID → SHIPPED | CANCELLED; SHIPPED → DELIVERED."""

    def __init__(self):
        raise NotImplementedError


# ---------------------------------------------------------------- уведомления


class Channel(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


@dataclass(frozen=True)
class Notification:
    id: int
    channel: Channel
    recipient: str
    sender: str
    text: str


class NotificationFilter:
    """set_prefs(user, channels=None, blocked=()), should_send(n) -> bool.

    Правила: канал разрешён получателем; отправитель не заблокирован;
    такое же (recipient, channel, text) не отправлялось за последние 24 часа."""

    def __init__(self, clock=time.time):
        raise NotImplementedError


# ---------------------------------------------------------------- переговорки


class RoomBusy(Exception):
    pass


class RoomBooking:
    """book(room, start, end) -> booking_id, cancel(booking_id), free_rooms(start, end) -> list.
    Интервалы полуоткрытые [start, end)."""

    def __init__(self, rooms: list[str]):
        raise NotImplementedError


# ---------------------------------------------------------------- банкомат


class CannotDispense(Exception):
    pass


class ATM:
    """★ ATM({5000: 2, 1000: 10, ...}); withdraw(amount) -> {номинал: штук} минимальным числом купюр;
    deposit({номинал: штук}); balance -> int. Невозможно — CannotDispense, состояние не меняется."""

    def __init__(self, cassettes: dict[int, int]):
        raise NotImplementedError
