package lesson72

import (
	"errors"
	"maps"
	"slices"
	"strings"
	"testing"
	"time"
)

func TestSet(t *testing.T) {
	s := NewSet("go", "python", "go")
	if s == nil {
		t.Fatal("NewSet вернул nil-map — первый же Add упадёт")
	}
	if s.Len() != 2 || !s.Has("go") || !s.Has("python") || s.Has("java") {
		t.Errorf("NewSet(go, python, go): Len=%d, Has(go)=%v, Has(python)=%v, Has(java)=%v — ожидалось 2, true, true, false",
			s.Len(), s.Has("go"), s.Has("python"), s.Has("java"))
	}
	s.Add("rust")
	s.Remove("python")
	s.Remove("нет такого")
	if s.Len() != 2 || !s.Has("rust") || s.Has("python") {
		t.Errorf("после Add(rust) и Remove(python): Len=%d, Has(rust)=%v, Has(python)=%v", s.Len(), s.Has("rust"), s.Has("python"))
	}
	empty := NewSet[int]()
	empty.Add(1)
	if !empty.Has(1) {
		t.Error("NewSet[int]() + Add(1): Has(1) = false")
	}
}

func TestGroupBy(t *testing.T) {
	words := []string{"kiwi", "apple", "avocado", "banana", "kale"}
	got := GroupBy(words, func(s string) byte { return s[0] })
	want := map[byte][]string{'a': {"apple", "avocado"}, 'b': {"banana"}, 'k': {"kiwi", "kale"}}
	if !maps.EqualFunc(got, want, slices.Equal[[]string]) {
		t.Errorf("GroupBy по первой букве = %v, а ожидалось %v", got, want)
	}
	type ad struct {
		city  string
		price int
	}
	ads := []ad{{"Казань", 100}, {"Москва", 200}, {"Казань", 300}}
	byCity := GroupBy(ads, func(a ad) string { return a.city })
	if len(byCity["Казань"]) != 2 || byCity["Казань"][1].price != 300 || len(byCity["Москва"]) != 1 {
		t.Errorf("GroupBy по городу = %v", byCity)
	}
}

func TestSortedKeys(t *testing.T) {
	m := map[string]int{"пт": 5, "вт": 2, "ср": 3, "пн": 1, "чт": 4}
	for range 20 { // порядок обхода map случайный — проверяем много раз
		if got, want := SortedKeys(m), []string{"вт", "пн", "пт", "ср", "чт"}; !slices.Equal(got, want) {
			t.Fatalf("SortedKeys = %v, а ожидалось %v", got, want)
		}
	}
	if got := SortedKeys(map[int]bool{3: true, 1: true, 2: false}); !slices.Equal(got, []int{1, 2, 3}) {
		t.Errorf("SortedKeys(int-ключи) = %v, а ожидалось [1 2 3]", got)
	}
}

func TestNewClient(t *testing.T) {
	c := NewClient("https://api.example.com")
	if c == nil {
		t.Fatal("NewClient вернул nil")
	}
	if c.BaseURL != "https://api.example.com" || c.Timeout != 5*time.Second || c.Retries != 3 {
		t.Errorf("NewClient без опций = %+v, а ожидалось BaseURL задан, Timeout 5s, Retries 3", *c)
	}
	c = NewClient("u", WithTimeout(time.Second), WithRetries(0))
	if c.Timeout != time.Second || c.Retries != 0 {
		t.Errorf("NewClient(WithTimeout(1s), WithRetries(0)) = %+v", *c)
	}
	c = NewClient("u", WithRetries(-5))
	if c.Retries != 3 {
		t.Errorf("WithRetries(-5) должна игнорироваться, а Retries = %d", c.Retries)
	}
	c = NewClient("u", WithRetries(1), WithRetries(7))
	if c.Retries != 7 {
		t.Errorf("опции применяются по порядку: WithRetries(1), WithRetries(7) → ожидалось 7, а получилось %d", c.Retries)
	}
}

func TestValidate(t *testing.T) {
	if err := Validate("Велосипед", 5000); err != nil {
		t.Errorf("Validate(корректное объявление) = %v (тип %T), а ожидался nil — интерфейс с nil-указателем внутри не равен nil", err, err)
	}
	err := Validate("", 100)
	var ae *AdError
	if !errors.As(err, &ae) || !strings.Contains(ae.Reason, "назван") {
		t.Errorf("Validate(\"\", 100) = %v, а ожидалась *AdError про название", err)
	}
	if err := Validate("Стул", -1); !errors.As(err, &ae) {
		t.Errorf("Validate(\"Стул\", -1) = %v, а ожидалась *AdError", err)
	}
	if err := Validate("", 0); !errors.Is(err, errEmpty) {
		t.Errorf("Validate(\"\", 0) = %v, а ожидалась errEmpty", err)
	}
}
