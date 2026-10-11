package lesson101

// Учебная база Барахолки. Её менять не нужно.
// Поиграть с запросами: go run ./course/cmd/sqlrun "SELECT * FROM ads"

import (
	"database/sql"

	_ "modernc.org/sqlite" // драйвер SQLite на чистом Go
)

const schema = `
CREATE TABLE users (
	id   INTEGER PRIMARY KEY,
	name TEXT NOT NULL,
	city TEXT NOT NULL
);
CREATE TABLE ads (
	id       INTEGER PRIMARY KEY,
	user_id  INTEGER NOT NULL REFERENCES users(id),
	title    TEXT NOT NULL,
	price    INTEGER NOT NULL CHECK (price >= 0),
	category TEXT NOT NULL,
	status   TEXT NOT NULL DEFAULT 'active'
);
CREATE TABLE deals (
	id       INTEGER PRIMARY KEY,
	ad_id    INTEGER NOT NULL REFERENCES ads(id),
	buyer_id INTEGER NOT NULL REFERENCES users(id),
	price    INTEGER NOT NULL
);

INSERT INTO users (id, name, city) VALUES
	(1, 'Гоша', 'Казань'), (2, 'Аня', 'Москва'), (3, 'Ильдар', 'Казань'),
	(4, 'Вика', 'Уфа'), (5, 'Петя', 'Москва'), (6, 'Саша', 'Казань');

INSERT INTO ads (id, user_id, title, price, category, status) VALUES
	(1,  1, 'Велосипед Stels', 8000,  'спорт',   'active'),
	(2,  1, 'Самокат',         3000,  'спорт',   'active'),
	(3,  1, 'Шкаф',            12000, 'мебель',  'sold'),
	(4,  2, 'Диван',           25000, 'мебель',  'active'),
	(5,  2, 'Лыжи',            6000,  'спорт',   'sold'),
	(6,  3, 'Чайник',          1500,  'техника', 'active'),
	(7,  3, 'Стул',            1500,  'мебель',  'active'),
	(8,  3, 'Ноутбук',         45000, 'техника', 'active'),
	(9,  4, 'Гантели',         2000,  'спорт',   'active'),
	(10, 4, 'Торшер',          3500,  'мебель',  'sold'),
	(11, 2, 'Кофемашина',      9000,  'техника', 'active'),
	(12, 3, 'Монитор',         7000,  'техника', 'sold'),
	(13, 4, 'Книга про Go',    900,   'книги',   'active');

INSERT INTO deals (ad_id, buyer_id, price) VALUES
	(3, 2, 11000), (5, 1, 6000), (10, 3, 3500), (12, 4, 6500);
`

// OpenFixture открывает новую базу в памяти с учебными данными.
func OpenFixture() (*sql.DB, error) {
	db, err := sql.Open("sqlite", ":memory:")
	if err != nil {
		return nil, err
	}
	db.SetMaxOpenConns(1) // у каждого соединения :memory: своя база — держим одно
	if _, err := db.Exec(schema); err != nil {
		db.Close()
		return nil, err
	}
	return db, nil
}
