// Урок 10.2 — Go и база данных: database/sql.
//
// Схема и типы — в db.go. Плейсхолдеры в SQLite — «?».
// Проверка: go test ./course/lesson102/
package lesson102

import "context"

// Задача 1. Вставь объявление (ID и Status из ad игнорируются, статус — по умолчанию 'active').
// Верни id новой записи.
func (s *Store) Create(ctx context.Context, ad Ad) (int64, error) {
	// TODO: твой код
	return 0, nil
}

// Задача 2. Найди объявление по id. Описание может быть NULL → Description == nil.
// Нет такого — ошибка, для которой errors.Is(err, ErrNotFound).
func (s *Store) Get(ctx context.Context, id int64) (Ad, error) {
	// TODO: твой код
	return Ad{}, nil
}

// Filter — условия поиска. Нулевые значения означают «не фильтровать».
type Filter struct {
	UserID   int64
	Status   string
	MaxPrice int64
	Limit    int // 0 → 20
	Offset   int
}

// Задача 3. Список объявлений по фильтру, по возрастанию id, с LIMIT и OFFSET.
// Значения подставляй ТОЛЬКО через параметры запроса.
func (s *Store) List(ctx context.Context, f Filter) ([]Ad, error) {
	// TODO: твой код
	return nil, nil
}

// Задача 4. Покупка — в одной транзакции:
//   - объявления нет → ErrNotFound; уже продано → ErrAlreadySold;
//   - покупатель — сам продавец → ErrOwnAd; денег меньше цены → ErrNoMoney;
//   - иначе: списать цену с покупателя, начислить продавцу, статус 'sold', запись в deals.
//
// При любой ошибке в базе ничего не должно измениться.
func (s *Store) Buy(ctx context.Context, adID, buyerID int64) error {
	// TODO: твой код
	return nil
}

// Задача 5 ★. Вставь все объявления в одной транзакции через подготовленный запрос.
// Если хоть одно не вставилось — не должно вставиться ни одно.
func (s *Store) BulkCreate(ctx context.Context, ads []Ad) error {
	// TODO: твой код
	return nil
}
