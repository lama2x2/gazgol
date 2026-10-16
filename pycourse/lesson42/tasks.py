# Урок 4.2. Наследование, MRO, дескрипторы и метаклассы
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 42
import threading  # noqa: F401 — для SingletonMeta


class Positive:
    """Дескриптор: значение — число > 0 (не bool). Иначе ValueError / TypeError.

    class Order:
        qty = Positive()
    """

    def __set_name__(self, owner, name):
        raise NotImplementedError

    def __get__(self, obj, owner):
        raise NotImplementedError

    def __set__(self, obj, value):
        raise NotImplementedError


class cached_prop:
    """Свой functools.cached_property: вычислить один раз и сохранить в экземпляре.

    class Report:
        @cached_prop
        def total(self): ...
    """

    def __init__(self, func):
        raise NotImplementedError


class Plugin:
    """Базовый класс с реестром наследников.

    class Csv(Plugin, name="csv"): ...      → Plugin.registry["csv"] is Csv
    class Json(Plugin): ...                 → Plugin.registry["json"] is Json
    Plugin.create("csv", *args)             → экземпляр Csv(*args)
    """

    registry = {}


class SingletonMeta(type):
    """★ Метакласс: один экземпляр на класс, __init__ — один раз, потокобезопасно.

    class Config(metaclass=SingletonMeta): ...
    Config() is Config()  → True
    """
