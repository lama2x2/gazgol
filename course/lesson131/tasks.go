// Урок 13.1 — Горутины и планировщик. Домашка «найди и почини».
//
// Каждая функция ниже РАБОТАЕТ — возвращает правильный результат. Но в каждой
// спрятана утечка горутин или зависание. Найди и исправь, не меняя сигнатуры.
//
// Проверка: go test -race ./course/lesson131/
package lesson131

import (
	"context"
	"errors"
	"sync"
	"time"
)

// Задача 1. Спрашиваем цену у нескольких поставщиков, берём первый ответ.
func FirstPrice(suppliers []func() int) int {
	ch := make(chan int)
	for _, s := range suppliers {
		go func() { ch <- s() }()
	}
	return <-ch
}

// Задача 2. Генератор чисел 0, 1, 2, ... до отмены ctx.
// После отмены канал должен закрыться, а горутина — завершиться.
func Numbers(ctx context.Context) <-chan int {
	ch := make(chan int)
	go func() {
		defer close(ch)
		for i := 0; ; i++ {
			ch <- i
		}
	}()
	return ch
}

// Задача 3. Обработать задачи несколькими воркерами и вернуть сумму результатов.
func RunJobs(jobs []int, workers int, f func(int) int) int {
	in := make(chan int)
	var mu sync.Mutex
	var wg sync.WaitGroup
	sum := 0
	for range workers {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := range in {
				r := f(j)
				mu.Lock()
				sum += r
				mu.Unlock()
			}
		}()
	}
	for _, j := range jobs {
		in <- j
	}
	wg.Wait()
	return sum
}

// Задача 4. Раз в interval вызывать report, пока не отменят ctx.
func StartReporter(ctx context.Context, interval time.Duration, report func()) {
	go func() {
		ticker := time.NewTicker(interval)
		for range ticker.C {
			report()
		}
	}()
}

// Задача 5 ★. Счёт с балансом.
var ErrInsufficient = errors.New("недостаточно средств")

type Account struct {
	mu      sync.Mutex
	balance int
}

func (a *Account) Withdraw(amount int) error {
	a.mu.Lock()
	if a.balance < amount {
		return ErrInsufficient
	}
	a.balance -= amount
	a.mu.Unlock()
	return nil
}

func (a *Account) Deposit(amount int) {
	a.mu.Lock()
	a.balance += amount
	a.mu.Unlock()
}
