//lyceum:race — проверка запускается с детектором гонок (-race).

package lesson141

import (
	"context"
	"errors"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func within(t *testing.T, d time.Duration, what string, f func()) {
	t.Helper()
	done := make(chan struct{})
	go func() { f(); close(done) }()
	select {
	case <-done:
	case <-time.After(d):
		t.Fatalf("%s: зависло дольше %v", what, d)
	}
}

func TestSpinLock(t *testing.T) {
	var l SpinLock
	n := 0
	within(t, 5*time.Second, "50 горутин × 1000 инкрементов", func() {
		var wg sync.WaitGroup
		for range 50 {
			wg.Add(1)
			go func() {
				defer wg.Done()
				for range 1000 {
					l.Lock()
					n++
					l.Unlock()
				}
			}()
		}
		wg.Wait()
	})
	if n != 50000 {
		t.Errorf("счётчик = %d, а ожидалось 50000 — замок пропускает двоих сразу", n)
	}
}

func TestStoreMax(t *testing.T) {
	var a atomic.Int64
	var wg sync.WaitGroup
	for g := range 20 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := range 1000 {
				StoreMax(&a, int64(g*1000+i))
			}
		}()
	}
	wg.Wait()
	if a.Load() != 19999 {
		t.Errorf("максимум = %d, а ожидалось 19999", a.Load())
	}
	StoreMax(&a, 5)
	if a.Load() != 19999 {
		t.Error("меньшее значение затёрло максимум")
	}
}

func TestSemaphore(t *testing.T) {
	s := NewSemaphore(3)
	var running, peak atomic.Int32
	var wg sync.WaitGroup
	for range 20 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if err := s.Acquire(context.Background()); err != nil {
				t.Error(err)
				return
			}
			n := running.Add(1)
			for {
				p := peak.Load()
				if n <= p || peak.CompareAndSwap(p, n) {
					break
				}
			}
			time.Sleep(5 * time.Millisecond)
			running.Add(-1)
			s.Release()
		}()
	}
	within(t, 3*time.Second, "20 задач через семафор на 3", wg.Wait)
	if peak.Load() != 3 {
		t.Errorf("одновременно держали семафор %d, а ожидалось ровно 3", peak.Load())
	}

	full := NewSemaphore(1)
	full.Acquire(context.Background())
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Millisecond)
	defer cancel()
	start := time.Now()
	if err := full.Acquire(ctx); !errors.Is(err, context.DeadlineExceeded) || time.Since(start) > time.Second {
		t.Errorf("Acquire на занятом семафоре с таймаутом 30ms: %v за %v", err, time.Since(start))
	}
	full.Release()
	within(t, time.Second, "Acquire после Release", func() { full.Acquire(context.Background()) })
}

func TestOnceErr(t *testing.T) {
	var o OnceErr
	calls := 0
	fail := errors.New("нет сети")
	if err := o.Do(func() error { calls++; return fail }); !errors.Is(err, fail) {
		t.Errorf("первый неудачный Do = %v", err)
	}
	if err := o.Do(func() error { calls++; return nil }); err != nil {
		t.Errorf("второй Do (успешный) = %v", err)
	}
	if err := o.Do(func() error { calls++; return fail }); err != nil || calls != 2 {
		t.Errorf("после успеха Do не должен вызывать f: вызовов %d, err %v", calls, err)
	}

	var o2 OnceErr
	var active, maxActive, total atomic.Int32
	var wg sync.WaitGroup
	for range 50 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			o2.Do(func() error {
				n := active.Add(1)
				if n > maxActive.Load() {
					maxActive.Store(n)
				}
				time.Sleep(time.Millisecond)
				active.Add(-1)
				total.Add(1)
				return nil
			})
		}()
	}
	wg.Wait()
	if total.Load() != 1 || maxActive.Load() != 1 {
		t.Errorf("50 параллельных Do: f вызвана %d раз (одновременно до %d), а нужно ровно 1", total.Load(), maxActive.Load())
	}
}

func TestBarrier(t *testing.T) {
	b := NewBarrier(4)
	var phase [3]atomic.Int32
	within(t, 3*time.Second, "4 горутины × 3 раунда барьера", func() {
		var wg sync.WaitGroup
		for g := range 4 {
			wg.Add(1)
			go func() {
				defer wg.Done()
				for round := range 3 {
					time.Sleep(time.Duration(g) * time.Millisecond)
					phase[round].Add(1)
					b.Wait()
					if got := phase[round].Load(); got != 4 {
						t.Errorf("раунд %d: прошли барьер, когда пришли только %d из 4", round, got)
					}
				}
			}()
		}
		wg.Wait()
	})
}
