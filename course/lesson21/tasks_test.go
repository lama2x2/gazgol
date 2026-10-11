package lesson21

import "testing"

func TestGrade(t *testing.T) {
	tests := []struct {
		score int
		want  string
	}{
		{100, "отлично"}, {90, "отлично"},
		{89, "хорошо"}, {75, "хорошо"},
		{74, "удовлетворительно"}, {60, "удовлетворительно"},
		{59, "плохо"}, {0, "плохо"},
		{-1, "ошибка"}, {101, "ошибка"},
	}
	for _, tt := range tests {
		if got := Grade(tt.score); got != tt.want {
			t.Errorf("Grade(%d) = %q, а ожидалось %q", tt.score, got, tt.want)
		}
	}
}

func TestIsLeapYear(t *testing.T) {
	tests := []struct {
		year int
		want bool
	}{
		{2024, true}, {2023, false}, {1900, false}, {2000, true}, {2100, false}, {1600, true},
	}
	for _, tt := range tests {
		if got := IsLeapYear(tt.year); got != tt.want {
			t.Errorf("IsLeapYear(%d) = %v, а ожидалось %v", tt.year, got, tt.want)
		}
	}
}

func TestCanRent(t *testing.T) {
	tests := []struct {
		age        int
		license    bool
		exp        int
		instructor bool
		want       bool
	}{
		{25, true, 5, false, true},
		{21, true, 2, false, true},
		{21, true, 1, false, false},
		{30, false, 10, false, false},
		{20, true, 3, false, false},
		{19, true, 1, true, true},
		{20, true, 1, true, true},
		{19, true, 0, true, false},
		{18, true, 1, true, false},
		{19, false, 1, true, false},
	}
	for _, tt := range tests {
		if got := CanRent(tt.age, tt.license, tt.exp, tt.instructor); got != tt.want {
			t.Errorf("CanRent(возраст %d, права %v, стаж %d, инструктор %v) = %v, а ожидалось %v",
				tt.age, tt.license, tt.exp, tt.instructor, got, tt.want)
		}
	}
}
