//lyceum:race — проверка запускается с детектором гонок (-race).

package lesson111

import (
	"context"
	"errors"
	"runtime"
	"strings"
	"sync/atomic"
	"testing"
	"time"
)

func TestSleep(t *testing.T) {
	start := time.Now()
	if err := Sleep(context.Background(), 30*time.Millisecond); err != nil || time.Since(start) < 30*time.Millisecond {
		t.Errorf("Sleep(30ms) = %v за %v — ожидался nil не раньше чем через 30ms", err, time.Since(start))
	}
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Millisecond)
	defer cancel()
	start = time.Now()
	err := Sleep(ctx, time.Second)
	if !errors.Is(err, context.DeadlineExceeded) || time.Since(start) > 300*time.Millisecond {
		t.Errorf("Sleep(1s) с таймаутом 20ms = %v за %v — ожидалось DeadlineExceeded почти сразу", err, time.Since(start))
	}
}

func TestFirstSuccess(t *testing.T) {
	before := runtime.NumGoroutine()
	var cancelled atomic.Int32
	slow := func(ctx context.Context) (string, error) {
		select {
		case <-time.After(2 * time.Second):
			return "медленный", nil
		case <-ctx.Done():
			cancelled.Add(1)
			return "", ctx.Err()
		}
	}
	fast := func(ctx context.Context) (string, error) {
		time.Sleep(20 * time.Millisecond)
		return "быстрый", nil
	}
	failing := func(ctx context.Context) (string, error) { return "", errors.New("упал") }

	start := time.Now()
	got, err := FirstSuccess(context.Background(), slow, failing, fast, slow)
	if got != "быстрый" || err != nil || time.Since(start) > time.Second {
		t.Fatalf("FirstSuccess = %q, %v за %v — ожидался быстрый ответ", got, err, time.Since(start))
	}
	time.Sleep(100 * time.Millisecond)
	if cancelled.Load() != 2 {
		t.Errorf("медленные функции увидели отмену %d раз из 2 — после успеха нужно отменить остальных", cancelled.Load())
	}
	_, err = FirstSuccess(context.Background(), failing, failing)
	if err == nil || !strings.Contains(err.Error(), "упал") {
		t.Errorf("все упали: ожидалась объединённая ошибка, а получено %v", err)
	}
	time.Sleep(50 * time.Millisecond)
	if after := runtime.NumGoroutine(); after > before+1 {
		t.Errorf("горутин было %d, стало %d — кто-то завис (утечка)", before, after)
	}
}

func TestGroup(t *testing.T) {
	g, ctx := WithContext(context.Background())
	var done atomic.Int32
	for range 5 {
		g.Go(func() error { time.Sleep(10 * time.Millisecond); done.Add(1); return nil })
	}
	if err := g.Wait(); err != nil || done.Load() != 5 {
		t.Fatalf("5 успешных задач: Wait = %v, выполнено %d", err, done.Load())
	}
	if ctx.Err() == nil {
		t.Error("после Wait контекст группы должен быть отменён")
	}

	boom := errors.New("boom")
	g, ctx = WithContext(context.Background())
	var sawCancel atomic.Bool
	g.Go(func() error { time.Sleep(10 * time.Millisecond); return boom })
	g.Go(func() error { time.Sleep(30 * time.Millisecond); return errors.New("вторая ошибка") })
	g.Go(func() error {
		select {
		case <-ctx.Done():
			sawCancel.Store(true)
			return ctx.Err()
		case <-time.After(2 * time.Second):
			return nil
		}
	})
	start := time.Now()
	if err := g.Wait(); err != boom {
		t.Errorf("Wait = %v, а ожидалась первая ошибка boom", err)
	}
	if !sawCancel.Load() || time.Since(start) > time.Second {
		t.Error("первая ошибка должна отменить контекст группы, чтобы остальные задачи остановились")
	}
}

func TestProcessAll(t *testing.T) {
	items := make([]int, 30)
	for i := range items {
		items[i] = i
	}
	var running, peak, total atomic.Int32
	err := ProcessAll(context.Background(), items, 4, func(ctx context.Context, item int) error {
		n := running.Add(1)
		for {
			p := peak.Load()
			if n <= p || peak.CompareAndSwap(p, n) {
				break
			}
		}
		time.Sleep(5 * time.Millisecond)
		running.Add(-1)
		total.Add(1)
		return nil
	})
	if err != nil || total.Load() != 30 {
		t.Fatalf("ProcessAll без ошибок: err = %v, обработано %d из 30", err, total.Load())
	}
	if peak.Load() > 4 || peak.Load() < 2 {
		t.Errorf("одновременно работало до %d задач, а лимит 4 (и параллельность должна быть)", peak.Load())
	}

	boom := errors.New("boom")
	var started atomic.Int32
	err = ProcessAll(context.Background(), items, 2, func(ctx context.Context, item int) error {
		started.Add(1)
		if item == 3 {
			return boom
		}
		select {
		case <-ctx.Done():
		case <-time.After(20 * time.Millisecond):
		}
		return nil
	})
	if !errors.Is(err, boom) {
		t.Errorf("ProcessAll с ошибкой на элементе 3 вернул %v", err)
	}
	if started.Load() > 8 {
		t.Errorf("после ошибки запустилось слишком много задач: %d из 30 — новые запускать не нужно", started.Load())
	}
}

func TestRetryCtx(t *testing.T) {
	calls := 0
	start := time.Now()
	err := RetryCtx(context.Background(), 4, 10*time.Millisecond, func() error {
		calls++
		if calls < 3 {
			return errors.New("timeout")
		}
		return nil
	})
	el := time.Since(start)
	if err != nil || calls != 3 || el < 30*time.Millisecond || el > 500*time.Millisecond {
		t.Errorf("успех с 3-й попытки: err %v, вызовов %d, время %v — ожидались паузы 10ms + 20ms", err, calls, el)
	}

	calls = 0
	boom := errors.New("boom")
	start = time.Now()
	err = RetryCtx(context.Background(), 3, 5*time.Millisecond, func() error { calls++; return boom })
	if !errors.Is(err, boom) || calls != 3 || time.Since(start) > 200*time.Millisecond {
		t.Errorf("все неудачны: err %v, вызовов %d за %v — после последней попытки ждать не нужно", err, calls, time.Since(start))
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Millisecond)
	defer cancel()
	calls = 0
	start = time.Now()
	err = RetryCtx(ctx, 10, 100*time.Millisecond, func() error { calls++; return boom })
	if !errors.Is(err, context.DeadlineExceeded) || calls != 1 || time.Since(start) > 300*time.Millisecond {
		t.Errorf("отмена во время паузы: err %v, вызовов %d за %v — ожидался быстрый выход с DeadlineExceeded", err, calls, time.Since(start))
	}
}
