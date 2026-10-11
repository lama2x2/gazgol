//lyceum:race — проверка запускается с детектором гонок (-race).

package lesson142

import (
	"errors"
	"fmt"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func TestSingleflight(t *testing.T) {
	var g Group
	var calls atomic.Int32
	var sharedCount atomic.Int32
	start := make(chan struct{})
	var wg sync.WaitGroup
	for range 100 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			<-start
			v, err, shared := g.Do("ad:42", func() (any, error) {
				calls.Add(1)
				time.Sleep(30 * time.Millisecond)
				return "Шкаф", nil
			})
			if v != "Шкаф" || err != nil {
				t.Errorf("Do = %v, %v", v, err)
			}
			if shared {
				sharedCount.Add(1)
			}
		}()
	}
	close(start)
	wg.Wait()
	if calls.Load() != 1 {
		t.Errorf("100 одновременных Do по одному ключу вызвали fn %d раз, а нужно 1", calls.Load())
	}
	if sharedCount.Load() < 2 {
		t.Errorf("shared = true вернулся %d раз — результатом поделились", sharedCount.Load())
	}
	boom := errors.New("db down")
	if _, err, _ := g.Do("ad:42", func() (any, error) { calls.Add(1); return nil, boom }); !errors.Is(err, boom) {
		t.Errorf("после завершения ключ должен освободиться: новый Do вернул %v", err)
	}
	if calls.Load() != 2 {
		t.Error("новый Do после завершения прошлого должен снова вызвать fn")
	}
	var a, b atomic.Int32
	var wg2 sync.WaitGroup
	for i := range 2 {
		wg2.Add(1)
		go func() {
			defer wg2.Done()
			g.Do(fmt.Sprint("k", i), func() (any, error) {
				if i == 0 {
					a.Add(1)
				} else {
					b.Add(1)
				}
				time.Sleep(10 * time.Millisecond)
				return nil, nil
			})
		}()
	}
	wg2.Wait()
	if a.Load() != 1 || b.Load() != 1 {
		t.Error("разные ключи должны выполняться независимо")
	}
}

type clock struct {
	mu  sync.Mutex
	now time.Time
}

func (c *clock) Now() time.Time      { c.mu.Lock(); defer c.mu.Unlock(); return c.now }
func (c *clock) Add(d time.Duration) { c.mu.Lock(); c.now = c.now.Add(d); c.mu.Unlock() }

func TestShardedCache(t *testing.T) {
	clk := &clock{now: time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)}
	c := NewCache[int](clk.Now)
	c.Set("a", 1, time.Minute)
	c.Set("b", 2, 10*time.Second)
	if v, ok := c.Get("a"); !ok || v != 1 {
		t.Errorf("Get(a) = %d, %v", v, ok)
	}
	if _, ok := c.Get("нет"); ok {
		t.Error("Get(нет) нашёл несуществующий ключ")
	}
	if c.Len() != 2 {
		t.Errorf("Len = %d, а ожидалось 2", c.Len())
	}
	clk.Add(30 * time.Second)
	if _, ok := c.Get("b"); ok {
		t.Error("ключ b с TTL 10s всё ещё находится через 30s")
	}
	if c.Len() != 1 {
		t.Errorf("после истечения b: Len = %d, а ожидалось 1", c.Len())
	}
	c.Set("a", 100, time.Minute)
	if v, _ := c.Get("a"); v != 100 {
		t.Errorf("перезапись a: Get = %d", v)
	}
	var wg sync.WaitGroup
	for g := range 16 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := range 500 {
				k := fmt.Sprintf("k%d-%d", g, i)
				c.Set(k, i, time.Hour)
				if v, ok := c.Get(k); !ok || v != i {
					t.Errorf("Get(%s) сразу после Set = %d, %v", k, v, ok)
					return
				}
			}
		}()
	}
	wg.Wait()
	if c.Len() != 16*500+1 {
		t.Errorf("Len после параллельной записи = %d, а ожидалось %d", c.Len(), 16*500+1)
	}
}

func TestBroker(t *testing.T) {
	b := NewBroker[int]()
	fast, unsubFast := b.Subscribe(100)
	slow, unsubSlow := b.Subscribe(2)
	done := make(chan struct{})
	go func() {
		for i := range 10 {
			b.Publish(i)
		}
		close(done)
	}()
	select {
	case <-done:
	case <-time.After(time.Second):
		t.Fatal("Publish заблокировался на медленном подписчике")
	}
	if len(fast) != 10 {
		t.Errorf("быстрый подписчик получил %d из 10", len(fast))
	}
	if len(slow) != 2 || b.Dropped() != 8 {
		t.Errorf("медленный: в буфере %d, потеряно %d — ожидались 2 и 8", len(slow), b.Dropped())
	}
	unsubSlow()
	unsubSlow()
	if !drainClosed(slow) {
		t.Fatal("после unsubscribe канал подписчика должен закрыться")
	}
	b.Publish(99)
	if len(fast) != 11 {
		t.Error("после отписки медленного быстрый должен продолжать получать")
	}
	unsubFast()
	var wg sync.WaitGroup
	for range 4 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			ch, unsub := b.Subscribe(1)
			for range 50 {
				b.Publish(1)
			}
			unsub()
			drainClosed(ch)
		}()
	}
	wg.Wait()
}

// drainClosed вычитывает канал и сообщает, закрылся ли он за секунду.
func drainClosed[T any](ch <-chan T) bool {
	deadline := time.After(time.Second)
	for {
		select {
		case _, ok := <-ch:
			if !ok {
				return true
			}
		case <-deadline:
			return false
		}
	}
}

func TestKeyedMutex(t *testing.T) {
	var k KeyedMutex
	counters := map[string]*int{"a": new(int), "b": new(int)}
	var wg sync.WaitGroup
	for _, key := range []string{"a", "b"} {
		for range 20 {
			wg.Add(1)
			go func() {
				defer wg.Done()
				for range 100 {
					unlock := k.Lock(key)
					*counters[key]++
					unlock()
				}
			}()
		}
	}
	wg.Wait()
	if *counters["a"] != 2000 || *counters["b"] != 2000 {
		t.Errorf("счётчики a=%d b=%d, а ожидалось по 2000", *counters["a"], *counters["b"])
	}
	if k.Keys() != 0 {
		t.Errorf("после всех unlock внутри осталось %d ключей — утечка памяти", k.Keys())
	}
	unlockA := k.Lock("a")
	got := make(chan struct{})
	go func() { u := k.Lock("b"); u(); close(got) }()
	select {
	case <-got:
	case <-time.After(time.Second):
		t.Fatal("Lock(b) ждёт, пока держат a — разные ключи не должны мешать друг другу")
	}
	waited := make(chan struct{})
	go func() { u := k.Lock("a"); close(waited); u() }()
	select {
	case <-waited:
		t.Fatal("второй Lock(a) прошёл, пока первый не отпущен")
	case <-time.After(50 * time.Millisecond):
	}
	unlockA()
	<-waited
}

func TestConfigUpdate(t *testing.T) {
	s := NewConfigStore(Config{Limit: 10})
	var wg sync.WaitGroup
	for range 200 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			s.Update(func(c Config) Config {
				c.Version++
				return c
			})
		}()
	}
	wg.Wait()
	if c := s.Load(); c.Version != 200 || c.Limit != 10 {
		t.Errorf("после 200 параллельных Update: %+v — потеряны обновления", c)
	}
}
