// Урок 16.2 — Наблюдаемость: свой мини-клиент Prometheus и трейсинг.
//
// Проверка: go test -race ./course/lesson162/
package lesson162

import (
	"io"
	"net/http"
	"sync"
)

// Metric — всё, что умеет записать себя в формате Prometheus.
type Metric interface {
	Write(w io.Writer)
}

type Registry struct {
	metrics []Metric
}

func (r *Registry) Register(m Metric) { r.metrics = append(r.metrics, m) }

// Задача 3. Записать все метрики в порядке регистрации.
func (r *Registry) WriteText(w io.Writer) {
	// TODO: твой код
}

// Задача 1. Счётчик с метками.
type CounterVec struct {
	name, help string
	labels     []string
	mu         sync.Mutex
	// TODO: поля
}

func NewCounterVec(name, help string, labels ...string) *CounterVec {
	// TODO: твой код
	return &CounterVec{name: name, help: help, labels: labels}
}

// Counter — один временной ряд счётчика (конкретные значения меток).
type Counter struct {
	// TODO: поля
}

// With возвращает ряд для значений меток (в том же порядке, что labels).
// Неверное число значений — panic.
func (c *CounterVec) With(values ...string) *Counter {
	// TODO: твой код
	return &Counter{}
}

func (c *Counter) Inc() {
	// TODO: твой код
}

func (c *Counter) Add(v float64) {
	// TODO: твой код
}

func (c *Counter) Value() float64 {
	// TODO: твой код
	return 0
}

// Write: # HELP, # TYPE counter и ряды, отсортированные по значениям меток:
//
//	name{method="GET",status="200"} 5
func (c *CounterVec) Write(w io.Writer) {
	// TODO: твой код
}

// Задача 2. Гистограмма (без меток).
type Histogram struct {
	name, help string
	bounds     []float64 // верхние границы корзин по возрастанию
	mu         sync.Mutex
	// TODO: поля
}

func NewHistogram(name, help string, bounds []float64) *Histogram {
	// TODO: твой код
	return &Histogram{name: name, help: help, bounds: bounds}
}

func (h *Histogram) Observe(v float64) {
	// TODO: твой код
}

func (h *Histogram) Count() uint64 {
	// TODO: твой код
	return 0
}

func (h *Histogram) Sum() float64 {
	// TODO: твой код
	return 0
}

// Write: # HELP, # TYPE histogram, кумулятивные корзины name_bucket{le="..."},
// корзина le="+Inf", затем name_sum и name_count.
func (h *Histogram) Write(w io.Writer) {
	// TODO: твой код
}

// Задача 4. RED-метрики для HTTP.
// requests — счётчик с метками (method, route, status); duration — гистограмма в секундах.
// route — шаблон маршрута из r.Pattern (например "GET /ads/{id}"), если пусто — "unmatched".
func Instrument(next http.Handler, requests *CounterVec, duration *Histogram) http.Handler {
	// TODO: твой код
	return next
}

// Задача 5 ★. Продолжить трейс: вернуть traceparent для исходящего запроса.
// Валидный входящий заголовок — тот же trace id и флаги, новый span id.
// Невалидный или пустой — новый трейс: newTraceID(), newSpanID(), флаги "01".
func ChildTraceparent(incoming string, newTraceID, newSpanID func() string) string {
	// TODO: твой код
	return ""
}
