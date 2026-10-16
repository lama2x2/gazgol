# Урок 4.3. SOLID, паттерны и внедрение зависимостей
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 43
import inspect  # noqa: F401
import weakref  # noqa: F401
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Protocol

# ---------------------------------------------------------------- стратегии скидок

DISCOUNTS: dict[str, Callable[[float], float]] = {}


def register_discount(name: str):
    """Декоратор с параметром: зарегистрировать функцию-скидку (сумма → сумма со скидкой)."""
    raise NotImplementedError


# Зарегистрируй этими же декораторами две скидки:
#   "black_friday" — минус 30%;
#   "loyal"        — минус 500, если сумма больше 5000, иначе без скидки.


def calculate_total(prices: list[float], kind: str | None = None) -> float:
    """Сумма цен со скидкой kind (None — без скидки), округлённая до 2 знаков. Неизвестная скидка — ValueError."""
    raise NotImplementedError


# ---------------------------------------------------------------- сервис заказов


@dataclass
class Item:
    sku: str
    qty: int
    price: float


@dataclass
class Order:
    user_id: int
    items: list[Item]
    total: float
    created_at: datetime


class OrderRepo(Protocol):
    def save(self, order: Order) -> int: ...


class Notifier(Protocol):
    def send(self, user_id: int, text: str) -> None: ...


class OrderService:
    """place(user_id, items) → order_id. Зависимости — только через конструктор.

    Текст уведомления: f"Заказ {order_id} на {total} принят", total = сумма qty * price.
    """

    def __init__(self, repo: OrderRepo, notifier: Notifier, clock: Callable[[], datetime] = datetime.now):
        raise NotImplementedError

    def place(self, user_id: int, items: list[Item]) -> int:
        raise NotImplementedError


# ---------------------------------------------------------------- шина событий


class EventBus:
    """★ subscribe(event, callback), unsubscribe(event, callback), publish(event, *args).

    Связанные методы храним слабо (weakref.WeakMethod), функции — обычными ссылками.
    Ошибки подписчиков не прерывают рассылку: после неё — ExceptionGroup со всеми ошибками.
    """

    def subscribe(self, event: str, callback: Callable) -> None:
        raise NotImplementedError

    def unsubscribe(self, event: str, callback: Callable) -> None:
        raise NotImplementedError

    def publish(self, event: str, *args) -> int:
        """Разослать событие; вернуть, сколько подписчиков было вызвано."""
        raise NotImplementedError
