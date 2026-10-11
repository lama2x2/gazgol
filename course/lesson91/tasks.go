// Урок 9.1 — HTTP и REST на net/http: API объявлений Барахолки.
//
// Хранилище уже готово (store.go). Твоя задача — HTTP-слой.
// Проверка: go test ./course/lesson91/
package lesson91

import (
	"net/http"
)

// CreateAdRequest — тело запроса POST /ads.
type CreateAdRequest struct {
	Title string `json:"title"`
	Price int    `json:"price"`
}

type API struct {
	store *MemStore
}

// NewAPI собирает роутер. Зарегистрируй четыре маршрута:
//
//	GET    /ads          → listAds
//	GET    /ads/{id}     → getAd
//	POST   /ads          → createAd
//	DELETE /ads/{id}     → deleteAd
func NewAPI(store *MemStore) http.Handler {
	a := &API{store: store}
	mux := http.NewServeMux()
	// TODO: зарегистрируй маршруты
	_ = a
	return mux
}

// writeJSON отправляет v как JSON с нужным статусом и Content-Type.
func writeJSON(w http.ResponseWriter, status int, v any) {
	// TODO: твой код
}

// writeError отправляет ошибку в формате {"error": "текст"}.
func writeError(w http.ResponseWriter, status int, msg string) {
	// TODO: твой код
}

// Задача 1. GET /ads — все объявления, по возрастанию id.
// ?max_price=N оставляет только объявления с ценой <= N. Нечисловое значение → 400.
// Пустой результат — [] (а не null).
func (a *API) listAds(w http.ResponseWriter, r *http.Request) {
	// TODO: твой код
}

// Задача 2. GET /ads/{id} → 200 и объявление; нет такого → 404; id не число → 400.
func (a *API) getAd(w http.ResponseWriter, r *http.Request) {
	// TODO: твой код
}

// Задача 3. POST /ads.
// Невалидный JSON → 400. Пустой title или price < 0 → 422.
// Успех → 201, заголовок Location: /ads/{id}, в теле созданное объявление.
func (a *API) createAd(w http.ResponseWriter, r *http.Request) {
	// TODO: твой код
}

// Задача 4. DELETE /ads/{id} → 204 без тела; нет такого → 404; id не число → 400.
func (a *API) deleteAd(w http.ResponseWriter, r *http.Request) {
	// TODO: твой код
}

// Задача 5 ★. Строгий JSON — см. тест TestJSONStrictness:
// Content-Type у всех JSON-ответов, тело запроса не больше 1 МБ,
// неизвестные поля в теле запроса → 400.
