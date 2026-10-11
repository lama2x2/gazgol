//lyceum:race — проверка запускается с детектором гонок (-race).

package lesson131

import (
	"context"
	"errors"
	"runtime"
	"sync/atomic"
	"testing"
	"time"
)

// settle ждёт, пока число горутин перестанет падать.
func goroutines() int {
	n := runtime.NumGoroutine()
	for range 20 {
		time.Sleep(10 * time.Millisecond)
		m := runtime.NumGoroutine()
		if m == n {
			break
		}
		n = m
	}
	return n
}

func TestFirstPriceNoLeak(t *testing.T) {
	before := goroutines()
	for range 20 {
		got := FirstPrice([]func() int{
			func() int { return 100 },
			func() int { time.Sleep(5 * time.Millisecond); return 200 },
			func() int { time.Sleep(5 * time.Millisecond); return 300 },
		})
		if got != 100 && got != 200 && got != 300 {
			t.Fatalf("FirstPrice = %d", got)
		}
	}
	time.Sleep(30 * time.Millisecond)
	if after := goroutines(); after > before+2 {
		t.Errorf("после 20 вызовов горутин стало %d (было %d): проигравшие горутины зависли на отправке", after, before)
	}
}

func TestNumbersStops(t *testing.T) {
	before := goroutines()
	ctx, cancel := context.WithCancel(context.Background())
	ch := Numbers(ctx)
	for want := range 5 {
		if got := <-ch; got != want {
			t.Fatalf("Numbers: получено %d, а ожидалось %d", got, want)
		}
	}
	cancel()
	closed := false
	deadline := time.After(time.Second)
	for !closed {
		select {
		case _, ok := <-ch:
			closed = !ok
		case <-deadline:
			t.Fatal("после отмены ctx канал так и не закрылся")
		}
	}
	if after := goroutines(); after > before {
		t.Errorf("горутина генератора не завершилась: было %d, стало %d", before, after)
	}
}

func TestRunJobsFinishes(t *testing.T) {
	done := make(chan int, 1)
	go func() { done <- RunJobs([]int{1, 2, 3, 4, 5}, 3, func(x int) int { return x * 10 }) }()
	select {
	case got := <-done:
		if got != 150 {
			t.Errorf("RunJobs = %d, а ожидалось 150", got)
		}
	case <-time.After(2 * time.Second):
		t.Fatal("RunJobs завис: воркеры ждут новых задач, которых не будет")
	}
}

func TestReporterStops(t *testing.T) {
	before := goroutines()
	var calls atomic.Int32
	ctx, cancel := context.WithCancel(context.Background())
	StartReporter(ctx, 5*time.Millisecond, func() { calls.Add(1) })
	time.Sleep(40 * time.Millisecond)
	cancel()
	time.Sleep(20 * time.Millisecond)
	n := calls.Load()
	if n < 2 {
		t.Fatalf("report вызван %d раз за 40ms при интервале 5ms", n)
	}
	time.Sleep(40 * time.Millisecond)
	if calls.Load() != n {
		t.Error("после отмены ctx report продолжает вызываться")
	}
	if after := goroutines(); after > before {
		t.Errorf("горутина репортера не завершилась: было %d, стало %d", before, after)
	}
}

func TestWithdrawNoDeadlock(t *testing.T) {
	a := &Account{}
	a.Deposit(100)
	done := make(chan error, 1)
	go func() {
		if err := a.Withdraw(500); !errors.Is(err, ErrInsufficient) {
			done <- err
			return
		}
		done <- a.Withdraw(60)
	}()
	select {
	case err := <-done:
		if err != nil {
			t.Errorf("Withdraw(60) после неудачного Withdraw(500) вернул %v", err)
		}
	case <-time.After(time.Second):
		t.Fatal("второй Withdraw завис: мьютекс не отпущен на одном из путей выполнения")
	}
}
