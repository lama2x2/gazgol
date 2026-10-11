package lesson42

import (
	"slices"
	"testing"
)

func TestSwap(t *testing.T) {
	x, y := 1, 2
	Swap(&x, &y)
	if x != 2 || y != 1 {
		t.Errorf("после Swap(&x, &y) x = %d, y = %d, а ожидалось 2, 1", x, y)
	}
}

func TestValueOr(t *testing.T) {
	n := 42
	if got := ValueOr(&n, 7); got != 42 {
		t.Errorf("ValueOr(&42, 7) = %d, а ожидалось 42", got)
	}
	zero := 0
	if got := ValueOr(&zero, 7); got != 0 {
		t.Errorf("ValueOr(&0, 7) = %d, а ожидалось 0 (указатель не nil, значение просто ноль)", got)
	}
	if got := ValueOr(nil, 7); got != 7 {
		t.Errorf("ValueOr(nil, 7) = %d, а ожидалось 7", got)
	}
}

func TestDoubleInPlace(t *testing.T) {
	nums := []int{1, -2, 3}
	DoubleInPlace(nums)
	if want := []int{2, -4, 6}; !slices.Equal(nums, want) {
		t.Errorf("после DoubleInPlace срез = %v, а ожидалось %v", nums, want)
	}
}

func TestSafeDivide(t *testing.T) {
	defer func() {
		if r := recover(); r != nil {
			t.Fatalf("SafeDivide упала с panic: %v — её нужно поймать через recover", r)
		}
	}()
	if got, err := SafeDivide(7, 2); got != 3 || err != nil {
		t.Errorf("SafeDivide(7, 2) = %d, %v, а ожидалось 3, <nil>", got, err)
	}
	if got, err := SafeDivide(1, 0); err == nil || got != 0 {
		t.Errorf("SafeDivide(1, 0) = %d, %v, а ожидалось 0 и ошибка", got, err)
	}
}

func TestOpenAll(t *testing.T) {
	got := OpenAll([]string{"db", "file", "cache"})
	want := []string{"open db", "open file", "open cache", "close cache", "close file", "close db"}
	if !slices.Equal(got, want) {
		t.Errorf("OpenAll = %q,\nа ожидалось %q", got, want)
	}
}
