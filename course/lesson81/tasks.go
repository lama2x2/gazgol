// Урок 8.1 — Ошибки как следует.
//
// Проверка: go test ./course/lesson81/
package lesson81

import "errors"

var (
	ErrNotFound  = errors.New("not found")
	ErrForbidden = errors.New("forbidden")
	ErrPermanent = errors.New("permanent error") // повторять бесполезно
)

// FieldError — ошибка в конкретном поле формы.
type FieldError struct {
	Field string
	Msg   string
}

func (e *FieldError) Error() string { return e.Field + ": " + e.Msg }

type Ad struct {
	Title string
	Price int
	City  string
}

// Задача 1. Валидация формы.
//
// Верни ВСЕ найденные проблемы через errors.Join, каждую — как *FieldError:
//   - Title пустой                → Field "title"
//   - Title длиннее 100 символов  → Field "title"
//   - Price < 0                   → Field "price"
//   - City пустой                 → Field "city"
//
// Если проблем нет — nil.
func ValidateAd(a Ad) error {
	// TODO: твой код
	return nil
}

// Задача 2. Поиск с контекстом.
//
// Если объявления нет — верни ошибку, которая содержит id в тексте
// и при этом находится через errors.Is(err, ErrNotFound).
func FindAd(ads map[int]Ad, id int) (Ad, error) {
	// TODO: твой код
	return Ad{}, nil
}

// Задача 3. Ошибка → HTTP-статус.
//
//	nil                         → 200
//	ErrNotFound                 → 404
//	ErrForbidden                → 403
//	*FieldError                 → 422
//	context.DeadlineExceeded    → 504
//	всё остальное               → 500
//
// Ошибки могут быть обёрнуты сколько угодно раз.
func StatusCode(err error) int {
	// TODO: твой код
	return 0
}

// Задача 4. Повторы.
//
// Вызывай fn, пока она не вернёт nil, но не больше attempts раз.
// Если ошибка обёртывает ErrPermanent — не повторяй, сразу верни её.
// Если все попытки неудачны — верни последнюю ошибку, обёрнутую с текстом
// "после N попыток" (так, чтобы errors.Is по ней работал).
func Retry(attempts int, fn func() error) error {
	// TODO: твой код
	return nil
}

// Задача 5 ★. Паника → ошибка.
//
// Запусти fn. Если она запаниковала — верни ошибку с текстом "panic: …".
// Если значение паники само является error — оберни его так, чтобы работал errors.Is.
func SafeGo(fn func()) (err error) {
	// TODO: твой код
	fn()
	return nil
}
