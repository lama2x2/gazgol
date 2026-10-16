# Урок 11.3. Код-ревью и поиск ошибок
#
# Здесь код уже написан, но с ошибками. Найди и исправь их, не переписывая всё с нуля
# (хотя можно, если так понятнее). Проверка:
#     python3 pycourse/check.py 113
import asyncio
import re
import time


def paginate(items: list, page: int, per_page: int = 10) -> dict:
    """Страница page (с 1) по per_page элементов.

    → {"items": [...], "page": page, "total_pages": ceil(len / per_page), "has_next": есть ли следующая}
    page < 1 или per_page < 1 — ValueError. Страница за пределами — пустой items.
    В функции 4 ошибки.
    """
    start = page * per_page
    end = start + per_page
    total_pages = len(items) // per_page
    return {"items": items[start:end], "page": page, "total_pages": total_pages, "has_next": page <= total_pages}


def merge_settings(defaults: dict, overrides: dict = {}) -> dict:
    """Рекурсивное слияние настроек: значения из overrides побеждают, вложенные словари сливаются
    на любую глубину. Возвращает новый словарь, входные не меняет. В функции 3 ошибки.
    """
    result = defaults
    for key, value in overrides.items():
        if isinstance(value, dict) and key in result:
            result[key].update(value)
        else:
            result[key] = value
    return result


UNITS = {"h": 60, "m": 3600, "s": 1}


def parse_duration(s: str) -> int:
    """"1h30m15s" → 5415 секунд; части в любом порядке и количестве, числа любой длины.
    Пустая строка или мусор — ValueError. В функции 3 ошибки.
    """
    total = 0
    for num, unit in re.findall(r"(\d)([hms])", s):
        total += int(num) * UNITS[unit]
    return total


def top_words(text: str, k: int, stop: frozenset = frozenset()) -> list[str]:
    """k самых частых слов (без учёта регистра и знаков .,!?:; по краям), без стоп-слов;
    по убыванию частоты, при равенстве — по алфавиту. В функции 4 ошибки.
    """
    counts = {}
    for w in text.split(" "):
        w = w.strip(".,!?:;").lower
        if w in stop:
            continue
        counts[w] = counts.get(w, 0) + 1
    return sorted(counts, key=lambda w: counts[w])[:k]


async def fetch_all(urls, fetch, limit=5, retries=2, delay=0.01):
    """★ Результаты await fetch(url) в порядке urls, конкурентно, не больше limit одновременно.
    На каждый URL до retries + 1 попыток с паузой delay между ними; если все упали —
    на месте результата объект последнего исключения. В функции 5 ошибок.
    """
    results = []
    for url in urls:
        for attempt in range(retries):
            try:
                results.append(await fetch(url))
            except Exception:
                time.sleep(delay)
    return results
