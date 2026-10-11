//lyceum:race — проверка запускается с детектором гонок (-race).

package lesson181

import (
	"fmt"
	"slices"
	"strings"
	"sync"
	"testing"
	"time"
)

func TestLRU(t *testing.T) {
	c := NewLRU[string, int](2)
	c.Put("a", 1)
	c.Put("b", 2)
	if v, ok := c.Get("a"); !ok || v != 1 {
		t.Fatalf("Get(a) = %d, %v", v, ok)
	}
	c.Put("c", 3) // вытесняет b: a недавно читали
	if _, ok := c.Get("b"); ok {
		t.Error("b должен был вытесниться: он самый давно использованный")
	}
	if v, ok := c.Get("a"); !ok || v != 1 {
		t.Error("a вытеснился, хотя его недавно читали")
	}
	c.Put("a", 10) // обновление не меняет размер
	if c.Len() != 2 {
		t.Errorf("Len = %d, а ожидалось 2", c.Len())
	}
	c.Put("d", 4) // теперь давнее всех c
	if _, ok := c.Get("c"); ok {
		t.Error("c должен был вытесниться")
	}
	if v, _ := c.Get("a"); v != 10 {
		t.Errorf("обновлённое значение a = %d", v)
	}
	big := NewLRU[int, int](1000)
	for i := range 5000 {
		big.Put(i, i)
	}
	if big.Len() != 1000 {
		t.Errorf("Len после 5000 вставок в кэш на 1000 = %d", big.Len())
	}
	if _, ok := big.Get(4999); !ok {
		t.Error("последние вставленные элементы должны остаться")
	}
	if _, ok := big.Get(3999); ok {
		t.Error("элемент 3999 должен был вытесниться: остаются последние 1000 (4000..4999)")
	}
}

func TestBase62(t *testing.T) {
	cases := map[uint64]string{0: "0", 61: "Z", 62: "10", 3843: "ZZ", 125: "21"}
	for n, want := range cases {
		if got := Encode62(n); got != want {
			t.Errorf("Encode62(%d) = %q, а ожидалось %q", n, got, want)
		}
	}
	for _, n := range []uint64{0, 1, 999999, 1 << 40, 18446744073709551615} {
		s := Encode62(n)
		back, err := Decode62(s)
		if err != nil || back != n {
			t.Errorf("Decode62(Encode62(%d)=%q) = %d, %v", n, s, back, err)
		}
	}
	if _, err := Decode62("abc-1"); err == nil {
		t.Error("Decode62 с символом '-' должен вернуть ошибку")
	}
	if _, err := Decode62("zzzzzzzzzzzzzzzz"); err == nil {
		t.Error("Decode62 для числа больше uint64 должен вернуть ошибку переполнения")
	}
}

func TestSnowflake(t *testing.T) {
	epoch := time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)
	var mu sync.Mutex
	now := epoch.Add(5 * time.Second)
	ticks := 0
	clock := func() time.Time {
		mu.Lock()
		defer mu.Unlock()
		ticks++
		if ticks%5000 == 0 { // время иногда идёт вперёд
			now = now.Add(time.Millisecond)
		}
		return now
	}
	s := &Snowflake{Epoch: epoch, Node: 7, Now: clock}
	id, err := s.Next()
	if err != nil {
		t.Fatal(err)
	}
	if ms := id >> 22; ms != 5000 {
		t.Errorf("старшие 41 бит = %d мс от эпохи, а ожидалось 5000", ms)
	}
	if node := (id >> 12) & 1023; node != 7 {
		t.Errorf("биты узла = %d, а ожидалось 7", node)
	}
	seen := map[int64]bool{id: true}
	var smu sync.Mutex
	var wg sync.WaitGroup
	for range 8 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			prev := int64(0)
			for range 2000 {
				id, err := s.Next()
				if err != nil {
					t.Error(err)
					return
				}
				if id <= prev {
					t.Errorf("id не растут: %d после %d", id, prev)
					return
				}
				prev = id
				smu.Lock()
				if seen[id] {
					t.Errorf("дубль id %d", id)
				}
				seen[id] = true
				smu.Unlock()
			}
		}()
	}
	wg.Wait()
	if len(seen) != 16001 {
		t.Errorf("уникальных id %d из 16001", len(seen))
	}
	back := &Snowflake{Epoch: epoch, Node: 1}
	tm := epoch.Add(time.Second)
	back.Now = func() time.Time { return tm }
	back.Next()
	tm = tm.Add(-time.Second / 2)
	if _, err := back.Next(); err == nil {
		t.Error("часы пошли назад — Next должен вернуть ошибку")
	}
}

func TestTopK(t *testing.T) {
	text := "go kafka go redis go kafka postgres redis kafka go docker"
	if got := TopK(strings.Fields(text), 3); !slices.Equal(got, []string{"go", "kafka", "redis"}) {
		t.Errorf("TopK(3) = %v, а ожидалось [go kafka redis]", got)
	}
	if got := TopK([]string{"b", "a", "c", "b", "a"}, 2); !slices.Equal(got, []string{"a", "b"}) {
		t.Errorf("при равной частоте — по алфавиту: %v", got)
	}
	if got := TopK([]string{"x"}, 5); !slices.Equal(got, []string{"x"}) {
		t.Errorf("k больше числа слов: %v", got)
	}
	var many []string
	for i := range 10000 {
		many = append(many, fmt.Sprint("w", i%500))
	}
	many = append(many, "w7", "w7", "w42")
	if got := TopK(many, 2); !slices.Equal(got, []string{"w7", "w42"}) {
		t.Errorf("большой вход: %v", got)
	}
}

func TestSlidingLimiter(t *testing.T) {
	now := time.Date(2026, 1, 1, 12, 0, 0, 0, time.UTC)
	var mu sync.Mutex
	clock := func() time.Time { mu.Lock(); defer mu.Unlock(); return now }
	at := func(d time.Duration) {
		mu.Lock()
		now = time.Date(2026, 1, 1, 12, 0, 0, 0, time.UTC).Add(d)
		mu.Unlock()
	}
	l := &SlidingLimiter{Limit: 10, Window: time.Minute, Now: clock}

	at(50 * time.Second) // конец первой минуты
	n := 0
	for range 20 {
		if l.Allow("gosha") {
			n++
		}
	}
	if n != 10 {
		t.Fatalf("за одну минуту пропущено %d из лимита 10", n)
	}
	at(65 * time.Second) // начало следующей минуты: прошлое окно ещё «весит» 75%
	n = 0
	for range 20 {
		if l.Allow("gosha") {
			n++
		}
	}
	if n > 3 {
		t.Errorf("на стыке окон пропущено ещё %d — фиксированное окно пропустило бы 10, скользящее — не больше 3", n)
	}
	if !l.Allow("anya") {
		t.Error("лимиты разных ключей независимы")
	}
	at(3 * time.Minute)
	n = 0
	for range 20 {
		if l.Allow("gosha") {
			n++
		}
	}
	if n != 10 {
		t.Errorf("после долгой паузы пропущено %d, а ожидалось 10", n)
	}
}
