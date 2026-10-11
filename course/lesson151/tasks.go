// Урок 15.1 — PostgreSQL изнутри: MVCC, индексы, планы, блокировки.
// Практика на SQLite (схема в db.go); идеи те же, что в PostgreSQL.
//
// Проверка: go test ./course/lesson151/
package lesson151

import (
	"context"
	"database/sql"
)

// Задача 1. Следующая страница АКТИВНЫХ объявлений в порядке (price, id) — keyset-пагинация.
// Параметры: ?1 — price последней строки прошлой страницы, ?2 — её id, ?3 — размер страницы.
// Колонки: id, price.
const NextPageSQL = `
-- TODO: твой запрос
`

// Задача 2. Индекс, с которым этот запрос идёт по индексу (SEARCH) и не сортирует в памяти:
//
//	SELECT id, price FROM ads WHERE category = ? AND status = 'active' ORDER BY price LIMIT 20
const IndexSQL = `
-- TODO: CREATE INDEX ...
`

// Задача 3. Воркер worker забирает до n задач в статусе 'pending': переводит их в 'running',
// записывает себя в worker и возвращает их id. Одна задача не должна достаться двум воркерам.
func ClaimJobs(ctx context.Context, db *sql.DB, worker string, n int) ([]int64, error) {
	// TODO: твой код
	return nil, nil
}

// Задача 4. Оптимистичная блокировка: обновить цену, только если версия совпадает.
// Успех — version увеличивается на 1. Версия устарела — ErrConflict. Нет объявления — ErrNotFound.
func UpdatePrice(ctx context.Context, db *sql.DB, id, version, price int64) error {
	// TODO: твой код
	return nil
}

// Задача 5 ★. Засчитать просмотр объявления за день (одним запросом, без гонок).
func CountView(ctx context.Context, db *sql.DB, adID int64, day string) error {
	// TODO: твой код
	return nil
}
