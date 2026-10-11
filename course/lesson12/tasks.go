// Урок 1.2 — Переменные, типы, арифметика, срезы и map.
//
// Проверка: go test ./course/lesson12/
package lesson12

// Задача 1. Градусы.
//
// Переведи градусы Цельсия в Фаренгейты: F = C * 9 / 5 + 32.
//
//	CelsiusToFahrenheit(100) → 212
//	CelsiusToFahrenheit(-40) → -40
func CelsiusToFahrenheit(c float64) float64 {
	// TODO: твой код
	return 0
}

// Задача 2. Среднее.
//
// Верни среднее арифметическое трёх целых чисел как float64.
// Осторожно: 1 + 2 / 3 в целых числах — совсем не то, что хочется.
//
//	Average(1, 2, 2) → 1.6666…
func Average(a, b, c int) float64 {
	// TODO: твой код
	return 0
}

// Задача 3. Таймер.
//
// Дано число секунд. Верни строку "ЧЧ:ММ:СС" с ведущими нулями.
// Подсказка: / и % для целых, и формат %02d.
//
//	FormatDuration(3723)  → "01:02:03"
//	FormatDuration(59)    → "00:00:59"
//	FormatDuration(36000) → "10:00:00"
func FormatDuration(total int) string {
	// TODO: твой код
	return ""
}

// Задача 4. Без краёв (индексы и срезы).
//
// Верни срез без первого и последнего элемента. Циклы и if не нужны — только s[a:b].
// Гарантируется, что элементов минимум два.
//
//	WithoutEnds([]int{1, 2, 3, 4}) → [2 3]
//	WithoutEnds([]int{1, 2})       → []
func WithoutEnds(nums []int) []int {
	// TODO: твой код
	return nil
}

// Задача 5. Прайс-лист (map).
//
// Найди цену товара в словаре. Второй результат — есть ли такой товар.
// Подсказка: v, ok := m[key].
//
//	Lookup(map[string]int{"чайник": 1500}, "чайник") → 1500, true
//	Lookup(map[string]int{"чайник": 1500}, "диван")  → 0, false
func Lookup(prices map[string]int, item string) (int, bool) {
	// TODO: твой код
	return 0, false
}
