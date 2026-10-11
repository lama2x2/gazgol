// Урок 13.2 — Память, GC и профилирование.
//
// Задачи проверяются замерами: размер структуры (unsafe.Sizeof)
// и число аллокаций на вызов (testing.AllocsPerRun).
// Подсказка: go build -gcflags=-m ./course/lesson132/ покажет, что убегает в кучу.
//
// Проверка: go test ./course/lesson132/
package lesson132

import (
	"fmt"
	"io"
	"strconv"
	"strings"
)

// Задача 1. Bad занимает 32 байта из-за выравнивания.
type Bad struct {
	Sold     bool
	ID       int64
	Promoted bool
	Views    int32
	Archived bool
}

// Good — те же поля (имена и типы), но в порядке, при котором размер 16 байт.
type Good struct {
	// TODO: перечисли поля
}

// Задача 2. Ключ кэша поиска: "ads:<category>:<maxPrice>:<tag1>,<tag2>,..." — не больше одной аллокации.
//
//	AdKey("мебель", 5000, []string{"дерево", "б/у"}) → "ads:мебель:5000:дерево,б/у"
func AdKey(category string, maxPrice int64, tags []string) string {
	return "ads:" + category + ":" + strconv.FormatInt(maxPrice, 10) + ":" + strings.Join(tags, ",")
}

// Задача 3. Сумма цен — без аллокаций.
type Pricer interface{ Price() int64 }

type Ad struct {
	ID    int64
	Title string
	Cents int64
}

func (a Ad) Price() int64 { return a.Cents }

var lastPriced Pricer // для отладки: последнее посчитанное объявление

func Total(ads []Ad) int64 {
	var sum int64
	for _, a := range ads {
		var p Pricer = a
		lastPriced = p
		sum += p.Price()
	}
	return sum
}

// Задача 4 ★. Записать объявление в w в формате `{"id":42,"title":"Шкаф"}` — без аллокаций.
// Экранировать кавычки в title не нужно: гарантируется, что их там нет.
func RenderTo(w io.Writer, ad Ad) error {
	_, err := fmt.Fprintf(w, `{"id":%d,"title":"%s"}`, ad.ID, ad.Title)
	return err
}
