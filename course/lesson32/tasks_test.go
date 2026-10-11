package lesson32

import (
	"maps"
	"slices"
	"strings"
	"testing"
)

func TestEvens(t *testing.T) {
	tests := []struct{ nums, want []int }{
		{[]int{1, 2, 3, 4, 6}, []int{2, 4, 6}},
		{[]int{1, 3, 5}, []int{}},
		{[]int{0, -2, -3}, []int{0, -2}},
	}
	for _, tt := range tests {
		orig := slices.Clone(tt.nums)
		got := Evens(tt.nums)
		if !slices.Equal(got, tt.want) {
			t.Errorf("Evens(%v) = %v, а ожидалось %v", orig, got, tt.want)
		}
		if !slices.Equal(tt.nums, orig) {
			t.Errorf("Evens испортил исходный срез: был %v, стал %v", orig, tt.nums)
		}
	}
}

func TestWordCount(t *testing.T) {
	tests := []struct {
		text string
		want map[string]int
	}{
		{"go Go python", map[string]int{"go": 2, "python": 1}},
		{"  Привет   привет мир ", map[string]int{"привет": 2, "мир": 1}},
		{"one", map[string]int{"one": 1}},
	}
	for _, tt := range tests {
		got := WordCount(tt.text)
		if !maps.Equal(got, tt.want) {
			t.Errorf("WordCount(%q) = %v, а ожидалось %v", tt.text, got, tt.want)
		}
	}
}

func TestReverse(t *testing.T) {
	tests := []struct{ s, want string }{
		{"Привет", "тевирП"},
		{"hello", "olleh"},
		{"Go, Гоу!", "!уоГ ,oG"},
		{"а", "а"},
	}
	for _, tt := range tests {
		if got := Reverse(tt.s); got != tt.want {
			t.Errorf("Reverse(%q) = %q, а ожидалось %q", tt.s, got, tt.want)
		}
	}
}

func TestParseAll(t *testing.T) {
	got, err := ParseAll([]string{"100", "", "250", "0"})
	if err != nil || !slices.Equal(got, []int{100, 250, 0}) {
		t.Errorf("ParseAll([100 \"\" 250 0]) = %v, %v, а ожидалось [100 250 0], <nil>", got, err)
	}
	got, err = ParseAll([]string{"100", "", "abc", "5"})
	if err == nil {
		t.Fatalf("ParseAll([100 \"\" abc 5]) вернул %v без ошибки", got)
	}
	if got != nil {
		t.Errorf("при ошибке ожидался nil вместо среза, а пришло %v", got)
	}
	if !strings.Contains(err.Error(), "строка 3") {
		t.Errorf("в ошибке %q нет номера строки «строка 3»", err)
	}
}

func TestUnique(t *testing.T) {
	tests := []struct{ nums, want []int }{
		{[]int{3, 1, 3, 2, 1}, []int{3, 1, 2}},
		{[]int{1, 1, 1}, []int{1}},
		{[]int{4, 5}, []int{4, 5}},
	}
	for _, tt := range tests {
		if got := Unique(tt.nums); !slices.Equal(got, tt.want) {
			t.Errorf("Unique(%v) = %v, а ожидалось %v", tt.nums, got, tt.want)
		}
	}
}
