//lyceum:race — проверка запускается с детектором гонок (-race).

package lesson62

import (
	"slices"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func TestViewCounter(t *testing.T) {
	var c ViewCounter
	var wg sync.WaitGroup
	for range 1000 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			c.Inc()
		}()
	}
	wg.Wait()
	if got := c.Value(); got != 1000 {
		t.Errorf("после 1000 параллельных Inc() Value() = %d, а ожидалось 1000", got)
	}
}

func TestFetchAll(t *testing.T) {
	urls := []string{"a", "bb", "ccc", "dddd", "eeeee", "ffffff", "g", "hh", "iii", "jjjj"}
	fetch := func(url string) int {
		time.Sleep(100 * time.Millisecond)
		return len(url)
	}
	start := time.Now()
	got := FetchAll(urls, fetch)
	el := time.Since(start)
	want := []int{1, 2, 3, 4, 5, 6, 1, 2, 3, 4}
	if !slices.Equal(got, want) {
		t.Errorf("FetchAll = %v, а ожидалось %v", got, want)
	}
	if el > 600*time.Millisecond {
		t.Errorf("FetchAll заняла %v: 10 запросов по 100ms должны идти параллельно (~100ms), а не по очереди (~1s)", el)
	}
}

func TestWorkerPool(t *testing.T) {
	jobs := make([]int, 20)
	for i := range jobs {
		jobs[i] = i
	}
	var running, peak atomic.Int32
	f := func(x int) int {
		n := running.Add(1)
		for {
			p := peak.Load()
			if n <= p || peak.CompareAndSwap(p, n) {
				break
			}
		}
		time.Sleep(20 * time.Millisecond)
		running.Add(-1)
		return x * x
	}
	got := WorkerPool(jobs, 4, f)
	want := make([]int, 20)
	for i := range want {
		want[i] = i * i
	}
	if !slices.Equal(got, want) {
		t.Errorf("WorkerPool = %v, а ожидалось %v", got, want)
	}
	if p := peak.Load(); p > 4 {
		t.Errorf("одновременно работало %d горутин, а лимит — 4", p)
	}
	if p := peak.Load(); p < 2 {
		t.Errorf("одновременно работало максимум %d — задачи выполняются не параллельно", p)
	}
}
