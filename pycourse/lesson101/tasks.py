# Урок 10.1. Рекурсия и перебор с возвратом
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 101
# itertools.permutations / combinations / product в этом уроке не используй.


def subsets(nums: list[int]) -> list[list[int]]:
    """Все подмножества в порядке обхода из разбора.

    >>> subsets([1, 2, 3])
    [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
    """
    raise NotImplementedError


def permutations(nums: list[int]) -> list[list[int]]:
    """Все перестановки различных чисел в лексикографическом порядке индексов.

    >>> permutations([1, 2, 3])
    [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
    """
    raise NotImplementedError


def generate_parentheses(n: int) -> list[str]:
    """Все правильные скобочные последовательности из n пар в лексикографическом порядке.

    >>> generate_parentheses(2)
    ['(())', '()()']
    """
    raise NotImplementedError


def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    """Комбинации (с повторами) с суммой target; каждая по неубыванию, список отсортирован.

    >>> combination_sum([2, 3, 6, 7], 7)
    [[2, 2, 3], [7]]
    """
    raise NotImplementedError


def n_queens(n: int) -> int:
    """★ Число расстановок n ферзей на доске n × n.

    >>> n_queens(4), n_queens(8)
    (2, 92)
    """
    raise NotImplementedError
