// Урок 15.2 — Масштабирование данных и кэширование.
//
// Проверка: go test -race ./course/lesson152/
package lesson152

import (
	"context"
	"errors"
	"sync"
	"sync/atomic"
	"time"
)

var ErrNotFound = errors.New("not found")

type Ad struct {
	ID    int64
	Title string
	Price int64
}

// cached — то, что лежит в кэше: объявление или маркер «не найдено».
type cached struct {
	Ad       Ad
	NotFound bool
}

// Cache — кэш (в проде это Redis).
type Cache interface {
	Get(ctx context.Context, key string) (cached, bool)
	Set(ctx context.Context, key string, v cached, ttl time.Duration)
	Delete(ctx context.Context, key string)
}

// DB — источник истины. Get возвращает ErrNotFound, если объявления нет.
type DB interface {
	Get(ctx context.Context, id int64) (Ad, error)
	Save(ctx context.Context, ad Ad) error
}

type Loader struct {
	Cache       Cache
	DB          DB
	TTL         time.Duration
	NegativeTTL time.Duration
}

// Key — ключ кэша для объявления. Уже готово.
func Key(id int64) string { return "ad:" + itoa(id) }

// Задача 1. Cache-aside с негативным кэшированием.
func (l *Loader) Get(ctx context.Context, id int64) (Ad, error) {
	// TODO: твой код
	return l.DB.Get(ctx, id)
}

// Задача 2. Обновить объявление: сначала БД, потом инвалидировать кэш.
func (l *Loader) Update(ctx context.Context, ad Ad) error {
	// TODO: твой код
	return l.DB.Save(ctx, ad)
}

// Задача 3. Консистентное хеширование с виртуальными узлами.
type Ring struct {
	Replicas int // сколько виртуальных точек на узел
	// TODO: поля
}

func (r *Ring) Add(node string) {
	// TODO: твой код
}

// Get возвращает узел для ключа ("" — если узлов нет).
func (r *Ring) Get(key string) string {
	// TODO: твой код
	return ""
}

// Задача 4. Маршрутизация запросов к мастеру и репликам.
type Router struct {
	Primary  string
	Replicas []string
	Lag      time.Duration // сколько после записи пользователя читать с мастера
	Now      func() time.Time

	mu sync.Mutex
	rr atomic.Uint64
	// TODO: поля
}

// MarkWrite отмечает, что user только что записал данные.
func (r *Router) MarkWrite(user string) {
	// TODO: твой код
}

// Pick выбирает базу: запись — мастер; чтение — мастер, если user писал меньше Lag назад,
// иначе реплики по кругу.
func (r *Router) Pick(user string, write bool) string {
	// TODO: твой код
	return r.Primary
}

// Задача 5 ★. Имя месячной партиции: 2026-10-11 → "ads_2026_10".
func PartitionFor(t time.Time) string {
	// TODO: твой код
	return ""
}

// ToDrop возвращает партиции из existing, все данные которых старше retention месяцев
// относительно первого числа месяца now (порядок — как в existing).
//
//	now = 2026-10-11, retention = 3 → граница 2026-07-01: удалить ads_2026_06 и старше, ads_2026_07 оставить.
func ToDrop(now time.Time, retention int, existing []string) []string {
	// TODO: твой код
	return nil
}

func itoa(n int64) string {
	if n == 0 {
		return "0"
	}
	neg := n < 0
	if neg {
		n = -n
	}
	var b [20]byte
	i := len(b)
	for n > 0 {
		i--
		b[i] = byte('0' + n%10)
		n /= 10
	}
	if neg {
		i--
		b[i] = '-'
	}
	return string(b[i:])
}
