// Урок 11.1 — context: отмена, таймауты, errgroup.
//
// Проверка: go test -race ./course/lesson111/
package lesson111

import (
	"context"
	"time"
)

// Задача 1. Подождать d, но вернуться раньше, если ctx отменили.
// Дождались — nil; отменили — ctx.Err().
func Sleep(ctx context.Context, d time.Duration) error {
	// TODO: твой код
	return nil
}

// Задача 2. Запусти все функции параллельно и верни первый УСПЕШНЫЙ результат.
// Как только он получен, остальные должны увидеть отмену своего ctx.
// Если все упали — верни объединённую ошибку (errors.Join).
// Ни одна горутина не должна остаться висеть.
func FirstSuccess(ctx context.Context, fns ...func(ctx context.Context) (string, error)) (string, error) {
	// TODO: твой код
	return "", nil
}

// Задача 3. Своя errgroup.
//
//	g, ctx := WithContext(parent)
//	g.Go(func() error { ... })
//	err := g.Wait() // ждёт всех, возвращает ПЕРВУЮ ошибку
//
// Первая ошибка отменяет ctx, который вернул WithContext. Wait тоже его отменяет в конце.
type Group struct {
	// TODO: поля
}

func WithContext(ctx context.Context) (*Group, context.Context) {
	// TODO: твой код
	return &Group{}, ctx
}

func (g *Group) Go(f func() error) {
	// TODO: твой код
}

func (g *Group) Wait() error {
	// TODO: твой код
	return nil
}

// Задача 4. Обработай все items функцией f, одновременно — не больше limit.
// При первой ошибке: остальным передаётся отменённый ctx, новые задачи не запускаются,
// ProcessAll возвращает эту ошибку после завершения уже запущенных.
func ProcessAll(ctx context.Context, items []int, limit int, f func(ctx context.Context, item int) error) error {
	// TODO: твой код
	return nil
}

// Задача 5 ★. Повторы с экспоненциальной паузой.
//
// До attempts вызовов fn. Между попытками пауза base, 2*base, 4*base...
// Успех — nil. Если ctx отменили во время паузы — сразу вернуть ошибку,
// для которой errors.Is(err, ctx.Err()) == true.
// Все попытки неудачны — вернуть последнюю ошибку.
func RetryCtx(ctx context.Context, attempts int, base time.Duration, fn func() error) error {
	// TODO: твой код
	return nil
}
