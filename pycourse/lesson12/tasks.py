# Урок 1.2. Как решать задачу на лайвкоде
#
# Пиши решение вместо `raise NotImplementedError`. Проверка:
#     python3 pycourse/check.py 12
# Сначала проговори идею и сложность, потом пиши код, потом проверь
# на примерах из docstring в уме — как на собесе, где код не запускают.


def compress_ranges(nums: list[int]) -> str:
    """Сжать числа в диапазоны.

    >>> compress_ranges([1, 4, 5, 2, 3, 9, 8, 11, 0])
    '0-5,8-9,11'
    >>> compress_ranges([])
    ''
    """
    raise NotImplementedError


def longest_non_decreasing(nums: list[int]) -> int:
    """Длина самого длинного непрерывного отрезка, где каждый элемент >= предыдущего.

    >>> longest_non_decreasing([1, 2, 2, 1, 5, 6, 7, 0])
    4
    """
    raise NotImplementedError


def clock_angle(h: int, m: int) -> float:
    """Меньший угол между часовой и минутной стрелкой, в градусах.

    >>> clock_angle(3, 0)
    90.0
    >>> clock_angle(3, 30)
    75.0
    """
    raise NotImplementedError


def is_monotonic(nums: list[int]) -> bool:
    """True, если список неубывающий или невозрастающий.

    >>> is_monotonic([1, 2, 2, 3]), is_monotonic([3, 3, 1]), is_monotonic([1, 3, 2])
    (True, True, False)
    """
    raise NotImplementedError


def max_dist_to_closest(seats: list[int]) -> int:
    """★ Ряд кинотеатра: 1 — занято, 0 — свободно. Зритель садится так, чтобы
    расстояние до ближайшего соседа было максимальным. Верни это расстояние.

    >>> max_dist_to_closest([1, 0, 0, 0, 1, 0, 1])
    2
    >>> max_dist_to_closest([0, 0, 0, 1])
    3
    """
    raise NotImplementedError
