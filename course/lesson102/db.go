package lesson102

// Схема и открытие базы. Менять не нужно.

import (
	"database/sql"
	"errors"

	_ "modernc.org/sqlite"
)

var (
	ErrNotFound    = errors.New("not found")
	ErrAlreadySold = errors.New("already sold")
	ErrNoMoney     = errors.New("not enough money")
	ErrOwnAd       = errors.New("cannot buy own ad")
)

const schema = `
CREATE TABLE users (
	id      INTEGER PRIMARY KEY,
	name    TEXT NOT NULL,
	balance INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0)
);
CREATE TABLE ads (
	id          INTEGER PRIMARY KEY,
	user_id     INTEGER NOT NULL REFERENCES users(id),
	title       TEXT NOT NULL,
	description TEXT,
	price       INTEGER NOT NULL CHECK (price >= 0),
	status      TEXT NOT NULL DEFAULT 'active'
);
CREATE TABLE deals (
	id       INTEGER PRIMARY KEY,
	ad_id    INTEGER NOT NULL REFERENCES ads(id),
	buyer_id INTEGER NOT NULL REFERENCES users(id),
	price    INTEGER NOT NULL
);
INSERT INTO users (id, name, balance) VALUES (1, 'Гоша', 10000), (2, 'Аня', 3000), (3, 'Ильдар', 0);
`

type Ad struct {
	ID          int64
	UserID      int64
	Title       string
	Description *string // nil — NULL в базе
	Price       int64
	Status      string // "active" или "sold"
}

type Store struct {
	db *sql.DB
}

// OpenStore создаёт базу в памяти со схемой и тремя пользователями.
// В пуле ровно одно соединение — так честнее видно ошибки с транзакциями.
func OpenStore() (*Store, error) {
	db, err := sql.Open("sqlite", ":memory:")
	if err != nil {
		return nil, err
	}
	db.SetMaxOpenConns(1)
	if _, err := db.Exec(schema); err != nil {
		db.Close()
		return nil, err
	}
	return &Store{db: db}, nil
}

func (s *Store) Close() error { return s.db.Close() }
