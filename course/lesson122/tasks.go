// Урок 12.2 — Сервис, готовый к продакшену.
//
// Проверка: go test ./course/lesson122/
package lesson122

import (
	"context"
	"io"
	"log/slog"
	"net"
	"net/http"
	"time"
)

type Config struct {
	Port            int           // PORT, по умолчанию 8080, от 1 до 65535
	DatabaseURL     string        // DATABASE_URL, обязательна
	LogLevel        string        // LOG_LEVEL: debug|info|warn|error, по умолчанию info
	ShutdownTimeout time.Duration // SHUTDOWN_TIMEOUT, например "15s", по умолчанию 10s
}

// Задача 1. Прочитай конфигурацию через getenv (в проде — os.Getenv).
// Сообщи обо ВСЕХ проблемах сразу через errors.Join; в тексте каждой упомяни имя переменной.
func LoadConfig(getenv func(string) string) (Config, error) {
	// TODO: твой код
	return Config{}, nil
}

// Задача 2. JSON-логгер в w с минимальным уровнем level (debug|info|warn|error).
func NewLogger(w io.Writer, level string) *slog.Logger {
	// TODO: твой код
	return slog.New(slog.NewTextHandler(w, nil))
}

// Задача 3. Пробы.
//
//	GET /healthz → 200 всегда
//	GET /readyz  → вызывает check с таймаутом 1 секунда:
//	               nil   → 200 и {"status": "ok"}
//	               error → 503 и {"status": "unavailable", "error": "<текст>"}
func Health(check func(ctx context.Context) error) http.Handler {
	// TODO: твой код
	return http.NewServeMux()
}

// Задача 4. Обслуживай h на ln, пока не отменят ctx; затем graceful shutdown,
// давая текущим запросам не больше timeout. Корректная остановка → nil.
func Serve(ctx context.Context, ln net.Listener, h http.Handler, timeout time.Duration) error {
	// TODO: твой код
	return nil
}

// Задача 5 ★. Логируй каждый запрос: logger.Info("request", "method", ..., "path", ...,
// "status", ..., "duration_ms", ...). Для статусов 5xx — уровень Error.
func AccessLog(logger *slog.Logger) func(http.Handler) http.Handler {
	// TODO: твой код
	return func(next http.Handler) http.Handler { return next }
}
