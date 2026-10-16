# Урок 7.2. Два указателя
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 72


def merge_unique(a: list[int], b: list[int]) -> list[int]:
    """Объединение двух отсортированных списков без повторов, O(n + m), без set и sorted.

    >>> merge_unique([1, 2, 2, 5], [2, 3, 5, 7])
    [1, 2, 3, 5, 7]
    """
    raise NotImplementedError


def is_palindrome(s: str) -> bool:
    """Палиндром по буквам и цифрам без учёта регистра, O(1) памяти.

    >>> is_palindrome("A man, a plan, a canal: Panama"), is_palindrome("race a car")
    (True, False)
    """
    raise NotImplementedError


def remove_duplicates(a: list[int]) -> int:
    """Удалить повторы из отсортированного списка на месте; вернуть k — первые k элементов уникальны.

    >>> a = [1, 1, 2, 3, 3]; remove_duplicates(a), a[:3]
    (3, [1, 2, 3])
    """
    raise NotImplementedError


def three_sum(nums: list[int]) -> list[list[int]]:
    """Все уникальные тройки с суммой 0; каждая тройка отсортирована, список троек отсортирован.

    >>> three_sum([-1, 0, 1, 2, -1, -4])
    [[-1, -1, 2], [-1, 0, 1]]
    """
    raise NotImplementedError


def trap_water(heights: list[int]) -> int:
    """★ Сколько единиц воды задержится между столбиками.

    >>> trap_water([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])
    6
    """
    raise NotImplementedError
