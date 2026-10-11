// Урок 14.1 — Как устроены канал, мьютекс и модель памяти.
// Домашка: свои примитивы синхронизации.
//
// Проверка: go test -race ./course/lesson141/
package lesson141

import (
	"context"
	"sync"
	"sync/atomic"
)

// Задача 1. Спинлок на CAS.
type SpinLock struct {
	locked atomic.Bool
}

func (l *SpinLock) Lock() {
	// TODO: твой код
}

func (l *SpinLock) Unlock() {
	// TODO: твой код
}

// Задача 2. Атомарно записать в a значение v, если оно больше текущего.
func StoreMax(a *atomic.Int64, v int64) {
	// TODO: твой код
}

// Задача 3. Семафор на n мест.
type Semaphore struct {
	// TODO: поля
}

func NewSemaphore(n int) *Semaphore {
	// TODO: твой код
	return &Semaphore{}
}

// Acquire занимает место или ждёт; при отмене ctx возвращает ctx.Err(), не заняв места.
func (s *Semaphore) Acquire(ctx context.Context) error {
	// TODO: твой код
	return nil
}

// Release освобождает место.
func (s *Semaphore) Release() {
	// TODO: твой код
}

// Задача 4. Как sync.Once, но f повторяется, пока не завершится успешно.
// После первого успеха Do больше не вызывает f и возвращает nil.
// Параллельные вызовы не запускают f одновременно.
type OnceErr struct {
	mu sync.Mutex
	// TODO: поля
}

func (o *OnceErr) Do(f func() error) error {
	// TODO: твой код
	return f()
}

// Задача 5 ★. Многоразовый барьер: Wait блокирует, пока его не вызовут n горутин,
// затем отпускает всех сразу и готов к следующему раунду.
type Barrier struct {
	// TODO: поля
}

func NewBarrier(n int) *Barrier {
	// TODO: твой код
	return &Barrier{}
}

func (b *Barrier) Wait() {
	// TODO: твой код
}
