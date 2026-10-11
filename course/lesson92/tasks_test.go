package lesson92

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func serve(h http.Handler, req *http.Request) *httptest.ResponseRecorder {
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, req)
	return rec
}

func TestRecover(t *testing.T) {
	boom := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { panic("пароль от БД: qwerty") })
	var rec *httptest.ResponseRecorder
	func() {
		defer func() {
			if v := recover(); v != nil {
				t.Fatalf("паника вылетела из Recover: %v", v)
			}
		}()
		rec = serve(Recover(boom), httptest.NewRequest("GET", "/", nil))
	}()
	if rec.Code != 500 {
		t.Errorf("статус %d, а ожидался 500", rec.Code)
	}
	var body map[string]string
	if err := json.Unmarshal(rec.Body.Bytes(), &body); err != nil || body["error"] != "internal error" {
		t.Errorf("тело %q, а ожидалось {\"error\": \"internal error\"}", rec.Body.String())
	}
	if strings.Contains(rec.Body.String(), "qwerty") {
		t.Error("текст паники утёк клиенту")
	}
	ok := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { w.WriteHeader(201) })
	if rec := serve(Recover(ok), httptest.NewRequest("GET", "/", nil)); rec.Code != 201 {
		t.Errorf("без паники Recover должен пропускать ответ как есть, а статус %d", rec.Code)
	}
}

func TestRequestID(t *testing.T) {
	var seen string
	h := RequestID(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { seen = RequestIDFrom(r.Context()) }))

	req := httptest.NewRequest("GET", "/", nil)
	req.Header.Set("X-Request-ID", "abc-123")
	rec := serve(h, req)
	if seen != "abc-123" || rec.Header().Get("X-Request-ID") != "abc-123" {
		t.Errorf("пришёл X-Request-ID abc-123: в контексте %q, в ответе %q", seen, rec.Header().Get("X-Request-ID"))
	}

	rec = serve(h, httptest.NewRequest("GET", "/", nil))
	got := rec.Header().Get("X-Request-ID")
	if got == "" || seen != got {
		t.Errorf("без X-Request-ID: в ответе %q, в контексте %q — нужно сгенерировать один id", got, seen)
	}
	if RequestIDFrom(httptest.NewRequest("GET", "/", nil).Context()) != "" {
		t.Error("RequestIDFrom для пустого контекста должен вернуть \"\"")
	}
}

func TestRequireRole(t *testing.T) {
	tokens := map[string]string{"adm1n": "admin", "us3r": "user"}
	var role string
	h := RequireRole(tokens, "admin")(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		role = RoleFrom(r.Context())
		w.WriteHeader(200)
	}))
	cases := []struct {
		auth string
		code int
	}{
		{"", 401},
		{"Basic adm1n", 401},
		{"Bearer nope", 401},
		{"Bearer us3r", 403},
		{"Bearer adm1n", 200},
	}
	for _, c := range cases {
		req := httptest.NewRequest("DELETE", "/ads/1", nil)
		if c.auth != "" {
			req.Header.Set("Authorization", c.auth)
		}
		rec := serve(h, req)
		if rec.Code != c.code {
			t.Errorf("Authorization %q: статус %d, а ожидался %d", c.auth, rec.Code, c.code)
		}
		if c.code == 401 && rec.Header().Get("WWW-Authenticate") == "" {
			t.Errorf("Authorization %q: при 401 нужен заголовок WWW-Authenticate: Bearer", c.auth)
		}
	}
	if role != "admin" {
		t.Errorf("RoleFrom в хендлере = %q, а ожидалось admin", role)
	}
}

func TestLogging(t *testing.T) {
	var lines []string
	logf := func(f string, args ...any) { lines = append(lines, fmt.Sprintf(f, args...)) }
	mux := http.NewServeMux()
	mux.HandleFunc("GET /ok", func(w http.ResponseWriter, r *http.Request) { w.Write([]byte("hi")) })
	mux.HandleFunc("POST /ads", func(w http.ResponseWriter, r *http.Request) { w.WriteHeader(201) })
	h := Logging(logf)(mux)
	serve(h, httptest.NewRequest("GET", "/ok", nil))
	serve(h, httptest.NewRequest("POST", "/ads", nil))
	serve(h, httptest.NewRequest("GET", "/nope", nil))
	want := []string{"GET /ok 200", "POST /ads 201", "GET /nope 404"}
	if strings.Join(lines, "|") != strings.Join(want, "|") {
		t.Errorf("логи %q, а ожидалось %q", lines, want)
	}
}

func TestChain(t *testing.T) {
	var order []string
	mk := func(name string) Middleware {
		return func(next http.Handler) http.Handler {
			return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				order = append(order, name)
				next.ServeHTTP(w, r)
			})
		}
	}
	h := Chain(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { order = append(order, "h") }), mk("A"), mk("B"), mk("C"))
	serve(h, httptest.NewRequest("GET", "/", nil))
	if got := strings.Join(order, ""); got != "ABCh" {
		t.Errorf("порядок вызовов %q, а ожидался ABCh — первый middleware в списке должен быть внешним", got)
	}
	order = nil
	serve(Chain(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { order = append(order, "h") })), httptest.NewRequest("GET", "/", nil))
	if strings.Join(order, "") != "h" {
		t.Error("Chain без middleware должен вернуть сам хендлер")
	}
}
