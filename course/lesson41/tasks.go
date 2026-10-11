// Урок 4.1 — Свои функции: несколько результатов, variadic, рекурсия, замыкания.
//
// Проверка: go test ./course/lesson41/
package lesson41

// Задача 1. Минимум и максимум.
//
// Верни наименьшее и наибольшее из трёх чисел — двумя результатами.
//
//	MinMax(3, 1, 2) → 1, 3
func MinMax(a, b, c int) (int, int) {
	// TODO: твой код
	return 0, 0
}

// Задача 2. Максимум из любого количества (variadic, как *args в Python).
//
// Второй результат false, если чисел не передали.
//
//	MaxOf(3, 9, 2) → 9, true
//	MaxOf()        → 0, false
func MaxOf(nums ...int) (int, bool) {
	// TODO: твой код
	return 0, false
}

// Задача 3. Фибоначчи рекурсией.
//
// Fib(0) = 0, Fib(1) = 1, Fib(n) = Fib(n-1) + Fib(n-2).
// Функция должна вызывать сама себя.
func Fib(n int) int {
	// TODO: твой код
	return 0
}

// Задача 4. Счётчик просмотров (замыкание).
//
// Верни функцию, которая при каждом вызове возвращает следующее число: 1, 2, 3…
// У каждого нового счётчика свой отсчёт.
//
//	views := NewCounter()
//	views() → 1; views() → 2
func NewCounter() func() int {
	// TODO: твой код
	return func() int { return 0 }
}

// Задача 5 ★. Дважды.
//
// Примени функцию f к x два раза: f(f(x)). Аналог lambda в Go —
// анонимная функция: func(n int) int { return n + 3 }.
//
//	ApplyTwice(func(n int) int { return n + 3 }, 10) → 16
func ApplyTwice(f func(int) int, x int) int {
	// TODO: твой код
	return 0
}
