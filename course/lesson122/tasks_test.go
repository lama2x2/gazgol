package lesson122

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"io"
	"net"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

func env(m map[string]string) func(string) string { return func(k string) string { return m[k] } }

func TestLoadConfig(t *testing.T) {
	cfg, err := LoadConfig(env(map[string]string{"DATABASE_URL": "postgres://x"}))
	if err != nil {
		t.Fatalf("минимальный конфиг: ошибка %v", err)
	}
	if cfg.Port != 8080 || cfg.LogLevel != "info" || cfg.ShutdownTimeout != 10*time.Second || cfg.DatabaseURL != "postgres://x" {
		t.Errorf("значения по умолчанию: %+v", cfg)
	}
	cfg, err = LoadConfig(env(map[string]string{"DATABASE_URL": "u", "PORT": "9000", "LOG_LEVEL": "debug", "SHUTDOWN_TIMEOUT": "3s"}))
	if err != nil || cfg.Port != 9000 || cfg.LogLevel != "debug" || cfg.ShutdownTimeout != 3*time.Second {
		t.Errorf("заданные значения: %+v, %v", cfg, err)
	}
	_, err = LoadConfig(env(map[string]string{"PORT": "99999", "LOG_LEVEL": "loud", "SHUTDOWN_TIMEOUT": "скоро"}))
	if err == nil {
		t.Fatal("плохой конфиг принят без ошибок")
	}
	for _, name := range []string{"DATABASE_URL", "PORT", "LOG_LEVEL", "SHUTDOWN_TIMEOUT"} {
		if !strings.Contains(err.Error(), name) {
			t.Errorf("в ошибке не упомянута %s: %v", name, err)
		}
	}
	if _, err := LoadConfig(env(map[string]string{"DATABASE_URL": "u", "PORT": "abc"})); err == nil {
		t.Error("PORT=abc должен быть ошибкой")
	}
}

func TestNewLogger(t *testing.T) {
	var buf bytes.Buffer
	l := NewLogger(&buf, "info")
	l.Debug("скрыто")
	l.Info("ad created", "ad_id", 42)
	l.Warn("медленно", "ms", 900)
	lines := strings.Split(strings.TrimSpace(buf.String()), "\n")
	if len(lines) != 2 {
		t.Fatalf("при уровне info ожидалось 2 строки лога, а их %d:\n%s", len(lines), buf.String())
	}
	var rec map[string]any
	if err := json.Unmarshal([]byte(lines[0]), &rec); err != nil {
		t.Fatalf("лог не в JSON: %q", lines[0])
	}
	if rec["msg"] != "ad created" || rec["level"] != "INFO" || rec["ad_id"] != float64(42) {
		t.Errorf("запись %v", rec)
	}
	buf.Reset()
	NewLogger(&buf, "debug").Debug("видно")
	if !strings.Contains(buf.String(), "видно") {
		t.Error("при уровне debug отладочные сообщения должны писаться")
	}
	buf.Reset()
	NewLogger(&buf, "error").Warn("не видно")
	if buf.Len() != 0 {
		t.Error("при уровне error предупреждения не пишутся")
	}
}

func TestHealth(t *testing.T) {
	get := func(h http.Handler, path string) *httptest.ResponseRecorder {
		rec := httptest.NewRecorder()
		h.ServeHTTP(rec, httptest.NewRequest("GET", path, nil))
		return rec
	}
	down := errors.New("db down")
	h := Health(func(ctx context.Context) error { return down })
	if rec := get(h, "/healthz"); rec.Code != 200 {
		t.Errorf("/healthz = %d, а должен быть 200 всегда", rec.Code)
	}
	rec := get(h, "/readyz")
	var body map[string]string
	json.Unmarshal(rec.Body.Bytes(), &body)
	if rec.Code != 503 || body["status"] != "unavailable" || body["error"] != "db down" {
		t.Errorf("/readyz при ошибке: %d %q", rec.Code, rec.Body.String())
	}
	ok := Health(func(ctx context.Context) error { return nil })
	rec = get(ok, "/readyz")
	json.Unmarshal(rec.Body.Bytes(), &body)
	if rec.Code != 200 || body["status"] != "ok" {
		t.Errorf("/readyz без ошибки: %d %q", rec.Code, rec.Body.String())
	}
	hang := Health(func(ctx context.Context) error { <-ctx.Done(); return ctx.Err() })
	start := time.Now()
	rec = get(hang, "/readyz")
	if el := time.Since(start); rec.Code != 503 || el < 900*time.Millisecond || el > 3*time.Second {
		t.Errorf("зависшая проверка: статус %d через %v — ожидался 503 примерно через 1с", rec.Code, el)
	}
}

func TestServe(t *testing.T) {
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	started := make(chan struct{})
	h := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		close(started)
		time.Sleep(300 * time.Millisecond)
		io.WriteString(w, "готово")
	})
	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan error, 1)
	go func() { done <- Serve(ctx, ln, h, 2*time.Second) }()

	type resp struct {
		body string
		err  error
	}
	got := make(chan resp, 1)
	go func() {
		r, err := http.Get("http://" + ln.Addr().String() + "/")
		if err != nil {
			got <- resp{err: err}
			return
		}
		defer r.Body.Close()
		b, _ := io.ReadAll(r.Body)
		got <- resp{body: string(b)}
	}()
	select {
	case <-started:
	case <-time.After(2 * time.Second):
		t.Fatal("сервер не принял запрос")
	}
	cancel()
	r := <-got
	if r.err != nil || r.body != "готово" {
		t.Errorf("запрос в процессе остановки: %q, %v — его нужно было доделать", r.body, r.err)
	}
	select {
	case err := <-done:
		if err != nil {
			t.Errorf("Serve вернул %v, а при корректной остановке нужен nil", err)
		}
	case <-time.After(3 * time.Second):
		t.Fatal("Serve не завершился после отмены ctx")
	}
	if _, err := http.Get("http://" + ln.Addr().String() + "/"); err == nil {
		t.Error("после остановки сервер всё ещё принимает соединения")
	}
}

func TestAccessLog(t *testing.T) {
	var buf bytes.Buffer
	logger := NewLogger(&buf, "info")
	mux := http.NewServeMux()
	mux.HandleFunc("GET /ads", func(w http.ResponseWriter, r *http.Request) { w.Write([]byte("[]")) })
	mux.HandleFunc("GET /boom", func(w http.ResponseWriter, r *http.Request) { w.WriteHeader(502) })
	h := AccessLog(logger)(mux)
	for _, p := range []string{"/ads", "/boom"} {
		h.ServeHTTP(httptest.NewRecorder(), httptest.NewRequest("GET", p, nil))
	}
	lines := strings.Split(strings.TrimSpace(buf.String()), "\n")
	if len(lines) != 2 {
		t.Fatalf("ожидалось 2 записи, а их %d: %s", len(lines), buf.String())
	}
	var a, b map[string]any
	json.Unmarshal([]byte(lines[0]), &a)
	json.Unmarshal([]byte(lines[1]), &b)
	if a["msg"] != "request" || a["method"] != "GET" || a["path"] != "/ads" || a["status"] != float64(200) || a["level"] != "INFO" {
		t.Errorf("запись для /ads: %v", a)
	}
	if _, ok := a["duration_ms"]; !ok {
		t.Error("нет поля duration_ms")
	}
	if b["status"] != float64(502) || b["level"] != "ERROR" {
		t.Errorf("запись для /boom (502): %v — для 5xx нужен уровень ERROR", b)
	}
}
