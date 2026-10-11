//lyceum:race — проверка запускается с детектором гонок (-race).

package lesson61

import (
	"slices"
	"testing"
	"time"
)

func collect(ch <-chan int) []int {
	var out []int
	timeout := time.After(2 * time.Second)
	for {
		select {
		case v, ok := <-ch:
			if !ok {
				return out
			}
			out = append(out, v)
		case <-timeout:
			return append(out, -999) // канал так и не закрыли
		}
	}
}

func TestGenerate(t *testing.T) {
	if got, want := collect(Generate(5)), []int{1, 2, 3, 4, 5}; !slices.Equal(got, want) {
		t.Errorf("Generate(5) отдал %v, а ожидалось %v (-999 значит, что канал не закрыт)", got, want)
	}
	if got := collect(Generate(0)); len(got) != 0 {
		t.Errorf("Generate(0) отдал %v, а ожидался пустой закрытый канал", got)
	}
}

func TestSquares(t *testing.T) {
	in := make(chan int)
	go func() {
		for _, v := range []int{1, 2, 3, -4} {
			in <- v
		}
		close(in)
	}()
	if got, want := collect(Squares(in)), []int{1, 4, 9, 16}; !slices.Equal(got, want) {
		t.Errorf("Squares(1 2 3 -4) отдал %v, а ожидалось %v", got, want)
	}
}

func TestSumParallel(t *testing.T) {
	nums := make([]int, 1000)
	for i := range nums {
		nums[i] = i + 1
	}
	for _, parts := range []int{1, 3, 4, 7, 0, -2, 5000} {
		if got := SumParallel(nums, parts); got != 500500 {
			t.Errorf("SumParallel(1..1000, %d) = %d, а ожидалось 500500", parts, got)
		}
	}
	if got := SumParallel(nil, 4); got != 0 {
		t.Errorf("SumParallel(nil, 4) = %d, а ожидалось 0", got)
	}
}

func TestWithTimeout(t *testing.T) {
	fast := func() int { return 7 }
	if got, ok := WithTimeout(fast, 500*time.Millisecond); got != 7 || !ok {
		t.Errorf("WithTimeout(быстрая) = %d, %v, а ожидалось 7, true", got, ok)
	}
	slow := func() int { time.Sleep(time.Second); return 1 }
	start := time.Now()
	got, ok := WithTimeout(slow, 50*time.Millisecond)
	if got != 0 || ok {
		t.Errorf("WithTimeout(медленная) = %d, %v, а ожидалось 0, false", got, ok)
	}
	if el := time.Since(start); el > 400*time.Millisecond {
		t.Errorf("WithTimeout ждала %v — нужно вернуться сразу по таймауту (~50ms)", el)
	}
}
