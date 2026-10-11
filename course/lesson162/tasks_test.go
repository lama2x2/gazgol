//lyceum:race — проверка запускается с детектором гонок (-race).

package lesson162

import (
	"bytes"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
	"time"
)

func TestCounterVec(t *testing.T) {
	c := NewCounterVec("orders_total", "Заказы.", "city")
	var wg sync.WaitGroup
	for range 50 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for range 100 {
				c.With("kazan").Inc()
			}
			c.With("ufa").Add(2)
		}()
	}
	wg.Wait()
	if v := c.With("kazan").Value(); v != 5000 {
		t.Errorf("kazan = %v, а ожидалось 5000", v)
	}
	if v := c.With("ufa").Value(); v != 100 {
		t.Errorf("ufa = %v, а ожидалось 100", v)
	}
	defer func() {
		if recover() == nil {
			t.Error("With с неверным числом значений меток должен паниковать")
		}
	}()
	c.With("kazan", "лишнее")
}

func TestHistogram(t *testing.T) {
	h := NewHistogram("latency_seconds", "Задержка.", []float64{0.1, 0.5, 1})
	for _, v := range []float64{0.05, 0.1, 0.3, 0.7, 3} {
		h.Observe(v)
	}
	if h.Count() != 5 {
		t.Errorf("Count = %d, а ожидалось 5", h.Count())
	}
	if s := h.Sum(); s < 4.149 || s > 4.151 {
		t.Errorf("Sum = %v, а ожидалось 4.15", s)
	}
}

func TestExposition(t *testing.T) {
	reg := &Registry{}
	c := NewCounterVec("http_requests_total", "Число HTTP-запросов.", "method", "status")
	h := NewHistogram("latency_seconds", "Задержка.", []float64{0.1, 0.5, 1})
	reg.Register(c)
	reg.Register(h)
	c.With("POST", "201").Inc()
	c.With("GET", "200").Add(5)
	c.With("GET", "404").Inc()
	for _, v := range []float64{0.05, 0.1, 0.3, 0.7, 3} {
		h.Observe(v)
	}
	var buf bytes.Buffer
	reg.WriteText(&buf)
	want := `# HELP http_requests_total Число HTTP-запросов.
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 5
http_requests_total{method="GET",status="404"} 1
http_requests_total{method="POST",status="201"} 1
# HELP latency_seconds Задержка.
# TYPE latency_seconds histogram
latency_seconds_bucket{le="0.1"} 2
latency_seconds_bucket{le="0.5"} 3
latency_seconds_bucket{le="1"} 4
latency_seconds_bucket{le="+Inf"} 5
latency_seconds_sum 4.15
latency_seconds_count 5
`
	if buf.String() != want {
		t.Errorf("вывод /metrics:\n%s\nа ожидалось:\n%s", buf.String(), want)
	}
}

func TestInstrument(t *testing.T) {
	req := NewCounterVec("http_requests_total", "", "method", "route", "status")
	dur := NewHistogram("http_request_duration_seconds", "", []float64{0.01, 0.1, 1})
	mux := http.NewServeMux()
	mux.HandleFunc("GET /ads/{id}", func(w http.ResponseWriter, r *http.Request) {
		if r.PathValue("id") == "0" {
			w.WriteHeader(404)
			return
		}
		w.Write([]byte("ok"))
	})
	mux.HandleFunc("POST /ads", func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(20 * time.Millisecond)
		w.WriteHeader(201)
	})
	h := Instrument(mux, req, dur)
	call := func(m, p string) {
		h.ServeHTTP(httptest.NewRecorder(), httptest.NewRequest(m, p, nil))
	}
	call("GET", "/ads/1")
	call("GET", "/ads/2")
	call("GET", "/ads/0")
	call("POST", "/ads")
	call("GET", "/nope")
	checks := []struct {
		labels []string
		want   float64
	}{
		{[]string{"GET", "GET /ads/{id}", "200"}, 2},
		{[]string{"GET", "GET /ads/{id}", "404"}, 1},
		{[]string{"POST", "POST /ads", "201"}, 1},
		{[]string{"GET", "unmatched", "404"}, 1},
	}
	for _, c := range checks {
		if v := req.With(c.labels...).Value(); v != c.want {
			t.Errorf("requests%v = %v, а ожидалось %v", c.labels, v, c.want)
		}
	}
	if dur.Count() != 5 {
		t.Errorf("гистограмма задержек: %d наблюдений, а запросов было 5", dur.Count())
	}
	if dur.Sum() < 0.02 {
		t.Errorf("сумма задержек %v с — POST спал 20ms, задержку нужно мерить в секундах", dur.Sum())
	}
}

func TestTraceparent(t *testing.T) {
	newTrace := func() string { return "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" }
	newSpan := func() string { return "bbbbbbbbbbbbbbbb" }
	in := "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
	if got, want := ChildTraceparent(in, newTrace, newSpan), "00-4bf92f3577b34da6a3ce929d0e0e4736-bbbbbbbbbbbbbbbb-01"; got != want {
		t.Errorf("продолжение трейса: %q, а ожидалось %q", got, want)
	}
	if got := ChildTraceparent("00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-00", newTrace, newSpan); !strings.HasSuffix(got, "-00") {
		t.Errorf("флаги нужно сохранить: %q", got)
	}
	fresh := "00-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-bbbbbbbbbbbbbbbb-01"
	for _, bad := range []string{
		"", "мусор", "00-4bf92f-00f067aa0ba902b7-01",
		"00-00000000000000000000000000000000-00f067aa0ba902b7-01",
		"00-4bf92f3577b34da6a3ce929d0e0e4736-0000000000000000-01",
		"00-4bf92f3577b34da6a3ce929d0e0e473Z-00f067aa0ba902b7-01",
	} {
		if got := ChildTraceparent(bad, newTrace, newSpan); got != fresh {
			t.Errorf("невалидный %q: получено %q, а нужен новый трейс %q", bad, got, fresh)
		}
	}
}
