package lesson41

import "testing"

func TestMinMax(t *testing.T) {
	tests := []struct{ a, b, c, min, max int }{
		{3, 1, 2, 1, 3},
		{1, 2, 3, 1, 3},
		{3, 2, 1, 1, 3},
		{5, 5, 5, 5, 5},
		{-1, 0, -7, -7, 0},
	}
	for _, tt := range tests {
		gotMin, gotMax := MinMax(tt.a, tt.b, tt.c)
		if gotMin != tt.min || gotMax != tt.max {
			t.Errorf("MinMax(%d, %d, %d) = %d, %d, а ожидалось %d, %d",
				tt.a, tt.b, tt.c, gotMin, gotMax, tt.min, tt.max)
		}
	}
}

func TestMaxOf(t *testing.T) {
	if got, ok := MaxOf(3, 9, 2); got != 9 || !ok {
		t.Errorf("MaxOf(3, 9, 2) = %d, %v, а ожидалось 9, true", got, ok)
	}
	if got, ok := MaxOf(-5, -2, -9); got != -2 || !ok {
		t.Errorf("MaxOf(-5, -2, -9) = %d, %v, а ожидалось -2, true", got, ok)
	}
	nums := []int{4, 8, 1}
	if got, ok := MaxOf(nums...); got != 8 || !ok {
		t.Errorf("MaxOf(nums...) = %d, %v, а ожидалось 8, true", got, ok)
	}
	if got, ok := MaxOf(); got != 0 || ok {
		t.Errorf("MaxOf() = %d, %v, а ожидалось 0, false", got, ok)
	}
}

func TestFib(t *testing.T) {
	tests := []struct{ n, want int }{{0, 0}, {1, 1}, {2, 1}, {7, 13}, {20, 6765}}
	for _, tt := range tests {
		if got := Fib(tt.n); got != tt.want {
			t.Errorf("Fib(%d) = %d, а ожидалось %d", tt.n, got, tt.want)
		}
	}
}

func TestNewCounter(t *testing.T) {
	a := NewCounter()
	b := NewCounter()
	for want := 1; want <= 3; want++ {
		if got := a(); got != want {
			t.Fatalf("счётчик a: вызов №%d вернул %d, а ожидалось %d", want, got, want)
		}
	}
	if got := b(); got != 1 {
		t.Errorf("новый счётчик b должен начинаться с 1, а вернул %d — счётчики не должны быть общими", got)
	}
}

func TestApplyTwice(t *testing.T) {
	plus3 := func(n int) int { return n + 3 }
	double := func(n int) int { return n * 2 }
	if got := ApplyTwice(plus3, 10); got != 16 {
		t.Errorf("ApplyTwice(+3, 10) = %d, а ожидалось 16", got)
	}
	if got := ApplyTwice(double, 5); got != 20 {
		t.Errorf("ApplyTwice(*2, 5) = %d, а ожидалось 20", got)
	}
}
