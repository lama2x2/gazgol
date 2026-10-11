package lesson91

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func do(t *testing.T, h http.Handler, method, path, body string) *httptest.ResponseRecorder {
	t.Helper()
	var req *http.Request
	if body == "" {
		req = httptest.NewRequest(method, path, nil)
	} else {
		req = httptest.NewRequest(method, path, strings.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
	}
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, req)
	return rec
}

func seeded() (*MemStore, http.Handler) {
	s := NewMemStore()
	s.Create("Велосипед", 5000)
	s.Create("Шкаф", 12000)
	s.Create("Лампа", 700)
	return s, NewAPI(s)
}

func hasErrorBody(t *testing.T, rec *httptest.ResponseRecorder) {
	t.Helper()
	var e map[string]string
	if err := json.Unmarshal(rec.Body.Bytes(), &e); err != nil || e["error"] == "" {
		t.Errorf("ожидалось тело {\"error\": \"...\"}, а пришло %q", rec.Body.String())
	}
}

func TestListAds(t *testing.T) {
	_, api := seeded()
	rec := do(t, api, "GET", "/ads", "")
	if rec.Code != 200 {
		t.Fatalf("GET /ads: статус %d, а ожидался 200", rec.Code)
	}
	var ads []Ad
	if err := json.Unmarshal(rec.Body.Bytes(), &ads); err != nil || len(ads) != 3 || ads[0].Title != "Велосипед" {
		t.Fatalf("GET /ads: тело %q — ожидался массив из 3 объявлений по порядку id", rec.Body.String())
	}
	rec = do(t, api, "GET", "/ads?max_price=5000", "")
	json.Unmarshal(rec.Body.Bytes(), &ads)
	if rec.Code != 200 || len(ads) != 2 || ads[0].ID != 1 || ads[1].ID != 3 {
		t.Errorf("GET /ads?max_price=5000: статус %d, тело %q — ожидались объявления 1 и 3", rec.Code, rec.Body.String())
	}
	rec = do(t, api, "GET", "/ads?max_price=1", "")
	if strings.TrimSpace(rec.Body.String()) != "[]" {
		t.Errorf("GET /ads?max_price=1: тело %q, а ожидался пустой массив []", rec.Body.String())
	}
	rec = do(t, api, "GET", "/ads?max_price=дорого", "")
	if rec.Code != 400 {
		t.Errorf("GET /ads?max_price=дорого: статус %d, а ожидался 400", rec.Code)
	}
}

func TestGetAd(t *testing.T) {
	_, api := seeded()
	rec := do(t, api, "GET", "/ads/2", "")
	var ad Ad
	json.Unmarshal(rec.Body.Bytes(), &ad)
	if rec.Code != 200 || ad.Title != "Шкаф" || ad.Price != 12000 {
		t.Errorf("GET /ads/2: статус %d, тело %q", rec.Code, rec.Body.String())
	}
	rec = do(t, api, "GET", "/ads/99", "")
	if rec.Code != 404 {
		t.Errorf("GET /ads/99: статус %d, а ожидался 404", rec.Code)
	}
	hasErrorBody(t, rec)
	rec = do(t, api, "GET", "/ads/abc", "")
	if rec.Code != 400 {
		t.Errorf("GET /ads/abc: статус %d, а ожидался 400", rec.Code)
	}
}

func TestCreateAd(t *testing.T) {
	s, api := seeded()
	rec := do(t, api, "POST", "/ads", `{"title": "Диван", "price": 9000}`)
	if rec.Code != 201 {
		t.Fatalf("POST /ads: статус %d (%q), а ожидался 201", rec.Code, rec.Body.String())
	}
	var ad Ad
	json.Unmarshal(rec.Body.Bytes(), &ad)
	if ad.ID != 4 || ad.Title != "Диван" || ad.Price != 9000 {
		t.Errorf("POST /ads: в теле %q, а ожидалось созданное объявление с id 4", rec.Body.String())
	}
	if loc := rec.Header().Get("Location"); loc != "/ads/4" {
		t.Errorf("POST /ads: Location = %q, а ожидалось /ads/4", loc)
	}
	if _, err := s.Get(4); err != nil {
		t.Error("объявление не сохранилось в хранилище")
	}
	cases := []struct {
		body string
		code int
	}{
		{`{"title": "Диван", "price": `, 400},
		{`не json`, 400},
		{`{"title": "", "price": 100}`, 422},
		{`{"title": "Стул", "price": -5}`, 422},
	}
	for _, c := range cases {
		rec := do(t, api, "POST", "/ads", c.body)
		if rec.Code != c.code {
			t.Errorf("POST /ads %s: статус %d, а ожидался %d", c.body, rec.Code, c.code)
		}
		hasErrorBody(t, rec)
	}
}

func TestDeleteAd(t *testing.T) {
	s, api := seeded()
	rec := do(t, api, "DELETE", "/ads/1", "")
	if rec.Code != 204 || rec.Body.Len() != 0 {
		t.Errorf("DELETE /ads/1: статус %d, тело %q — ожидался 204 без тела", rec.Code, rec.Body.String())
	}
	if _, err := s.Get(1); err == nil {
		t.Error("объявление 1 не удалилось")
	}
	if rec := do(t, api, "DELETE", "/ads/1", ""); rec.Code != 404 {
		t.Errorf("повторный DELETE /ads/1: статус %d, а ожидался 404", rec.Code)
	}
	if rec := do(t, api, "DELETE", "/ads/x", ""); rec.Code != 400 {
		t.Errorf("DELETE /ads/x: статус %d, а ожидался 400", rec.Code)
	}
}

func TestJSONStrictness(t *testing.T) {
	_, api := seeded()
	for _, r := range []struct{ method, path, body string }{
		{"GET", "/ads", ""}, {"GET", "/ads/1", ""}, {"GET", "/ads/99", ""},
		{"POST", "/ads", `{"title": "Кот", "price": 1}`}, {"POST", "/ads", `{"title": ""}`},
	} {
		rec := do(t, api, r.method, r.path, r.body)
		if ct := rec.Header().Get("Content-Type"); !strings.HasPrefix(ct, "application/json") {
			t.Errorf("%s %s: Content-Type = %q, а ожидался application/json", r.method, r.path, ct)
		}
	}
	rec := do(t, api, "POST", "/ads", `{"tittle": "опечатка", "price": 1}`)
	if rec.Code != 400 {
		t.Errorf("POST с неизвестным полем \"tittle\": статус %d, а ожидался 400 (DisallowUnknownFields)", rec.Code)
	}
	huge := `{"title": "` + strings.Repeat("я", 1<<20) + `", "price": 1}`
	rec = do(t, api, "POST", "/ads", huge)
	if rec.Code != 400 && rec.Code != 413 {
		t.Errorf("POST с телом больше 1 МБ: статус %d, а ожидался 400 или 413 (http.MaxBytesReader)", rec.Code)
	}
}
