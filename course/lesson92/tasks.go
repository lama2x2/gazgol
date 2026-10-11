// Урок 9.2 — Middleware, авторизация, таймауты.
//
// Проверка: go test ./course/lesson92/
package lesson92

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"net/http"
)

// Middleware — функция, которая оборачивает хендлер.
type Middleware func(http.Handler) http.Handler

// newID генерирует случайный id запроса. Уже готово.
func newID() string {
	b := make([]byte, 8)
	rand.Read(b)
	return hex.EncodeToString(b)
}

// Задача 1. Паника в хендлере → 500 и {"error": "internal error"} в JSON.
// Сервис не должен падать.
func Recover(next http.Handler) http.Handler {
	// TODO: твой код
	return next
}

// Задача 2. Id запроса.
//
// Возьми X-Request-ID из запроса или сгенерируй через newID().
// Положи его в заголовок ответа X-Request-ID и в контекст запроса.
func RequestID(next http.Handler) http.Handler {
	// TODO: твой код
	return next
}

// RequestIDFrom достаёт id запроса из контекста. Если его нет — "".
func RequestIDFrom(ctx context.Context) string {
	// TODO: твой код
	return ""
}

// Задача 3. Доступ по ролям.
//
// tokens — известные токены и роли их владельцев: {"t0ken": "admin"}.
// Заголовок: "Authorization: Bearer <token>".
//   - нет заголовка, не Bearer или неизвестный токен → 401 и заголовок WWW-Authenticate: Bearer
//   - токен известен, но роль не role → 403
//   - иначе — положи роль в контекст (RoleFrom её достанет) и вызови next
func RequireRole(tokens map[string]string, role string) Middleware {
	// TODO: твой код
	return func(next http.Handler) http.Handler { return next }
}

// RoleFrom достаёт роль пользователя из контекста. Если её нет — "".
func RoleFrom(ctx context.Context) string {
	// TODO: твой код
	return ""
}

// Задача 4. Логирование.
//
// После обработки запроса вызови logf("%s %s %d", метод, путь, статус).
// Если хендлер не вызывал WriteHeader — статус 200.
func Logging(logf func(format string, args ...any)) Middleware {
	// TODO: твой код
	return func(next http.Handler) http.Handler { return next }
}

// Задача 5 ★. Цепочка: Chain(h, A, B, C) == A(B(C(h))) — первый в списке внешний.
func Chain(h http.Handler, mws ...Middleware) http.Handler {
	// TODO: твой код
	return h
}
