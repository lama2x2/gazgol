// Урок 6.2 — sync: WaitGroup, Mutex, пул воркеров.
//
// Проверка: go test -race ./course/lesson62/
// Флаг -race включает детектор гонок: он поймает доступ к общим данным без защиты.
package lesson62

import "sync"

// Задача 1. Счётчик просмотров, безопасный для горутин.
//
// Inc и Value могут вызываться из тысячи горутин одновременно.
// Защити поле n мьютексом (поле mu уже есть).
type ViewCounter struct {
	mu sync.Mutex
	n  int
}

func (c *ViewCounter) Inc() {
	// TODO: твой код
}

func (c *ViewCounter) Value() int {
	// TODO: твой код
	return 0
}

// Задача 2. Параллельная загрузка.
//
// Вызови fetch для каждого url одновременно (по горутине на url)
// и дождись всех через sync.WaitGroup.
// Результаты верни в том же порядке, что и urls.
// Подсказка: заранее создай срез нужной длины и пиши в results[i] —
// разные горутины пишут в разные ячейки, мьютекс не нужен.
func FetchAll(urls []string, fetch func(url string) int) []int {
	// TODO: твой код
	return nil
}

// Задача 3 ★. Пул воркеров.
//
// Обработай все jobs функцией f, но одновременно должно работать
// не больше workers горутин. Результаты — в порядке jobs.
// Классическая схема: канал с индексами задач, workers горутин читают
// из него в цикле for range, WaitGroup ждёт, пока все закончат.
func WorkerPool(jobs []int, workers int, f func(int) int) []int {
	// TODO: твой код
	return nil
}
