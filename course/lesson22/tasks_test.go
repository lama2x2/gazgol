package lesson22

import (
	"errors"
	"testing"
)

func TestDayType(t *testing.T) {
	tests := []struct{ day, want string }{
		{"пн", "будний"}, {"вт", "будний"}, {"ср", "будний"}, {"чт", "будний"}, {"пт", "будний"},
		{"сб", "выходной"}, {"вс", "выходной"},
		{"Пн", "неизвестно"}, {"", "неизвестно"}, {"понедельник", "неизвестно"},
	}
	for _, tt := range tests {
		if got := DayType(tt.day); got != tt.want {
			t.Errorf("DayType(%q) = %q, а ожидалось %q", tt.day, got, tt.want)
		}
	}
}

func TestDivide(t *testing.T) {
	got, err := Divide(7, 2)
	if err != nil || got != 3 {
		t.Errorf("Divide(7, 2) = %d, %v, а ожидалось 3, <nil>", got, err)
	}
	got, err = Divide(-9, 3)
	if err != nil || got != -3 {
		t.Errorf("Divide(-9, 3) = %d, %v, а ожидалось -3, <nil>", got, err)
	}
	got, err = Divide(5, 0)
	if !errors.Is(err, ErrDivByZero) || got != 0 {
		t.Errorf("Divide(5, 0) = %d, %v, а ожидалось 0, ErrDivByZero", got, err)
	}
}

func TestParseAge(t *testing.T) {
	ok := []struct {
		s    string
		want int
	}{
		{"25", 25}, {"0", 0}, {"150", 150}, {" 42 ", 42},
	}
	for _, tt := range ok {
		got, err := ParseAge(tt.s)
		if err != nil || got != tt.want {
			t.Errorf("ParseAge(%q) = %d, %v, а ожидалось %d, <nil>", tt.s, got, err, tt.want)
		}
	}
	bad := []string{"abc", "", "12.5", "-1", "151", "1000"}
	for _, s := range bad {
		if _, err := ParseAge(s); err == nil {
			t.Errorf("ParseAge(%q) вернул nil, а ожидалась ошибка", s)
		}
	}
}

func TestTriangle(t *testing.T) {
	tests := []struct {
		a, b, c int
		want    string
	}{
		{3, 3, 3, "равносторонний"},
		{3, 3, 5, "равнобедренный"},
		{5, 3, 3, "равнобедренный"},
		{3, 5, 3, "равнобедренный"},
		{3, 4, 5, "разносторонний"},
		{1, 2, 3, "не существует"},
		{1, 1, 10, "не существует"},
		{0, 0, 0, "не существует"},
		{-3, 4, 5, "не существует"},
	}
	for _, tt := range tests {
		if got := Triangle(tt.a, tt.b, tt.c); got != tt.want {
			t.Errorf("Triangle(%d, %d, %d) = %q, а ожидалось %q", tt.a, tt.b, tt.c, got, tt.want)
		}
	}
}
