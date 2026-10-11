// Урок 6.1 — Горутины и каналы.
//
// Проверка: go test -race ./course/lesson61/
package lesson61

import "time"

// Задача 1. Генератор.
//
// Верни канал, в который отдельная горутина отправит числа 1..n,
// а потом закроет его. Вызывающий читает: for v := range Generate(3) { … }
func Generate(n int) <-chan int {
	// TODO: твой код
	ch := make(chan int)
	close(ch)
	return ch
}

// Задача 2. Конвейер.
//
// Читай числа из in, отправляй их квадраты в новый канал.
// Когда in закроется, закрой и выходной канал.
//
//	Squares(Generate(3)) → 1, 4, 9
func Squares(in <-chan int) <-chan int {
	// TODO: твой код
	ch := make(chan int)
	close(ch)
	return ch
}

// Задача 3. Параллельная сумма.
//
// Разбей срез на parts примерно равных кусков, посчитай сумму каждого
// куска в своей горутине, частичные суммы собери через канал и сложи.
// Если parts < 1, считай, что parts = 1. Если parts больше длины среза, тоже не ломайся.
// Пустой срез → 0.
func SumParallel(nums []int, parts int) int {
	// TODO: твой код
	return 0
}

// Задача 4 ★. Таймаут через select.
//
// Запусти f в горутине. Если она вернула результат быстрее, чем за d,
// верни его и true. Иначе верни 0 и false, не дожидаясь f.
// Подсказка: select + time.After(d). Канал для результата сделай
// буферизованным (make(chan int, 1)), иначе опоздавшая горутина зависнет навсегда.
func WithTimeout(f func() int, d time.Duration) (int, bool) {
	// TODO: твой код
	return 0, false
}
