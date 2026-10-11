// Урок 7.2 — Map, интерфейсы и дженерики изнутри.
//
// Проверка: go test ./course/lesson72/
package lesson72

import (
	"cmp"
	"errors"
	"time"
)

// Задача 1. Обобщённое множество.
//
// Set хранит уникальные значения любого сравнимого типа.
type Set[T comparable] map[T]struct{}

// NewSet создаёт множество из перечисленных элементов (может быть пустым).
func NewSet[T comparable](items ...T) Set[T] {
	// TODO: твой код
	return nil
}

func (s Set[T]) Add(v T) {
	// TODO: твой код
}

func (s Set[T]) Has(v T) bool {
	// TODO: твой код
	return false
}

func (s Set[T]) Remove(v T) {
	// TODO: твой код
}

func (s Set[T]) Len() int {
	// TODO: твой код
	return 0
}

// Задача 2. Группировка.
//
// Разложи элементы по ключу, который возвращает key. Порядок внутри группы — как во входном слайсе.
//
//	GroupBy([]string{"kiwi", "apple", "avocado"}, первая буква) → map[a:[apple avocado] k:[kiwi]]
func GroupBy[T any, K comparable](items []T, key func(T) K) map[K][]T {
	// TODO: твой код
	return nil
}

// Задача 3. Ключи по порядку.
//
// Верни ключи map, отсортированные по возрастанию.
func SortedKeys[K cmp.Ordered, V any](m map[K]V) []K {
	// TODO: твой код
	return nil
}

// Задача 4. Functional options.
//
// Client — HTTP-клиент к API Барахолки. По умолчанию: Timeout 5s, Retries 3.
type Client struct {
	BaseURL string
	Timeout time.Duration
	Retries int
}

type Option func(*Client)

// WithTimeout задаёт таймаут запроса.
func WithTimeout(d time.Duration) Option {
	// TODO: твой код
	return func(c *Client) {}
}

// WithRetries задаёт число повторов. Отрицательное значение игнорируется.
func WithRetries(n int) Option {
	// TODO: твой код
	return func(c *Client) {}
}

// NewClient создаёт клиента со значениями по умолчанию и применяет опции по порядку.
func NewClient(baseURL string, opts ...Option) *Client {
	// TODO: твой код
	return nil
}

// Задача 5 ★. Найди и исправь баг.
//
// Validate проверяет объявление. Проверки правильные, но тест жалуется,
// что для корректного объявления функция возвращает «ошибку». Почини.

// AdError — ошибка валидации объявления.
type AdError struct{ Reason string }

func (e *AdError) Error() string { return "объявление: " + e.Reason }

var errEmpty = errors.New("пустое объявление")

func Validate(title string, price int) error {
	if title == "" && price == 0 {
		return errEmpty
	}
	var err *AdError
	if title == "" {
		err = &AdError{Reason: "нет названия"}
	} else if price < 0 {
		err = &AdError{Reason: "цена меньше нуля"}
	}
	return err
}
