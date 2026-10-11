// Урок 5.2 — ООП: встраивание вместо наследования, интерфейсы, полиморфизм.
//
// Проверка: go test ./course/lesson52/
package lesson52

// ---------- Встраивание ----------

// User — любой пользователь Барахолки.
type User struct {
	Name   string
	Rating float64
}

// Seller — продавец. Он «встраивает» User: поля и методы User
// доступны прямо у Seller (s.Name, s.Contact()). Это композиция, а не наследование.
type Seller struct {
	User
	Phone string
}

// Задача 1. Контакт пользователя.
//
// Формат: имя и рейтинг с одним знаком после запятой (%.1f).
//
//	User{"Гоша", 4.83}.Contact() → "Гоша (★4.8)"
func (u User) Contact() string {
	// TODO: твой код
	return ""
}

// Задача 2. Контакт продавца.
//
// Seller переопределяет Contact: к контакту User добавляется телефон.
// Не дублируй форматирование — вызови метод встроенного User: s.User.Contact().
//
//	"Гоша (★4.8), тел. +7 900 000-00-00"
func (s Seller) Contact() string {
	// TODO: твой код
	return ""
}

// ---------- Интерфейсы ----------

// Delivery — способ доставки. Любой тип с этими двумя методами
// автоматически считается Delivery. Никаких implements писать не нужно.
type Delivery interface {
	Name() string
	Cost(km int) int
}

// Задача 3. Три способа доставки. Заполни методы:
//
//	Pickup  — "Самовывоз", всегда 0 ₽
//	Courier — "Курьер", 200 ₽ + PerKm за каждый км
//	Post    — "Почта", 350 ₽ + 50 ₽ за каждые полные 100 км (km / 100 * 50)
type Pickup struct{}

func (Pickup) Name() string    { return "" } // TODO
func (Pickup) Cost(km int) int { return 0 }  // TODO

type Courier struct{ PerKm int }

func (c Courier) Name() string    { return "" } // TODO
func (c Courier) Cost(km int) int { return 0 }  // TODO

type Post struct{}

func (Post) Name() string    { return "" } // TODO
func (Post) Cost(km int) int { return 0 }  // TODO

// Задача 4. Самая дешёвая доставка (полиморфизм).
//
// Функция не знает и не должна знать, какие конкретно типы ей передали.
// При равной цене выбирай ту, что раньше в списке.
// Пустой список → nil и ошибка.
func Cheapest(options []Delivery, km int) (Delivery, error) {
	// TODO: твой код
	return nil, nil
}

// Задача 5 ★. Что это за значение? (type switch)
//
// Порядок проверок важен:
//
//	Delivery     → "доставка: <Name()>"
//	error        → "ошибка: <Error()>"
//	fmt.Stringer → "<String()>"
//	int          → "число <n>"
//	nil          → "пусто"
//	иначе        → "неизвестно"
func Describe(v any) string {
	// TODO: твой код
	return ""
}
