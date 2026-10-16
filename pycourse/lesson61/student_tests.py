# Урок 6.1. Типизация и тесты
#
# Здесь тесты пишешь ты. Код под тестом — cart.py (не меняй его).
# Проверяющая система подменяет cart.py «мутантами» — копиями с одной внесённой ошибкой —
# и запускает твои тесты. Хорошие тесты падают на каждом мутанте («убивают» его).
#
#     python3 pycourse/check.py 61
#
# Пиши обычные pytest-тесты: функции test_…, assert, pytest.raises, pytest.mark.parametrize.
# Для Checkout понадобятся тестовые двойники: unittest.mock.Mock или свои фейк-классы.
import pytest
from unittest.mock import Mock, call  # noqa: F401

from cart import Checkout, PaymentError, apply_promo, delivery_cost, line_total  # noqa: F401


def test_line_total_basic():
    assert line_total(250, 4) == 1000


# TODO: граничные случаи line_total (qty, price)
# TODO: каждый промокод, включая неизвестный и границу 3000
# TODO: доставка на границе 5000
# TODO: Checkout: сумма, уведомление, поведение при PaymentError
