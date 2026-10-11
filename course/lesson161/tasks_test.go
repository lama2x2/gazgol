package lesson161

import (
	"context"
	"encoding/json"
	"errors"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
)

// ---------- фейки ----------

type txKey struct{}

type tx struct {
	sold      []int64
	transfers [][3]int64
	requests  map[string]error
}

type world struct {
	mu         sync.Mutex
	ads        map[int64]Ad
	balance    map[int64]int64
	requests   map[string]error
	notified   []int64
	violations []string
	failNotify bool
	commits    int
}

func newWorld() *world {
	return &world{
		ads:      map[int64]Ad{1: {1, 10, 3000, false}, 2: {2, 10, 9000, false}, 3: {3, 10, 100, true}},
		balance:  map[int64]int64{10: 0, 20: 5000, 30: 100},
		requests: map[string]error{},
	}
}

func (w *world) tx(ctx context.Context, op string) *tx {
	t, _ := ctx.Value(txKey{}).(*tx)
	if t == nil {
		w.violations = append(w.violations, op+" вызван вне транзакции")
	}
	return t
}

type fakeTx struct{ w *world }

func (f fakeTx) WithinTx(ctx context.Context, fn func(ctx context.Context) error) error {
	t := &tx{requests: map[string]error{}}
	if err := fn(context.WithValue(ctx, txKey{}, t)); err != nil {
		return err // откат: изменения t выбрасываются
	}
	f.w.mu.Lock()
	defer f.w.mu.Unlock()
	for _, id := range t.sold {
		ad := f.w.ads[id]
		ad.Sold = true
		f.w.ads[id] = ad
	}
	for _, tr := range t.transfers {
		f.w.balance[tr[0]] -= tr[2]
		f.w.balance[tr[1]] += tr[2]
	}
	for k, v := range t.requests {
		f.w.requests[k] = v
	}
	f.w.commits++
	return nil
}

type fakeAds struct{ w *world }

func (f fakeAds) Get(ctx context.Context, id int64) (Ad, error) {
	f.w.tx(ctx, "Ads.Get")
	f.w.mu.Lock()
	defer f.w.mu.Unlock()
	ad, ok := f.w.ads[id]
	if !ok {
		return Ad{}, ErrNotFound
	}
	return ad, nil
}
func (f fakeAds) MarkSold(ctx context.Context, id int64) error {
	if t := f.w.tx(ctx, "Ads.MarkSold"); t != nil {
		t.sold = append(t.sold, id)
	}
	return nil
}

type fakeWallets struct{ w *world }

func (f fakeWallets) Balance(ctx context.Context, user int64) (int64, error) {
	f.w.tx(ctx, "Wallets.Balance")
	f.w.mu.Lock()
	defer f.w.mu.Unlock()
	return f.w.balance[user], nil
}
func (f fakeWallets) Transfer(ctx context.Context, from, to, amount int64) error {
	if t := f.w.tx(ctx, "Wallets.Transfer"); t != nil {
		t.transfers = append(t.transfers, [3]int64{from, to, amount})
	}
	return nil
}

type fakeNotifier struct{ w *world }

func (f fakeNotifier) AdSold(ctx context.Context, adID, buyerID int64) error {
	if ctx.Value(txKey{}) != nil {
		f.w.violations = append(f.w.violations, "уведомление отправлено изнутри транзакции")
	}
	f.w.mu.Lock()
	defer f.w.mu.Unlock()
	f.w.notified = append(f.w.notified, adID)
	if f.w.failNotify {
		return errors.New("smtp down")
	}
	return nil
}

type fakeRequests struct{ w *world }

func (f fakeRequests) Seen(ctx context.Context, id string) (bool, error, error) {
	f.w.mu.Lock()
	defer f.w.mu.Unlock()
	r, ok := f.w.requests[id]
	return ok, r, nil
}
func (f fakeRequests) Save(ctx context.Context, id string, result error) error {
	if t, _ := ctx.Value(txKey{}).(*tx); t != nil {
		t.requests[id] = result
		return nil
	}
	f.w.mu.Lock()
	defer f.w.mu.Unlock()
	f.w.requests[id] = result
	return nil
}

func service(w *world) *Service {
	return &Service{Ads: fakeAds{w}, Wallets: fakeWallets{w}, Tx: fakeTx{w}, Notify: fakeNotifier{w}}
}

// ---------- тесты ----------

func TestBuyRules(t *testing.T) {
	w := newWorld()
	s := service(w)
	ctx := context.Background()
	cases := []struct {
		name      string
		buyer, ad int64
		want      error
	}{
		{"нет объявления", 20, 99, ErrNotFound},
		{"своё объявление", 10, 1, ErrForbidden},
		{"уже продано", 20, 3, ErrConflict},
		{"не хватает денег", 30, 1, ErrNoMoney},
	}
	for _, c := range cases {
		if err := s.Buy(ctx, "", c.buyer, c.ad); !errors.Is(err, c.want) {
			t.Errorf("%s: Buy = %v, а ожидалось %v", c.name, err, c.want)
		}
	}
	if err := s.Buy(ctx, "", 20, 1); err != nil {
		t.Fatalf("успешная покупка: %v", err)
	}
	if !w.ads[1].Sold || w.balance[20] != 2000 || w.balance[10] != 3000 {
		t.Errorf("после покупки: продано=%v, баланс покупателя %d (ожидалось 2000), продавца %d (ожидалось 3000)",
			w.ads[1].Sold, w.balance[20], w.balance[10])
	}
}

func TestBuyTxAndNotify(t *testing.T) {
	w := newWorld()
	s := service(w)
	ctx := context.Background()
	s.Buy(ctx, "", 20, 1)
	s.Buy(ctx, "", 30, 2) // нет денег
	if len(w.violations) > 0 {
		t.Errorf("нарушения: %v", w.violations)
	}
	if len(w.notified) != 1 || w.notified[0] != 1 {
		t.Errorf("уведомления: %v — ожидалось одно, об объявлении 1 (неудачная покупка не уведомляет)", w.notified)
	}
	if w.commits != 1 {
		t.Errorf("коммитов %d, а ожидался 1 — вся покупка должна идти через WithinTx", w.commits)
	}
	w2 := newWorld()
	w2.failNotify = true
	if err := service(w2).Buy(ctx, "", 20, 1); err != nil {
		t.Errorf("ошибка уведомления после коммита не должна возвращаться: %v", err)
	}
}

type fakeBuyer struct {
	err             error
	gotBuyer, gotAd int64
	gotReq          string
}

func (f *fakeBuyer) Buy(ctx context.Context, req string, buyer, ad int64) error {
	f.gotReq, f.gotBuyer, f.gotAd = req, buyer, ad
	return f.err
}

func TestBuyHandler(t *testing.T) {
	send := func(b Buyer, path, user string) *httptest.ResponseRecorder {
		req := httptest.NewRequest("POST", path, nil)
		if user != "" {
			req.Header.Set("X-User-ID", user)
		}
		req.Header.Set("Idempotency-Key", "k-1")
		rec := httptest.NewRecorder()
		BuyHandler(b).ServeHTTP(rec, req)
		return rec
	}
	fb := &fakeBuyer{}
	rec := send(fb, "/ads/5/buy", "42")
	var body map[string]string
	json.Unmarshal(rec.Body.Bytes(), &body)
	if rec.Code != 200 || body["status"] != "sold" || fb.gotAd != 5 || fb.gotBuyer != 42 || fb.gotReq != "k-1" {
		t.Errorf("успех: статус %d, тело %q, вызов Buy(%q, %d, %d)", rec.Code, rec.Body.String(), fb.gotReq, fb.gotBuyer, fb.gotAd)
	}
	for _, c := range []struct {
		err  error
		code int
	}{
		{ErrNotFound, 404}, {ErrForbidden, 403}, {ErrConflict, 409}, {ErrNoMoney, 409},
		{errors.New("db down"), 500}, {errors.Join(errors.New("ctx"), ErrConflict), 409},
	} {
		if rec := send(&fakeBuyer{err: c.err}, "/ads/5/buy", "42"); rec.Code != c.code {
			t.Errorf("ошибка %v: статус %d, а ожидался %d", c.err, rec.Code, c.code)
		}
	}
	if rec := send(fb, "/ads/abc/buy", "42"); rec.Code != 400 {
		t.Errorf("id объявления abc: статус %d, а ожидался 400", rec.Code)
	}
	if rec := send(fb, "/ads/5/buy", "гоша"); rec.Code != 400 {
		t.Errorf("X-User-ID не число: статус %d, а ожидался 400", rec.Code)
	}
}

func TestPrice(t *testing.T) {
	if _, err := NewPrice(-1); err == nil {
		t.Error("NewPrice(-1) должен вернуть ошибку")
	}
	cases := map[int64]string{0: "0 ₽", 999: "999 ₽", 1500: "1 500 ₽", 12000000: "12 000 000 ₽"}
	for rub, want := range cases {
		p, err := NewPrice(rub)
		if err != nil || p.String() != want || p.Kopecks() != rub*100 {
			t.Errorf("NewPrice(%d): %q, копеек %d, err %v — ожидалось %q", rub, p.String(), p.Kopecks(), err, want)
		}
	}
	a, _ := NewPrice(1000)
	b, _ := NewPrice(500)
	sum := a.Add(b)
	if sum.String() != "1 500 ₽" || a.String() != "1 000 ₽" {
		t.Errorf("Add: сумма %q, первое слагаемое стало %q — исходные значения меняться не должны", sum, a)
	}
	if got := (Price{kopecks: 9990}).String(); got != "99,90 ₽" {
		t.Errorf("99 руб. 90 коп. = %q, а ожидалось \"99,90 ₽\"", got)
	}
	if got := (Price{kopecks: 150005}).String(); !strings.HasPrefix(got, "1 500,05") {
		t.Errorf("1500 руб. 05 коп. = %q", got)
	}
}

func TestBuyIdempotent(t *testing.T) {
	w := newWorld()
	s := service(w)
	s.Requests = fakeRequests{w}
	ctx := context.Background()
	for range 3 {
		if err := s.Buy(ctx, "req-1", 20, 1); err != nil {
			t.Fatalf("Buy(req-1): %v", err)
		}
	}
	if w.balance[20] != 2000 || w.balance[10] != 3000 {
		t.Errorf("три повтора одного запроса: баланс покупателя %d (ожидалось 2000) — списано несколько раз", w.balance[20])
	}
	if len(w.notified) != 1 {
		t.Errorf("уведомлений %d, а повтор не должен уведомлять снова", len(w.notified))
	}
	for range 2 {
		if err := s.Buy(ctx, "req-2", 30, 2); !errors.Is(err, ErrNoMoney) {
			t.Errorf("повтор неудачного запроса должен вернуть ту же ошибку, а вернул %v", err)
		}
	}
	if err := s.Buy(ctx, "req-3", 20, 1); !errors.Is(err, ErrConflict) {
		t.Errorf("новый запрос на уже проданное: %v", err)
	}
}
