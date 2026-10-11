package lesson12

import (
	"math"
	"slices"
	"testing"
)

func almostEqual(a, b float64) bool { return math.Abs(a-b) < 1e-9 }

func TestCelsiusToFahrenheit(t *testing.T) {
	tests := []struct{ c, want float64 }{
		{0, 32},
		{100, 212},
		{-40, -40},
		{36.6, 97.88},
	}
	for _, tt := range tests {
		if got := CelsiusToFahrenheit(tt.c); !almostEqual(got, tt.want) {
			t.Errorf("CelsiusToFahrenheit(%v) = %v, а ожидалось %v", tt.c, got, tt.want)
		}
	}
}

func TestAverage(t *testing.T) {
	tests := []struct {
		a, b, c int
		want    float64
	}{
		{1, 2, 3, 2},
		{1, 2, 2, 5.0 / 3.0},
		{0, 0, 1, 1.0 / 3.0},
		{-3, 3, 0, 0},
	}
	for _, tt := range tests {
		if got := Average(tt.a, tt.b, tt.c); !almostEqual(got, tt.want) {
			t.Errorf("Average(%d, %d, %d) = %v, а ожидалось %v", tt.a, tt.b, tt.c, got, tt.want)
		}
	}
}

func TestFormatDuration(t *testing.T) {
	tests := []struct {
		total int
		want  string
	}{
		{0, "00:00:00"},
		{59, "00:00:59"},
		{60, "00:01:00"},
		{3723, "01:02:03"},
		{36000, "10:00:00"},
	}
	for _, tt := range tests {
		if got := FormatDuration(tt.total); got != tt.want {
			t.Errorf("FormatDuration(%d) = %q, а ожидалось %q", tt.total, got, tt.want)
		}
	}
}

func TestWithoutEnds(t *testing.T) {
	tests := []struct{ nums, want []int }{
		{[]int{1, 2, 3, 4}, []int{2, 3}},
		{[]int{5, 6, 7}, []int{6}},
		{[]int{1, 2}, []int{}},
	}
	for _, tt := range tests {
		if got := WithoutEnds(tt.nums); !slices.Equal(got, tt.want) {
			t.Errorf("WithoutEnds(%v) = %v, а ожидалось %v", tt.nums, got, tt.want)
		}
	}
}

func TestLookup(t *testing.T) {
	prices := map[string]int{"чайник": 1500, "даром": 0}
	if got, ok := Lookup(prices, "чайник"); got != 1500 || !ok {
		t.Errorf("Lookup(..., \"чайник\") = %d, %v, а ожидалось 1500, true", got, ok)
	}
	if got, ok := Lookup(prices, "даром"); got != 0 || !ok {
		t.Errorf("Lookup(..., \"даром\") = %d, %v, а ожидалось 0, true (товар есть, просто бесплатный)", got, ok)
	}
	if got, ok := Lookup(prices, "диван"); got != 0 || ok {
		t.Errorf("Lookup(..., \"диван\") = %d, %v, а ожидалось 0, false", got, ok)
	}
}
