# Урок 4.1. Классы и магические методы
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 41
import functools  # noqa: F401 — total_ordering


class Version:
    """Версия «1.10.2». Version.from_string("1.10.2") == Version(1, 10, 2).

    Сравнение по числам, хвостовые нули не важны: Version(1, 2) == Version(1, 2, 0).
    repr → Version('1.10.2'), str → 1.10.2
    """

    def __init__(self, *parts: int):
        raise NotImplementedError


class Money:
    """Деньги: Money(1050, "RUB") — это 10.50 RUB. Неизменяемы по смыслу.

    + с той же валютой; с другой — ValueError; sum([...]) работает; сравнение и хеш по (currency, cents).
    """

    def __init__(self, cents: int, currency: str):
        raise NotImplementedError


class Vector:
    """Vector(1, 2, 3): len, v[i], v[1:], abs(v), v * 2, 2 * v, v @ w, ==, repr → Vector(1, 2, 3)."""

    def __init__(self, *components):
        raise NotImplementedError


class HashMap:
    """★ Хеш-таблица без dict и set: m[k] = v, m[k], del m[k], k in m, len(m), m.get(k, default), for k in m."""

    def __init__(self):
        raise NotImplementedError
