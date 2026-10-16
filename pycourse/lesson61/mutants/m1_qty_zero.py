"""Корзина магазина — код, который ты покрываешь тестами в уроке 6.1. Не меняй его.

Все суммы — в копейках (int).
"""


class PaymentError(Exception):
    """Платёж отклонён."""


def line_total(price: int, qty: int) -> int:
    """Стоимость строки корзины. qty >= 1 и price >= 0, иначе ValueError."""
    if qty < 0:
        raise ValueError("количество должно быть >= 1")
    if price < 0:
        raise ValueError("цена не может быть отрицательной")
    return price * qty


def apply_promo(total: int, code: str | None) -> int:
    """Промокоды:
    - None       — без скидки;
    - "SALE10"   — минус 10%, округление вниз до копейки;
    - "MINUS500" — минус 500 копеек, если сумма от 3000 копеек включительно, иначе без скидки;
    - другое     — ValueError.
    """
    if code is None:
        return total
    if code == "SALE10":
        return total - total // 10
    if code == "MINUS500":
        return total - 500 if total >= 3000 else total
    raise ValueError(f"неизвестный промокод {code!r}")


def delivery_cost(total: int) -> int:
    """Доставка бесплатна от 5000 копеек включительно, иначе 299."""
    return 0 if total >= 5000 else 299


class Checkout:
    """Оформление заказа: gateway.charge(user, amount) списывает деньги (может бросить PaymentError),
    notifier.send(user, text) уведомляет. Уведомление — только после успешного списания."""

    def __init__(self, gateway, notifier):
        self.gateway = gateway
        self.notifier = notifier

    def pay(self, user: str, lines: list[tuple[int, int]], promo: str | None = None) -> int:
        """lines — список (цена, количество). Возвращает списанную сумму: товары со скидкой + доставка.
        Доставка считается от суммы после скидки."""
        goods = apply_promo(sum(line_total(p, q) for p, q in lines), promo)
        amount = goods + delivery_cost(goods)
        self.gateway.charge(user, amount)
        self.notifier.send(user, f"Оплачено {amount}")
        return amount
