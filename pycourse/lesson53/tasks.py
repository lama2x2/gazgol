# Урок 5.3. asyncio: event loop, задачи, отмена
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 53
import asyncio  # noqa: F401


async def fetch_all(urls, fetch, limit):
    """[await fetch(u) for u in urls] конкурентно, не больше limit одновременно; порядок как во входе."""
    raise NotImplementedError


async def with_timeout(coro, seconds, default=None):
    """Результат coro, если успела за seconds, иначе default (а coro отменена)."""
    raise NotImplementedError


async def race(*coros):
    """Результат первой успешно завершившейся корутины; остальные отменить.
    Если упали все — ExceptionGroup со всеми ошибками."""
    raise NotImplementedError


async def gather_blocking(funcs):
    """Выполнить блокирующие функции без аргументов конкурентно, не блокируя цикл; результаты по порядку."""
    raise NotImplementedError


async def run_pipeline(items, worker_fn, n_workers=3):
    """★ Конвейер на asyncio.Queue(maxsize=n_workers * 2): n_workers воркеров вызывают await worker_fn(item).
    Вернуть список результатов в порядке items; если worker_fn упал — на этом месте объект исключения."""
    raise NotImplementedError
