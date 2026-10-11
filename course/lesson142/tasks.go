// Урок 14.2 — Паттерны конкурентности уровня middle.
//
// Проверка: go test -race ./course/lesson142/
package lesson142

import (
	"sync"
	"sync/atomic"
	"time"
)

// Задача 1. Свой singleflight.
//
// Do выполняет fn для ключа. Если для этого ключа fn уже выполняется,
// новый вызов ждёт и получает тот же результат. shared == true, если
// результатом поделились больше чем с одним вызывающим.
type Group struct {
	mu sync.Mutex
	// TODO: поля
}

func (g *Group) Do(key string, fn func() (any, error)) (v any, err error, shared bool) {
	// TODO: твой код
	v, err = fn()
	return v, err, false
}

// Задача 2. Шардированный кэш с TTL (16 шардов).
type Cache[V any] struct {
	now func() time.Time
	// TODO: поля
}

func NewCache[V any](now func() time.Time) *Cache[V] {
	// TODO: твой код
	return &Cache[V]{now: now}
}

func (c *Cache[V]) Set(key string, v V, ttl time.Duration) {
	// TODO: твой код
}

// Get возвращает значение, если оно есть и не истекло.
func (c *Cache[V]) Get(key string) (V, bool) {
	// TODO: твой код
	var zero V
	return zero, false
}

// Len — число НЕистёкших записей.
func (c *Cache[V]) Len() int {
	// TODO: твой код
	return 0
}

// Задача 3. Pub/sub, где медленный подписчик не тормозит остальных.
type Broker[T any] struct {
	mu      sync.RWMutex
	dropped atomic.Int64
	// TODO: поля
}

func NewBroker[T any]() *Broker[T] {
	// TODO: твой код
	return &Broker[T]{}
}

// Subscribe создаёт подписку с буфером buf. unsubscribe удаляет подписку
// и закрывает канал; повторный вызов unsubscribe безопасен.
func (b *Broker[T]) Subscribe(buf int) (ch <-chan T, unsubscribe func()) {
	// TODO: твой код
	c := make(chan T)
	return c, func() {}
}

// Publish отправляет v всем подписчикам без блокировки. Если у подписчика
// полный буфер, сообщение для него теряется, а Dropped увеличивается.
func (b *Broker[T]) Publish(v T) {
	// TODO: твой код
}

func (b *Broker[T]) Dropped() int64 { return b.dropped.Load() }

// Задача 4. Мьютекс на ключ: Lock(key) блокирует только этот ключ.
// Когда ключ никто не держит и не ждёт, запись о нём должна удаляться.
type KeyedMutex struct {
	mu sync.Mutex
	// TODO: поля
}

func (k *KeyedMutex) Lock(key string) (unlock func()) {
	// TODO: твой код
	return func() {}
}

// Keys — сколько ключей сейчас хранится внутри (для теста на утечку).
func (k *KeyedMutex) Keys() int {
	// TODO: твой код
	return 0
}

// Задача 5 ★. Конфиг с атомарной подменой.
type Config struct {
	Limit   int
	Version int
}

type ConfigStore struct {
	p atomic.Pointer[Config]
}

func NewConfigStore(c Config) *ConfigStore {
	s := &ConfigStore{}
	s.p.Store(&c)
	return s
}

func (s *ConfigStore) Load() Config { return *s.p.Load() }

// Update применяет f к текущему конфигу и атомарно подменяет его.
// Параллельные Update не должны терять изменения друг друга.
func (s *ConfigStore) Update(f func(Config) Config) {
	// TODO: твой код
	n := f(*s.p.Load())
	s.p.Store(&n)
}
