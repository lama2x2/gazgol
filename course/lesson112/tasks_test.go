//lyceum:race — проверка запускается с детектором гонок (-race).

package lesson112

import (
	"context"
	"errors"
	"runtime"
	"slices"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func gen(vals ...int) <-chan int {
	ch := make(chan int)
	go func() {
		defer close(ch)
		for _, v := range vals {
			ch <- v
		}
	}()
	return ch
}

func drain[T any](t *testing.T, ch <-chan T) []T {
	t.Helper()
	var out []T
	timeout := time.After(2 * time.Second)
	for {
		select {
		case v, ok := <-ch:
			if !ok {
				return out
			}
			out = append(out, v)
		case <-timeout:
			t.Fatalf("выходной канал не закрылся за 2 секунды; прочитано %v", out)
			return nil
		}
	}
}

func TestMerge(t *testing.T) {
	got := drain(t, Merge(context.Background(), gen(1, 2, 3), gen(10, 20), gen(), gen(100)))
	slices.Sort(got)
	if want := []int{1, 2, 3, 10, 20, 100}; !slices.Equal(got, want) {
		t.Errorf("Merge отдал %v, а ожидалось %v (в любом порядке)", got, want)
	}

	before := runtime.NumGoroutine()
	ctx, cancel := context.WithCancel(context.Background())
	endless := make(chan int)
	go func() {
		for i := 0; ; i++ {
			select {
			case endless <- i:
			case <-time.After(time.Second):
				return
			}
		}
	}()
	out := Merge(ctx, endless, gen(1, 2, 3))
	<-out
	cancel()
	drain(t, out)
	time.Sleep(50 * time.Millisecond)
	if after := runtime.NumGoroutine(); after > before+2 {
		t.Errorf("после отмены горутин стало %d (было %d) — горутины Merge должны завершиться", after, before)
	}
}

func TestMap(t *testing.T) {
	words := make(chan string)
	go func() {
		defer close(words)
		for _, w := range []string{"go", "kafka", "postgres"} {
			words <- w
		}
	}()
	got := drain(t, Map(context.Background(), words, func(s string) int { return len(s) }))
	if !slices.Equal(got, []int{2, 5, 8}) {
		t.Errorf("Map(len) = %v, а ожидалось [2 5 8]", got)
	}
	ctx, cancel := context.WithCancel(context.Background())
	never := make(chan int)
	out := Map(ctx, never, func(v int) int { return v })
	cancel()
	drain(t, out)
}

func TestLimiter(t *testing.T) {
	var mu sync.Mutex
	now := time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)
	clock := func() time.Time { mu.Lock(); defer mu.Unlock(); return now }
	advance := func(d time.Duration) { mu.Lock(); now = now.Add(d); mu.Unlock() }

	l := NewLimiter(2, 3, clock) // 2 в секунду, ведро на 3
	allowed := 0
	for range 5 {
		if l.Allow() {
			allowed++
		}
	}
	if allowed != 3 {
		t.Fatalf("полное ведро на 3: из 5 запросов пропущено %d", allowed)
	}
	advance(500 * time.Millisecond) // +1 жетон
	if !l.Allow() || l.Allow() {
		t.Error("через 0.5с при скорости 2/с должен появиться ровно 1 жетон")
	}
	advance(10 * time.Second) // ведро снова полное, но не больше burst
	allowed = 0
	for range 10 {
		if l.Allow() {
			allowed++
		}
	}
	if allowed != 3 {
		t.Errorf("после долгого простоя пропущено %d, а ожидалось 3 — жетонов не больше burst", allowed)
	}
	advance(250 * time.Millisecond) // полжетона
	if l.Allow() {
		t.Error("полжетона — ещё не жетон")
	}
	advance(250 * time.Millisecond)
	if !l.Allow() {
		t.Error("две половинки должны сложиться в жетон")
	}

	l = NewLimiter(1, 50, clock)
	var ok atomic.Int32
	var wg sync.WaitGroup
	for range 200 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if l.Allow() {
				ok.Add(1)
			}
		}()
	}
	wg.Wait()
	if ok.Load() != 50 {
		t.Errorf("200 параллельных запросов при burst 50: пропущено %d", ok.Load())
	}
}

func TestLazy(t *testing.T) {
	var calls atomic.Int32
	l := NewLazy(func() (string, error) {
		calls.Add(1)
		time.Sleep(20 * time.Millisecond)
		return "конфиг", nil
	})
	var wg sync.WaitGroup
	for range 100 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if v, err := l.Get(); v != "конфиг" || err != nil {
				t.Errorf("Get() = %q, %v", v, err)
			}
		}()
	}
	wg.Wait()
	if calls.Load() != 1 {
		t.Errorf("f вызвана %d раз, а должна ровно 1", calls.Load())
	}
	boom := errors.New("нет файла")
	bad := NewLazy(func() (int, error) { calls.Add(1); return 0, boom })
	bad.Get()
	if _, err := bad.Get(); !errors.Is(err, boom) {
		t.Errorf("ошибка тоже запоминается: второй Get вернул %v", err)
	}
}

func TestBatch(t *testing.T) {
	in := make(chan int)
	out := Batch(in, 3, 50*time.Millisecond)
	go func() {
		for i := 1; i <= 7; i++ {
			in <- i
		}
		time.Sleep(120 * time.Millisecond) // 7-й ждёт таймера
		in <- 8
		in <- 9
		close(in)
	}()
	got := drain(t, out)
	want := [][]int{{1, 2, 3}, {4, 5, 6}, {7}, {8, 9}}
	if len(got) != len(want) {
		t.Fatalf("пачки %v, а ожидались %v", got, want)
	}
	for i := range want {
		if !slices.Equal(got[i], want[i]) {
			t.Fatalf("пачки %v, а ожидались %v", got, want)
		}
	}
	empty := make(chan int)
	close(empty)
	if got := drain(t, Batch(empty, 3, time.Second)); len(got) != 0 {
		t.Errorf("из пустого входа пришли пачки %v", got)
	}
}
