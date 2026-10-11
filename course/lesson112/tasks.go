// Урок 11.2 — Паттерны конкурентности.
//
// Проверка: go test -race ./course/lesson112/
package lesson112

import (
	"context"
	"sync"
	"time"
)

// Задача 1. Fan-in: все значения из всех входов — в один выходной канал.
// Выход закрывается, когда закрылись все входы. При отмене ctx горутины завершаются,
// а выход закрывается (даже если входы ещё открыты).
func Merge(ctx context.Context, ins ...<-chan int) <-chan int {
	// TODO: твой код
	out := make(chan int)
	close(out)
	return out
}

// Задача 2. Стадия конвейера: применяет f к каждому значению из in.
// Закрывает выход, когда закрылся вход или отменили ctx.
func Map[T, U any](ctx context.Context, in <-chan T, f func(T) U) <-chan U {
	// TODO: твой код
	out := make(chan U)
	close(out)
	return out
}

// Задача 3. Token bucket.
//
// В ведре до burst жетонов, пополняется со скоростью rate жетонов в секунду.
// В начале ведро полное. Allow забирает жетон и возвращает true или возвращает false, если жетонов нет.
// Текущее время — только через now() (тест подменяет часы).
type Limiter struct {
	mu sync.Mutex
	// TODO: поля
}

func NewLimiter(rate float64, burst int, now func() time.Time) *Limiter {
	// TODO: твой код
	return &Limiter{}
}

func (l *Limiter) Allow() bool {
	// TODO: твой код
	return false
}

// Задача 4. Ленивое значение: f вызывается не больше одного раза,
// даже если Get вызывают одновременно из многих горутин.
type Lazy[T any] struct {
	f func() (T, error)
	// TODO: поля
}

func NewLazy[T any](f func() (T, error)) *Lazy[T] {
	return &Lazy[T]{f: f}
}

func (l *Lazy[T]) Get() (T, error) {
	// TODO: твой код
	return l.f()
}

// Задача 5 ★. Пачки.
//
// Читай из in и отдавай пачки в выходной канал:
//   - как только в пачке size элементов — отдать сразу;
//   - если с ПЕРВОГО элемента пачки прошло wait, а она не полная — отдать как есть;
//   - in закрылся — отдать остаток (если не пустой) и закрыть выход.
//
// Пустые пачки не отправляются.
func Batch[T any](in <-chan T, size int, wait time.Duration) <-chan []T {
	// TODO: твой код
	out := make(chan []T)
	close(out)
	return out
}
