package lesson31

import "testing"

func TestSumTo(t *testing.T) {
	tests := []struct{ n, want int }{{5, 15}, {1, 1}, {100, 5050}, {0, 0}, {-7, 0}}
	for _, tt := range tests {
		if got := SumTo(tt.n); got != tt.want {
			t.Errorf("SumTo(%d) = %d, а ожидалось %d", tt.n, got, tt.want)
		}
	}
}

func TestFactorial(t *testing.T) {
	tests := []struct{ n, want int }{{0, 1}, {1, 1}, {5, 120}, {10, 3628800}}
	for _, tt := range tests {
		if got := Factorial(tt.n); got != tt.want {
			t.Errorf("Factorial(%d) = %d, а ожидалось %d", tt.n, got, tt.want)
		}
	}
}

func TestCountDigits(t *testing.T) {
	tests := []struct{ n, want int }{{12345, 5}, {7, 1}, {0, 1}, {-70, 2}, {1000000, 7}}
	for _, tt := range tests {
		if got := CountDigits(tt.n); got != tt.want {
			t.Errorf("CountDigits(%d) = %d, а ожидалось %d", tt.n, got, tt.want)
		}
	}
}

func TestIsPrime(t *testing.T) {
	tests := []struct {
		n    int
		want bool
	}{
		{-5, false}, {0, false}, {1, false}, {2, true}, {3, true}, {4, false},
		{9, false}, {17, true}, {25, false}, {97, true}, {7919, true}, {7917, false},
	}
	for _, tt := range tests {
		if got := IsPrime(tt.n); got != tt.want {
			t.Errorf("IsPrime(%d) = %v, а ожидалось %v", tt.n, got, tt.want)
		}
	}
}

func TestCollatzSteps(t *testing.T) {
	tests := []struct{ n, want int }{{1, 0}, {2, 1}, {6, 8}, {7, 16}, {27, 111}}
	for _, tt := range tests {
		if got := CollatzSteps(tt.n); got != tt.want {
			t.Errorf("CollatzSteps(%d) = %d, а ожидалось %d", tt.n, got, tt.want)
		}
	}
}
