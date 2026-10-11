// Урок 17.2 — Брокеры сообщений и согласованность данных.
//
// Проверка: go test -race ./course/lesson172/
package lesson172

import "context"

// Задача 1. Номер партиции для ключа (FNV-1a 32 бита по модулю n).
func Partition(key string, n int) int {
	// TODO: твой код
	return 0
}

// ---------- outbox ----------

type Event struct {
	ID    string
	Topic string
	Key   string
	Data  string
}

type Outbox interface {
	FetchUnsent(ctx context.Context, limit int) ([]Event, error) // по порядку записи
	MarkSent(ctx context.Context, ids []string) error
}

type Publisher interface {
	Publish(ctx context.Context, e Event) error
}

type Relay struct {
	Outbox    Outbox
	Publisher Publisher
	Batch     int
}

// Задача 2. Один проход ретранслятора: забрать до Batch неотправленных событий,
// опубликовать по порядку и пометить отправленными. На ошибке публикации —
// пометить уже опубликованные, остановиться и вернуть ошибку.
// Возвращает число опубликованных событий.
func (r *Relay) RunOnce(ctx context.Context) (int, error) {
	// TODO: твой код
	return 0, nil
}

// ---------- идемпотентный консьюмер ----------

type Message struct {
	ID     string
	UserID int64
	Bonus  int64
}

type Store interface {
	WithinTx(ctx context.Context, fn func(ctx context.Context) error) error
	Processed(ctx context.Context, msgID string) (bool, error)
	MarkProcessed(ctx context.Context, msgID string) error
	AddBonus(ctx context.Context, userID, amount int64) error
}

type Consumer struct{ Store Store }

// Задача 3. Начислить бонус из сообщения ровно один раз, даже если сообщение пришло несколько раз.
func (c *Consumer) Handle(ctx context.Context, msg Message) error {
	// TODO: твой код
	return c.Store.AddBonus(ctx, msg.UserID, msg.Bonus)
}

// ---------- сага ----------

type Step struct {
	Name       string
	Do         func(ctx context.Context) error
	Compensate func(ctx context.Context) error
}

// Задача 4. Выполнить шаги по порядку. При ошибке — компенсировать выполненные
// шаги в обратном порядке и вернуть ошибку (вместе с ошибками компенсаций).
func RunSaga(ctx context.Context, steps []Step) error {
	// TODO: твой код
	for _, s := range steps {
		if err := s.Do(ctx); err != nil {
			return err
		}
	}
	return nil
}

// Задача 5 ★. Обработать сообщения n воркерами: сообщения с одним ключом — строго по порядку
// и одним воркером, разные ключи — параллельно. Вернуться после обработки всех.
type KeyedMsg struct {
	Key string
	Seq int
}

func ProcessOrdered(msgs []KeyedMsg, n int, handle func(KeyedMsg)) {
	// TODO: твой код
	for _, m := range msgs {
		handle(m)
	}
}
