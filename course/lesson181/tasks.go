// Урок 18.1 — System design: классические задачи лайвкодинга.
//
// Проверка: go test -race ./course/lesson181/
package lesson181

import (
	"sync"
	"time"
)

// Задача 1. LRU-кэш на capacity элементов. Get и Put — O(1).
type LRU[K comparable, V any] struct {
	capacity int
	// TODO: поля
}

func NewLRU[K comparable, V any](capacity int) *LRU[K, V] {
	// TODO: твой код
	return &LRU[K, V]{capacity: capacity}
}

func (c *LRU[K, V]) Get(key K) (V, bool) {
	// TODO: твой код
	var zero V
	return zero, false
}

func (c *LRU[K, V]) Put(key K, val V) {
	// TODO: твой код
}

func (c *LRU[K, V]) Len() int {
	// TODO: твой код
	return 0
}

// Задача 2. Base62 с алфавитом 0-9a-zA-Z.
const alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

func Encode62(n uint64) string {
	// TODO: твой код
	return ""
}

// Decode62 — обратное преобразование. Чужой символ или переполнение uint64 — ошибка.
func Decode62(s string) (uint64, error) {
	// TODO: твой код
	return 0, nil
}

// Задача 3. Snowflake: 41 бит — миллисекунды от Epoch, 10 бит — Node, 12 бит — счётчик.
type Snowflake struct {
	Epoch time.Time
	Node  int64 // 0..1023
	Now   func() time.Time

	mu sync.Mutex
	// TODO: поля
}

// Next возвращает следующий уникальный id. Если часы пошли назад — ошибка.
func (s *Snowflake) Next() (int64, error) {
	// TODO: твой код
	return 0, nil
}

// Задача 4. k самых частых слов: по убыванию частоты, при равенстве — по алфавиту.
func TopK(words []string, k int) []string {
	// TODO: твой код
	return nil
}

// Задача 5 ★. Скользящее окно: не больше Limit запросов за Window на ключ.
type SlidingLimiter struct {
	Limit  int
	Window time.Duration
	Now    func() time.Time

	mu sync.Mutex
	// TODO: поля
}

func (l *SlidingLimiter) Allow(key string) bool {
	// TODO: твой код
	return true
}
