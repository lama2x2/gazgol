//lyceum:race — проверка запускается с детектором гонок (-race).

package lesson171

import (
	"context"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func TestBackoff(t *testing.T) {
	one := func() float64 { return 1 }
	half := func() float64 { return 0.5 }
	base, max := 100*time.Millisecond, 2*time.Second
	cases := []struct {
		attempt int
		rnd     func() float64
		want    time.Duration
	}{
		{0, one, 100 * time.Millisecond},
		{1, one, 200 * time.Millisecond},
		{3, one, 800 * time.Millisecond},
		{3, half, 400 * time.Millisecond},
		{5, one, 2 * time.Second},
		{100, one, 2 * time.Second},
		{2, func() float64 { return 0 }, 0},
	}
	for _, c := range cases {
		if got := Backoff(c.attempt, base, max, c.rnd); got != c.want {
			t.Errorf("Backoff(%d) = %v, а ожидалось %v", c.attempt, got, c.want)
		}
	}
}

func TestBreaker(t *testing.T) {
	now := time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)
	var mu sync.Mutex
	clock := func() time.Time { mu.Lock(); defer mu.Unlock(); return now }
	advance := func(d time.Duration) { mu.Lock(); now = now.Add(d); mu.Unlock() }
	b := &Breaker{Threshold: 3, OpenFor: 10 * time.Second, Now: clock}
	boom := errors.New("boom")
	calls := 0
	fail := func() error { calls++; return boom }
	ok := func() error { calls++; return nil }

	b.Call(fail)
	b.Call(fail)
	b.Call(ok) // успех сбрасывает счётчик подряд идущих ошибок
	b.Call(fail)
	b.Call(fail)
	if err := b.Call(ok); err != nil {
		t.Fatalf("после 2 ошибок подряд выключатель ещё закрыт, а Call = %v", err)
	}
	for range 3 {
		b.Call(fail)
	}
	calls = 0
	if err := b.Call(ok); !errors.Is(err, ErrOpen) || calls != 0 {
		t.Fatalf("после 3 ошибок подряд: Call = %v, вызовов fn %d — ожидался ErrOpen без вызова", err, calls)
	}
	advance(5 * time.Second)
	if err := b.Call(ok); !errors.Is(err, ErrOpen) {
		t.Error("через 5с из 10 выключатель должен быть ещё открыт")
	}
	advance(6 * time.Second)
	if err := b.Call(fail); !errors.Is(err, boom) || calls != 1 {
		t.Fatalf("half-open: пробный вызов должен пройти, а Call = %v, вызовов %d", err, calls)
	}
	if err := b.Call(ok); !errors.Is(err, ErrOpen) {
		t.Error("неудачный пробный вызов должен снова открыть выключатель")
	}
	advance(11 * time.Second)
	if err := b.Call(ok); err != nil {
		t.Errorf("успешный пробный вызов: %v", err)
	}
	if err := b.Call(ok); err != nil {
		t.Errorf("после успешной пробы выключатель закрыт: %v", err)
	}

	for range 3 {
		b.Call(fail)
	}
	advance(11 * time.Second)
	release := make(chan struct{})
	var passed atomic.Int32
	var wg sync.WaitGroup
	for range 10 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			b.Call(func() error { passed.Add(1); <-release; return nil })
		}()
	}
	time.Sleep(50 * time.Millisecond)
	close(release)
	wg.Wait()
	if passed.Load() != 1 {
		t.Errorf("в half-open одновременно прошло %d пробных вызовов, а нужен 1", passed.Load())
	}
}

func TestRetrier(t *testing.T) {
	var slept []time.Duration
	r := Retrier{Attempts: 4, Base: 100 * time.Millisecond, Max: time.Second, Rand: func() float64 { return 1 },
		Sleep: func(ctx context.Context, d time.Duration) error { slept = append(slept, d); return nil }}
	calls := 0
	err := r.Do(context.Background(), func(ctx context.Context) error {
		calls++
		if calls < 3 {
			return fmt.Errorf("503: %w", ErrTemporary)
		}
		return nil
	})
	if err != nil || calls != 3 || fmt.Sprint(slept) != "[100ms 200ms]" {
		t.Errorf("успех с 3-й попытки: err %v, вызовов %d, паузы %v — ожидались [100ms 200ms]", err, calls, slept)
	}

	slept, calls = nil, 0
	bad := errors.New("400 bad request")
	err = r.Do(context.Background(), func(ctx context.Context) error { calls++; return bad })
	if !errors.Is(err, bad) || calls != 1 || len(slept) != 0 {
		t.Errorf("постоянная ошибка: err %v, вызовов %d — повторять нельзя", err, calls)
	}

	slept, calls = nil, 0
	err = r.Do(context.Background(), func(ctx context.Context) error { calls++; return ErrTemporary })
	if !errors.Is(err, ErrTemporary) || calls != 4 || len(slept) != 3 {
		t.Errorf("все попытки неудачны: err %v, вызовов %d, пауз %d — ожидалось 4 и 3", err, calls, len(slept))
	}

	slept, calls = nil, 0
	ctx, cancel := context.WithTimeout(context.Background(), 150*time.Millisecond)
	defer cancel()
	err = r.Do(ctx, func(ctx context.Context) error { calls++; return ErrTemporary })
	if calls != 2 || fmt.Sprint(slept) != "[100ms]" {
		t.Errorf("дедлайн 150ms: вызовов %d, паузы %v — после паузы 100ms следующая (200ms) не влезет в бюджет", calls, slept)
	}
}

func TestIdempotency(t *testing.T) {
	var charges atomic.Int32
	slow := make(chan struct{})
	h := Idempotent(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		b, _ := io.ReadAll(r.Body)
		if strings.Contains(string(b), "slow") {
			<-slow
		}
		n := charges.Add(1)
		w.WriteHeader(201)
		fmt.Fprintf(w, `{"charge":%d,"body":%q}`, n, b)
	}))
	send := func(key, body string) *httptest.ResponseRecorder {
		req := httptest.NewRequest("POST", "/payments", strings.NewReader(body))
		if key != "" {
			req.Header.Set("Idempotency-Key", key)
		}
		rec := httptest.NewRecorder()
		h.ServeHTTP(rec, req)
		return rec
	}
	first := send("k1", `{"amount":500}`)
	if first.Code != 201 || !strings.Contains(first.Body.String(), `"charge":1`) {
		t.Fatalf("первый запрос: %d %s", first.Code, first.Body.String())
	}
	again := send("k1", `{"amount":500}`)
	if again.Code != 201 || again.Body.String() != first.Body.String() || again.Header().Get("Idempotent-Replayed") != "true" {
		t.Errorf("повтор: %d %s, Replayed=%q — ожидался сохранённый ответ", again.Code, again.Body.String(), again.Header().Get("Idempotent-Replayed"))
	}
	if charges.Load() != 1 {
		t.Errorf("повтор с тем же ключом выполнил списание снова: списаний %d", charges.Load())
	}
	if rec := send("k1", `{"amount":999}`); rec.Code != 422 {
		t.Errorf("тот же ключ, другое тело: статус %d, а ожидался 422", rec.Code)
	}
	send("", `{"amount":1}`)
	send("", `{"amount":1}`)
	if charges.Load() != 3 {
		t.Errorf("без ключа запросы выполняются как обычно: списаний %d, ожидалось 3", charges.Load())
	}
	done := make(chan *httptest.ResponseRecorder, 1)
	go func() { done <- send("k2", `slow`) }()
	time.Sleep(30 * time.Millisecond)
	dup := make(chan *httptest.ResponseRecorder, 1)
	go func() { dup <- send("k2", `slow`) }()
	select {
	case rec := <-dup:
		if rec.Code != 409 {
			t.Errorf("параллельный дубль, пока первый в работе: статус %d, а ожидался 409", rec.Code)
		}
	case <-time.After(time.Second):
		t.Error("параллельный дубль не получил 409 сразу, а начал выполняться повторно")
	}
	close(slow)
	if rec := <-done; rec.Code != 201 {
		t.Errorf("медленный первый запрос: %d", rec.Code)
	}
}

func TestOutgoingTimeout(t *testing.T) {
	if d, ok := OutgoingTimeout(context.Background(), 50*time.Millisecond, time.Second); d != time.Second || !ok {
		t.Errorf("без дедлайна: %v, %v — ожидалось 1s, true", d, ok)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 500*time.Millisecond)
	defer cancel()
	d, ok := OutgoingTimeout(ctx, 100*time.Millisecond, time.Second)
	if !ok || d > 400*time.Millisecond || d < 350*time.Millisecond {
		t.Errorf("дедлайн 500ms, резерв 100ms: %v, %v — ожидалось около 400ms", d, ok)
	}
	if d, ok := OutgoingTimeout(ctx, 100*time.Millisecond, 200*time.Millisecond); d != 200*time.Millisecond || !ok {
		t.Errorf("max 200ms меньше бюджета: %v, %v", d, ok)
	}
	short, cancel2 := context.WithTimeout(context.Background(), 30*time.Millisecond)
	defer cancel2()
	if d, ok := OutgoingTimeout(short, 50*time.Millisecond, time.Second); ok || d != 0 {
		t.Errorf("бюджет меньше резерва: %v, %v — ожидалось 0, false", d, ok)
	}
}
