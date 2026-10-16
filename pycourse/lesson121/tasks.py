# Урок 12.1. SQL на собеседовании
#
# Здесь ответы — SQL-запросы в строках. База — SQLite в памяти, схема и данные в shopdb.py.
# Попробовать запрос:
#     python3 pycourse/lesson121/shopdb.py "SELECT * FROM orders LIMIT 5"
# Проверка:
#     python3 pycourse/check.py 121
#
# Схема:
#   users(id, name, city, created_at, banned_at)
#   products(id, name, category, price)                 — текущая цена
#   orders(id, user_id, created_at, status)             — status: 'paid' | 'cancelled' | 'new'
#   order_items(order_id, product_id, qty, price)       — цена на момент заказа
#   employees(id, name, department, salary, manager_id)
# Даты — строки 'YYYY-MM-DD HH:MM:SS'; date(x) даёт день, datetime(x, '+7 days') — сдвиг.

# Имена пользователей без заказов, по алфавиту. Столбцы: name
Q_USERS_WITHOUT_ORDERS = """
SELECT 1
"""

# Выручка оплаченных заказов по категориям, только > 50000, по убыванию. Столбцы: category, revenue
Q_REVENUE_BY_CATEGORY = """
SELECT 1
"""

# Сотрудники с двумя наибольшими различными зарплатами в своём отделе.
# Столбцы: department, name, salary; ORDER BY department, salary DESC, name
Q_TOP2_SALARY = """
SELECT 1
"""

# GMV оплаченных заказов по дням и нарастающий итог. Столбцы: day, gmv, running_gmv; по дню
Q_RUNNING_GMV = """
SELECT 1
"""

# Вторая по величине различная зарплата или NULL. Одна строка, один столбец
Q_SECOND_SALARY = """
SELECT 1
"""

# ★ Для пользователей с оплаченными заказами: user_id, first_order_day, first_week_revenue
# (выручка оплаченных заказов в первые 7 суток от первого оплаченного); ORDER BY user_id
Q_FIRST_WEEK = """
SELECT 1
"""
