package lesson161

// Доменные ошибки и порты (интерфейсы), которые нужны сервису. Менять не нужно.

import (
	"context"
	"errors"
)

var (
	ErrNotFound  = errors.New("объявление не найдено")
	ErrForbidden = errors.New("нельзя купить своё объявление")
	ErrConflict  = errors.New("объявление уже продано")
	ErrNoMoney   = errors.New("недостаточно средств")
)

type Ad struct {
	ID       int64
	SellerID int64
	Price    int64
	Sold     bool
}

type Ads interface {
	Get(ctx context.Context, id int64) (Ad, error) // ErrNotFound, если нет
	MarkSold(ctx context.Context, id int64) error
}

type Wallets interface {
	Balance(ctx context.Context, userID int64) (int64, error)
	Transfer(ctx context.Context, from, to, amount int64) error
}

// TxManager выполняет fn в транзакции: ошибка fn — откат, nil — коммит.
// Репозитории должны получать ctx, который передан в fn.
type TxManager interface {
	WithinTx(ctx context.Context, fn func(ctx context.Context) error) error
}

type Notifier interface {
	AdSold(ctx context.Context, adID, buyerID int64) error
}

// Requests хранит результаты обработанных запросов для идемпотентности.
type Requests interface {
	// Seen: done — запрос уже обрабатывали, result — его результат (nil или доменная ошибка).
	Seen(ctx context.Context, requestID string) (done bool, result error, err error)
	Save(ctx context.Context, requestID string, result error) error
}

type Service struct {
	Ads      Ads
	Wallets  Wallets
	Tx       TxManager
	Notify   Notifier
	Requests Requests // может быть nil — тогда без идемпотентности
}

// Buyer — то, что нужно HTTP-хендлеру от сервиса.
type Buyer interface {
	Buy(ctx context.Context, requestID string, buyerID, adID int64) error
}
