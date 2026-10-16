# Урок 12.2. Индексы, транзакции, изоляция, блокировки
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 122
#
# Работаем с sqlite3 из стандартной библиотеки. Схема (создаётся в тестах):
#   accounts(id INTEGER PRIMARY KEY, balance INTEGER NOT NULL, version INTEGER NOT NULL DEFAULT 0)
#   users(id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE)
#   products(sku TEXT PRIMARY KEY, name TEXT NOT NULL, price INTEGER NOT NULL)
#   orders(id INTEGER PRIMARY KEY, user_id INTEGER, status TEXT, created_at TEXT, total INTEGER)
#
# `with conn:` в sqlite3 — транзакция: COMMIT при выходе, ROLLBACK при исключении.
import sqlite3


class InsufficientFunds(Exception):
    pass


class ConflictError(Exception):
    pass


def transfer(conn: sqlite3.Connection, src: int, dst: int, amount: int) -> None:
    """Перевести amount со счёта src на dst атомарно. Нет счёта — ValueError,
    не хватает денег — InsufficientFunds; при любой ошибке балансы не меняются."""
    raise NotImplementedError


def get_or_create_user(conn: sqlite3.Connection, email: str) -> tuple[int, bool]:
    """(id, created). Email нормализуется: strip() и lower()."""
    raise NotImplementedError


def upsert_products(conn: sqlite3.Connection, rows: list[tuple[str, str, int]]) -> None:
    """Пакетно вставить или обновить (sku, name, price) по sku."""
    raise NotImplementedError


def withdraw_optimistic(conn: sqlite3.Connection, account_id: int, amount: int,
                        attempts: int = 3, before_write=lambda: None) -> int:
    """Списать amount с оптимистической блокировкой (столбец version); вернуть новый баланс.
    before_write() вызывай между чтением и UPDATE (тест имитирует там чужую транзакцию).
    Не хватает денег — InsufficientFunds, попытки кончились — ConflictError."""
    raise NotImplementedError


# ★ Индексы для запроса
#   SELECT created_at, total FROM orders
#   WHERE user_id = ? AND status = 'paid'
#   ORDER BY created_at DESC LIMIT 20
# Список строк CREATE INDEX ...
INDEXES: list[str] = []
