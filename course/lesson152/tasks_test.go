//lyceum:race — проверка запускается с детектором гонок (-race).

package lesson152

import (
	"context"
	"errors"
	"fmt"
	"slices"
	"strings"
	"sync"
	"testing"
	"time"
)

type fakeCache struct {
	mu  sync.Mutex
	m   map[string]cached
	ttl map[string]time.Duration
	log *[]string
}

func (c *fakeCache) Get(_ context.Context, k string) (cached, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()
	v, ok := c.m[k]
	return v, ok
}
func (c *fakeCache) Set(_ context.Context, k string, v cached, ttl time.Duration) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.m[k], c.ttl[k] = v, ttl
	*c.log = append(*c.log, "cache.Set "+k)
}
func (c *fakeCache) Delete(_ context.Context, k string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	delete(c.m, k)
	*c.log = append(*c.log, "cache.Delete "+k)
}

type fakeDB struct {
	mu   sync.Mutex
	ads  map[int64]Ad
	gets int
	fail error
	log  *[]string
}

func (d *fakeDB) Get(_ context.Context, id int64) (Ad, error) {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.gets++
	if d.fail != nil {
		return Ad{}, d.fail
	}
	ad, ok := d.ads[id]
	if !ok {
		return Ad{}, ErrNotFound
	}
	return ad, nil
}
func (d *fakeDB) Save(_ context.Context, ad Ad) error {
	d.mu.Lock()
	defer d.mu.Unlock()
	*d.log = append(*d.log, "db.Save")
	if d.fail != nil {
		return d.fail
	}
	d.ads[ad.ID] = ad
	return nil
}

func setup() (*Loader, *fakeCache, *fakeDB, *[]string) {
	log := &[]string{}
	c := &fakeCache{m: map[string]cached{}, ttl: map[string]time.Duration{}, log: log}
	d := &fakeDB{ads: map[int64]Ad{1: {1, "Шкаф", 3000}}, log: log}
	return &Loader{Cache: c, DB: d, TTL: time.Minute, NegativeTTL: 5 * time.Second}, c, d, log
}

func TestCacheAside(t *testing.T) {
	l, c, d, _ := setup()
	ctx := context.Background()
	for range 3 {
		ad, err := l.Get(ctx, 1)
		if err != nil || ad.Title != "Шкаф" {
			t.Fatalf("Get(1) = %+v, %v", ad, err)
		}
	}
	if d.gets != 1 {
		t.Errorf("3 чтения одного объявления сходили в БД %d раз, а нужно 1", d.gets)
	}
	if c.ttl[Key(1)] != time.Minute {
		t.Errorf("TTL найденного = %v, а ожидался TTL лоадера", c.ttl[Key(1)])
	}
	for range 3 {
		if _, err := l.Get(ctx, 404); !errors.Is(err, ErrNotFound) {
			t.Fatalf("Get(404) = %v, а ожидался ErrNotFound", err)
		}
	}
	if d.gets != 2 {
		t.Errorf("3 запроса несуществующего пробили кэш до БД %d раз, а нужно 1 (негативное кэширование)", d.gets-1)
	}
	if c.ttl[Key(404)] != 5*time.Second {
		t.Errorf("TTL маркера «не найдено» = %v, а ожидался NegativeTTL", c.ttl[Key(404)])
	}
	d.fail = errors.New("connection refused")
	if _, err := l.Get(ctx, 7); err == nil || errors.Is(err, ErrNotFound) {
		t.Errorf("при ошибке БД Get(7) = %v", err)
	}
	if _, ok := c.m[Key(7)]; ok {
		t.Error("ошибку БД нельзя кэшировать")
	}
}

func TestUpdateInvalidates(t *testing.T) {
	l, c, _, log := setup()
	ctx := context.Background()
	l.Get(ctx, 1)
	*log = nil
	if err := l.Update(ctx, Ad{1, "Шкаф-купе", 3500}); err != nil {
		t.Fatal(err)
	}
	if strings.Join(*log, ", ") != "db.Save, cache.Delete ad:1" {
		t.Errorf("порядок операций при обновлении: %v, а нужно: db.Save, затем cache.Delete", *log)
	}
	if ad, _ := l.Get(ctx, 1); ad.Title != "Шкаф-купе" {
		t.Errorf("после обновления Get вернул старое: %+v", ad)
	}
	l2, c2, d2, log2 := setup()
	l2.Get(ctx, 1)
	*log2 = nil
	d2.fail = errors.New("db down")
	if err := l2.Update(ctx, Ad{1, "x", 1}); err == nil {
		t.Error("ошибка БД при Update должна вернуться")
	}
	if _, ok := c2.m[Key(1)]; !ok || len(*log2) != 1 {
		t.Errorf("при ошибке БД кэш трогать не нужно, а лог: %v", *log2)
	}
	_ = c
}

func TestRing(t *testing.T) {
	r := &Ring{Replicas: 150}
	if r.Get("x") != "" {
		t.Error("пустое кольцо должно вернуть \"\"")
	}
	for _, n := range []string{"db-a", "db-b", "db-c", "db-d"} {
		r.Add(n)
	}
	keys := make([]string, 20000)
	before := make([]string, len(keys))
	count := map[string]int{}
	for i := range keys {
		keys[i] = fmt.Sprintf("user:%d", i)
		before[i] = r.Get(keys[i])
		count[before[i]]++
		if r.Get(keys[i]) != before[i] {
			t.Fatal("Get для одного ключа возвращает разные узлы")
		}
	}
	for n, c := range count {
		if c < 3000 || c > 7000 {
			t.Errorf("на узел %s попало %d ключей из 20000 — распределение неравномерное (нужно 3000..7000)", n, c)
		}
	}
	r.Add("db-e")
	moved := 0
	for i, k := range keys {
		if after := r.Get(k); after != before[i] {
			moved++
			if after != "db-e" {
				t.Fatalf("ключ %s переехал с %s на %s — при добавлении узла ключи должны переезжать только на новый", k, before[i], after)
			}
		}
	}
	if share := float64(moved) / float64(len(keys)); share > 0.35 || share < 0.1 {
		t.Errorf("при добавлении 5-го узла переехало %.0f%% ключей, а ожидается около 20%%", share*100)
	}
}

func TestRouter(t *testing.T) {
	now := time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)
	var mu sync.Mutex
	r := &Router{Primary: "primary", Replicas: []string{"r1", "r2"}, Lag: 2 * time.Second,
		Now: func() time.Time { mu.Lock(); defer mu.Unlock(); return now }}
	advance := func(d time.Duration) { mu.Lock(); now = now.Add(d); mu.Unlock() }
	if r.Pick("gosha", true) != "primary" {
		t.Error("запись должна идти на мастер")
	}
	var got []string
	for range 4 {
		got = append(got, r.Pick("gosha", false))
	}
	slices.Sort(got)
	if !slices.Equal(got, []string{"r1", "r1", "r2", "r2"}) {
		t.Errorf("4 чтения распределились так: %v — нужны реплики по кругу", got)
	}
	r.MarkWrite("gosha")
	if r.Pick("gosha", false) != "primary" {
		t.Error("сразу после своей записи пользователь должен читать с мастера")
	}
	if p := r.Pick("anya", false); p == "primary" {
		t.Error("другой пользователь может читать с реплики")
	}
	advance(3 * time.Second)
	if r.Pick("gosha", false) == "primary" {
		t.Error("через 3с (Lag 2с) снова можно читать с реплики")
	}
	var wg sync.WaitGroup
	for i := range 50 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			u := fmt.Sprint("u", i%5)
			r.MarkWrite(u)
			r.Pick(u, false)
		}()
	}
	wg.Wait()
}

func TestPartitions(t *testing.T) {
	if got := PartitionFor(time.Date(2026, 10, 11, 15, 0, 0, 0, time.UTC)); got != "ads_2026_10" {
		t.Errorf("PartitionFor(2026-10-11) = %q", got)
	}
	if got := PartitionFor(time.Date(2027, 1, 1, 0, 0, 0, 0, time.UTC)); got != "ads_2027_01" {
		t.Errorf("PartitionFor(2027-01-01) = %q", got)
	}
	existing := []string{"ads_2025_12", "ads_2026_05", "ads_2026_06", "ads_2026_07", "ads_2026_08", "ads_2026_10"}
	now := time.Date(2026, 10, 11, 0, 0, 0, 0, time.UTC)
	if got := ToDrop(now, 3, existing); !slices.Equal(got, []string{"ads_2025_12", "ads_2026_05", "ads_2026_06"}) {
		t.Errorf("ToDrop(2026-10-11, 3 мес.) = %v", got)
	}
	jan := time.Date(2027, 1, 20, 0, 0, 0, 0, time.UTC)
	if got := ToDrop(jan, 2, []string{"ads_2026_10", "ads_2026_11", "ads_2026_12"}); !slices.Equal(got, []string{"ads_2026_10"}) {
		t.Errorf("ToDrop через границу года = %v", got)
	}
}
