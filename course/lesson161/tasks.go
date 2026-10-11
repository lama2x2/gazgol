// Урок 16.1 — Архитектура сервиса.
//
// Порты и ошибки — в ports.go. Здесь — бизнес-логика, транспорт и value object.
// Проверка: go test ./course/lesson161/
package lesson161

import (
	"context"
	"net/http"
)

// Задачи 1, 2 и 5 ★. Покупка объявления.
//
// Правила: нет объявления → ErrNotFound; своё → ErrForbidden; продано → ErrConflict;
// баланс меньше цены → ErrNoMoney; иначе перевод денег продавцу и отметка «продано».
// Всё чтение и запись — в одной транзакции (s.Tx). Уведомление — после коммита,
// его ошибка не влияет на результат.
// ★ Если requestID не пустой и s.Requests != nil — повтор запроса возвращает
// сохранённый результат без повторного списания.
func (s *Service) Buy(ctx context.Context, requestID string, buyerID, adID int64) error {
	// TODO: твой код
	return nil
}

// Задача 3. POST /ads/{id}/buy — тонкий хендлер.
// Покупатель — заголовок X-User-ID, ключ идемпотентности — заголовок Idempotency-Key.
func BuyHandler(svc Buyer) http.Handler {
	// TODO: твой код
	return http.NewServeMux()
}

// Задача 4. Цена — value object. Хранится в копейках.
type Price struct {
	kopecks int64
}

// NewPrice создаёт цену из рублей. Отрицательная — ошибка.
func NewPrice(rub int64) (Price, error) {
	// TODO: твой код
	return Price{}, nil
}

func (p Price) Kopecks() int64 { return p.kopecks }

// Add возвращает новую цену — сумму двух. Исходные не меняются.
func (p Price) Add(o Price) Price {
	// TODO: твой код
	return p
}

// String: целые рубли с разделением тысяч пробелом: "1 500 ₽", "0 ₽".
// Копейки, если есть, через запятую: "99,90 ₽".
func (p Price) String() string {
	// TODO: твой код
	return ""
}
