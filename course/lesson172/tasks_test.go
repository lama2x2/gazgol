//lyceum:race — проверка запускается с детектором гонок (-race).

package lesson172

import (
	"context"
	"errors"
	"fmt"
	"slices"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func TestPartition(t *testing.T) {
	if Partition("ad:42", 8) != Partition("ad:42", 8) {
		t.Fatal("один ключ должен всегда давать одну партицию")
	}
	if got := Partition("ad:42", 8); got != 4 {
		t.Errorf("Partition(\"ad:42\", 8) = %d, а FNV-1a даёт 4", got)
	}
	count := make([]int, 6)
	for i := range 6000 {
		p := Partition(fmt.Sprint("user:", i), 6)
		if p < 0 || p >= 6 {
			t.Fatalf("партиция %d вне диапазона 0..5", p)
		}
		count[p]++
	}
	for p, c := range count {
		if c < 700 || c > 1300 {
			t.Errorf("в партицию %d попало %d ключей из 6000 — распределение неравномерное", p, c)
		}
	}
}

type fakeOutbox struct {
	mu     sync.Mutex
	events []Event
	sent   map[string]bool
}

func (o *fakeOutbox) FetchUnsent(_ context.Context, limit int) ([]Event, error) {
	o.mu.Lock()
	defer o.mu.Unlock()
	var res []Event
	for _, e := range o.events {
		if !o.sent[e.ID] && len(res) < limit {
			res = append(res, e)
		}
	}
	return res, nil
}
func (o *fakeOutbox) MarkSent(_ context.Context, ids []string) error {
	o.mu.Lock()
	defer o.mu.Unlock()
	for _, id := range ids {
		o.sent[id] = true
	}
	return nil
}

type fakePub struct {
	got    []string
	failOn string
}

func (p *fakePub) Publish(_ context.Context, e Event) error {
	if e.ID == p.failOn {
		return errors.New("kafka unavailable")
	}
	p.got = append(p.got, e.ID)
	return nil
}

func TestOutboxRelay(t *testing.T) {
	ob := &fakeOutbox{sent: map[string]bool{}}
	for i := 1; i <= 7; i++ {
		ob.events = append(ob.events, Event{ID: fmt.Sprint("e", i), Topic: "ads.sold"})
	}
	pub := &fakePub{failOn: "e4"}
	r := &Relay{Outbox: ob, Publisher: pub, Batch: 5}
	n, err := r.RunOnce(context.Background())
	if err == nil || n != 3 {
		t.Errorf("ошибка на e4: RunOnce = %d, %v — ожидалось 3 и ошибка", n, err)
	}
	if !slices.Equal(pub.got, []string{"e1", "e2", "e3"}) {
		t.Errorf("опубликованы %v — после ошибки публиковать дальше нельзя (порядок)", pub.got)
	}
	if !ob.sent["e1"] || !ob.sent["e3"] || ob.sent["e4"] || ob.sent["e5"] {
		t.Errorf("помечены отправленными: %v — нужно ровно e1..e3", ob.sent)
	}
	pub.failOn = ""
	n, err = r.RunOnce(context.Background())
	if err != nil || n != 4 || !slices.Equal(pub.got[3:], []string{"e4", "e5", "e6", "e7"}) {
		t.Errorf("второй проход: %d, %v, опубликованы %v", n, err, pub.got)
	}
	if n, _ := r.RunOnce(context.Background()); n != 0 {
		t.Errorf("пустой outbox: опубликовано %d", n)
	}
}

type txKey struct{}

type fakeStore struct {
	mu         sync.Mutex
	processed  map[string]bool
	bonus      map[int64]int64
	failAfter  bool
	violations []string
}

func (s *fakeStore) WithinTx(ctx context.Context, fn func(ctx context.Context) error) error {
	s.mu.Lock() // транзакции сериализуются, как на одной строке
	defer s.mu.Unlock()
	snapP, snapB := map[string]bool{}, map[int64]int64{}
	for k, v := range s.processed {
		snapP[k] = v
	}
	for k, v := range s.bonus {
		snapB[k] = v
	}
	if err := fn(context.WithValue(ctx, txKey{}, true)); err != nil {
		s.processed, s.bonus = snapP, snapB
		return err
	}
	return nil
}
func (s *fakeStore) check(ctx context.Context, op string) {
	if ctx.Value(txKey{}) == nil {
		s.violations = append(s.violations, op+" вне транзакции")
	}
}
func (s *fakeStore) Processed(ctx context.Context, id string) (bool, error) {
	s.check(ctx, "Processed")
	return s.processed[id], nil
}
func (s *fakeStore) MarkProcessed(ctx context.Context, id string) error {
	s.check(ctx, "MarkProcessed")
	if s.failAfter {
		return errors.New("db crash")
	}
	s.processed[id] = true
	return nil
}
func (s *fakeStore) AddBonus(ctx context.Context, user, amount int64) error {
	s.check(ctx, "AddBonus")
	s.bonus[user] += amount
	return nil
}

func TestIdempotentConsumer(t *testing.T) {
	st := &fakeStore{processed: map[string]bool{}, bonus: map[int64]int64{}}
	c := &Consumer{Store: st}
	ctx := context.Background()
	var wg sync.WaitGroup
	for range 5 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if err := c.Handle(ctx, Message{ID: "m1", UserID: 7, Bonus: 100}); err != nil {
				t.Error(err)
			}
		}()
	}
	wg.Wait()
	c.Handle(ctx, Message{ID: "m2", UserID: 7, Bonus: 50})
	if st.bonus[7] != 150 {
		t.Errorf("бонус = %d, а ожидалось 150 — дубли m1 начислены повторно", st.bonus[7])
	}
	if len(st.violations) > 0 {
		t.Errorf("нарушения: %v", st.violations[:1])
	}
	st.failAfter = true
	if err := c.Handle(ctx, Message{ID: "m3", UserID: 7, Bonus: 999}); err == nil {
		t.Error("ошибка MarkProcessed должна вернуться")
	}
	if st.bonus[7] != 150 {
		t.Errorf("сбой после начисления: бонус %d — эффект и отметка должны быть в одной транзакции", st.bonus[7])
	}
}

func TestSaga(t *testing.T) {
	var log []string
	step := func(name string, fail, failComp bool) Step {
		return Step{
			Name: name,
			Do: func(ctx context.Context) error {
				log = append(log, "do "+name)
				if fail {
					return errors.New(name + " failed")
				}
				return nil
			},
			Compensate: func(ctx context.Context) error {
				log = append(log, "undo "+name)
				if failComp {
					return errors.New("undo " + name + " failed")
				}
				return nil
			},
		}
	}
	ctx := context.Background()
	if err := RunSaga(ctx, []Step{step("pay", false, false), step("reserve", false, false)}); err != nil || strings.Join(log, ",") != "do pay,do reserve" {
		t.Errorf("успешная сага: %v, лог %v", err, log)
	}
	log = nil
	err := RunSaga(ctx, []Step{step("pay", false, false), step("reserve", false, false), step("ship", true, false)})
	if err == nil || !strings.Contains(err.Error(), "ship failed") {
		t.Errorf("ошибка шага ship должна вернуться, а получено %v", err)
	}
	if got := strings.Join(log, ","); got != "do pay,do reserve,do ship,undo reserve,undo pay" {
		t.Errorf("лог: %s — компенсировать выполненные шаги в обратном порядке, неудачный не компенсировать", got)
	}
	log = nil
	err = RunSaga(ctx, []Step{step("pay", false, true), step("ship", true, false)})
	if err == nil || !strings.Contains(err.Error(), "ship failed") || !strings.Contains(err.Error(), "undo pay failed") {
		t.Errorf("ошибка компенсации тоже должна попасть в результат: %v", err)
	}
}

func TestOrdered(t *testing.T) {
	var msgs []KeyedMsg
	for seq := range 20 {
		for k := range 8 {
			msgs = append(msgs, KeyedMsg{Key: fmt.Sprint("ad", k), Seq: seq})
		}
	}
	var mu sync.Mutex
	last := map[string]int{}
	var active, peak atomic.Int32
	done := make(chan struct{})
	go func() {
		ProcessOrdered(msgs, 4, func(m KeyedMsg) {
			n := active.Add(1)
			for {
				p := peak.Load()
				if n <= p || peak.CompareAndSwap(p, n) {
					break
				}
			}
			time.Sleep(time.Millisecond)
			mu.Lock()
			if prev, ok := last[m.Key]; ok && m.Seq != prev+1 {
				t.Errorf("ключ %s: сообщение %d после %d — порядок нарушен", m.Key, m.Seq, prev)
			}
			last[m.Key] = m.Seq
			mu.Unlock()
			active.Add(-1)
		})
		close(done)
	}()
	select {
	case <-done:
	case <-time.After(5 * time.Second):
		t.Fatal("ProcessOrdered не завершился")
	}
	if len(last) != 8 || last["ad3"] != 19 {
		t.Errorf("обработаны не все сообщения: %v", last)
	}
	if peak.Load() < 2 {
		t.Error("разные ключи должны обрабатываться параллельно")
	}
}
