# Урок 2.1. Всё — объект: имена, ссылки, изменяемость
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 21


def append_to(x, items=None):
    """Добавить x в items и вернуть items. Без items — начать с нового пустого списка.

    >>> append_to(1), append_to(2)
    ([1], [2])
    >>> lst = []; append_to(1, lst) is lst
    True
    """
    raise NotImplementedError


def make_grid(rows: int, cols: int, fill=0) -> list[list]:
    """Сетка rows × cols, заполненная fill; строки — независимые списки.

    >>> make_grid(2, 3)
    [[0, 0, 0], [0, 0, 0]]
    """
    raise NotImplementedError


def deep_copy(obj):
    """Глубокая копия вложенных list / dict / tuple / set (без модуля copy).

    >>> a = {"x": [1, [2]]}; b = deep_copy(a); b["x"][1].append(3); a
    {'x': [1, [2]]}
    """
    raise NotImplementedError


def dedupe(items: list) -> list:
    """Убрать повторы, сохранив порядок первых вхождений. Элементы хешируемые.

    >>> dedupe([3, 1, 3, 2, 1])
    [3, 1, 2]
    """
    raise NotImplementedError


def freeze(obj):
    """★ Хешируемая версия вложенной структуры: list/tuple → tuple, set → frozenset,
    dict → frozenset пар (ключ, freeze(значение)). Остальное — как есть.

    >>> freeze([1, [2, 3]])
    (1, (2, 3))
    >>> freeze({"a": 1, "b": [2]}) == freeze({"b": [2], "a": 1})
    True
    """
    raise NotImplementedError
