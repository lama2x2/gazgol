// Урок 17.1 — Взаимодействие сервисов и отказоустойчивость.
//
// Проверка: go test -race ./course/lesson171/
package lesson171

import (
	"context"
	"errors"
	"net/http"
	"sync"
	"time"
)

var (
	ErrOpen      = errors.New("circuit breaker open")
	ErrTemporary = errors.New("temporary error") // такие ошибки можно повторять
)

// Задача 1. Пауза перед попыткой attempt (0, 1, 2...): случайное от 0 до min(max, base·2^attempt).
// rnd возвращает число от 0 до 1.
func Backoff(attempt int, base, max time.Duration, rnd func() float64) time.Duration {
	// TODO: твой код
	return 0
}

// Задача 2. Автоматический выключатель.
//
// CLOSED: вызовы проходят; Threshold ошибок ПОДРЯД → OPEN.
// OPEN: Call сразу возвращает ErrOpen, пока не прошло OpenFor с момента открытия.
// Затем HALF-OPEN: пропускается ровно один пробный вызов (остальные — ErrOpen),
// успех → CLOSED, ошибка → снова OPEN.
type Breaker struct {
	Threshold int
	OpenFor   time.Duration
	Now       func() time.Time

	mu sync.Mutex
	// TODO: поля
}

func (b *Breaker) Call(fn func() error) error {
	// TODO: твой код
	return fn()
}

// Задача 3. Повторы.
type Retrier struct {
	Attempts  int
	Base, Max time.Duration
	Rand      func() float64
	Sleep     func(ctx context.Context, d time.Duration) error
}

// Do вызывает fn до Attempts раз. Повторяет только ошибки, для которых
// errors.Is(err, ErrTemporary). Не засыпает, если до дедлайна ctx осталось меньше паузы,
// и сразу возвращает последнюю ошибку.
func (r Retrier) Do(ctx context.Context, fn func(ctx context.Context) error) error {
	// TODO: твой код
	return fn(ctx)
}

// Задача 4. Middleware ключей идемпотентности (заголовок Idempotency-Key).
//
//	без ключа                      → как обычно
//	новый ключ                     → выполнить и запомнить статус и тело ответа
//	ключ выполнен, тело то же      → вернуть сохранённое + заголовок Idempotent-Replayed: true
//	ключ выполнен, тело другое     → 422
//	ключ ещё выполняется           → 409
func Idempotent(next http.Handler) http.Handler {
	// TODO: твой код
	return next
}

// Задача 5 ★. Таймаут для вызова вниз по цепочке: оставить reserve на свою работу,
// не больше max. Если у ctx нет дедлайна — (max, true). Бюджета нет — (0, false).
func OutgoingTimeout(ctx context.Context, reserve, max time.Duration) (time.Duration, bool) {
	// TODO: твой код
	return max, true
}
