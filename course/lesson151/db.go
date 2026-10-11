package lesson151

// Учебная база. Менять не нужно.

import (
	"database/sql"
	"errors"
	"fmt"

	_ "modernc.org/sqlite"
)

var (
	ErrNotFound = errors.New("not found")
	ErrConflict = errors.New("conflict: объявление изменили раньше")
)

const schema = `
CREATE TABLE ads (
	id       INTEGER PRIMARY KEY,
	title    TEXT NOT NULL,
	price    INTEGER NOT NULL,
	category TEXT NOT NULL,
	status   TEXT NOT NULL DEFAULT 'active',
	version  INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE jobs (
	id     INTEGER PRIMARY KEY,
	status TEXT NOT NULL DEFAULT 'pending',
	worker TEXT
);
CREATE TABLE ad_views (
	ad_id INTEGER NOT NULL,
	day   TEXT NOT NULL,
	views INTEGER NOT NULL,
	PRIMARY KEY (ad_id, day)
);
`

// Open создаёт базу в памяти: 2000 объявлений в 5 категориях, 30 задач в очереди.
func Open() (*sql.DB, error) {
	db, err := sql.Open("sqlite", ":memory:")
	if err != nil {
		return nil, err
	}
	db.SetMaxOpenConns(1)
	if _, err := db.Exec(schema); err != nil {
		return nil, err
	}
	cats := []string{"мебель", "техника", "спорт", "одежда", "книги"}
	tx, _ := db.Begin()
	for i := 1; i <= 2000; i++ {
		status := "active"
		if i%7 == 0 {
			status = "sold"
		}
		price := (i * 37) % 500 * 100 // много одинаковых цен — для честной пагинации
		if _, err := tx.Exec("INSERT INTO ads (id, title, price, category, status) VALUES (?, ?, ?, ?, ?)",
			i, fmt.Sprintf("Объявление %d", i), price, cats[i%5], status); err != nil {
			return nil, err
		}
	}
	for i := 1; i <= 30; i++ {
		tx.Exec("INSERT INTO jobs (id) VALUES (?)", i)
	}
	return db, tx.Commit()
}
