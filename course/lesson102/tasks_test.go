package lesson102

import (
	"context"
	"errors"
	"testing"
	"time"
)

func setup(t *testing.T) (*Store, context.Context) {
	t.Helper()
	s, err := OpenStore()
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { s.Close() })
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	t.Cleanup(cancel)
	return s, ctx
}

func ptr(s string) *string { return &s }

func mustCreate(t *testing.T, s *Store, ctx context.Context, ad Ad) int64 {
	t.Helper()
	id, err := s.Create(ctx, ad)
	if err != nil {
		t.Fatalf("Create(%+v): %v", ad, err)
	}
	return id
}

func balance(t *testing.T, s *Store, id int64) int64 {
	t.Helper()
	var b int64
	if err := s.db.QueryRow("SELECT balance FROM users WHERE id = ?", id).Scan(&b); err != nil {
		t.Fatal(err)
	}
	return b
}

func TestCreate(t *testing.T) {
	s, ctx := setup(t)
	id1 := mustCreate(t, s, ctx, Ad{UserID: 1, Title: "Велосипед", Price: 5000, Description: ptr("почти новый")})
	id2 := mustCreate(t, s, ctx, Ad{UserID: 2, Title: "Шкаф", Price: 2000})
	if id1 != 1 || id2 != 2 {
		t.Errorf("Create вернул id %d и %d, а ожидались 1 и 2", id1, id2)
	}
	var title, status string
	var desc *string
	if err := s.db.QueryRow("SELECT title, description, status FROM ads WHERE id = 2").Scan(&title, &desc, &status); err != nil {
		t.Fatal(err)
	}
	if title != "Шкаф" || desc != nil || status != "active" {
		t.Errorf("в базе: title %q, description %v, status %q — ожидались Шкаф, NULL, active", title, desc, status)
	}
	if _, err := s.Create(ctx, Ad{UserID: 1, Title: "Минус", Price: -1}); err == nil {
		t.Error("отрицательная цена нарушает CHECK — Create должен вернуть ошибку")
	}
}

func TestGet(t *testing.T) {
	s, ctx := setup(t)
	mustCreate(t, s, ctx, Ad{UserID: 1, Title: "Велосипед", Price: 5000, Description: ptr("почти новый")})
	mustCreate(t, s, ctx, Ad{UserID: 2, Title: "Шкаф", Price: 2000})
	ad, err := s.Get(ctx, 1)
	if err != nil || ad.ID != 1 || ad.UserID != 1 || ad.Title != "Велосипед" || ad.Price != 5000 || ad.Status != "active" ||
		ad.Description == nil || *ad.Description != "почти новый" {
		t.Errorf("Get(1) = %+v, %v", ad, err)
	}
	ad, err = s.Get(ctx, 2)
	if err != nil || ad.Description != nil {
		t.Errorf("Get(2): описание NULL должно стать nil, а получено %+v, %v", ad, err)
	}
	if _, err := s.Get(ctx, 99); !errors.Is(err, ErrNotFound) {
		t.Errorf("Get(99): ожидалась ErrNotFound, а получено %v", err)
	}
}

func TestList(t *testing.T) {
	s, ctx := setup(t)
	for _, ad := range []Ad{
		{UserID: 1, Title: "a", Price: 100}, {UserID: 1, Title: "b", Price: 900}, {UserID: 2, Title: "c", Price: 300},
		{UserID: 2, Title: "d", Price: 5000}, {UserID: 1, Title: "e", Price: 50},
	} {
		mustCreate(t, s, ctx, ad)
	}
	s.db.Exec("UPDATE ads SET status = 'sold' WHERE id = 3")
	ids := func(ads []Ad) []int64 {
		var r []int64
		for _, a := range ads {
			r = append(r, a.ID)
		}
		return r
	}
	cases := []struct {
		f    Filter
		want []int64
	}{
		{Filter{}, []int64{1, 2, 3, 4, 5}},
		{Filter{UserID: 1}, []int64{1, 2, 5}},
		{Filter{Status: "active", MaxPrice: 1000}, []int64{1, 2, 5}},
		{Filter{Status: "sold"}, []int64{3}},
		{Filter{Limit: 2, Offset: 1}, []int64{2, 3}},
		{Filter{UserID: 2, MaxPrice: 400}, []int64{3}},
		{Filter{Status: "x' OR '1'='1"}, nil},
	}
	for _, c := range cases {
		got, err := s.List(ctx, c.f)
		if err != nil {
			t.Errorf("List(%+v): ошибка %v", c.f, err)
			continue
		}
		if g := ids(got); len(g) != len(c.want) || (len(g) > 0 && g[0] != c.want[0]) || (len(g) > 0 && g[len(g)-1] != c.want[len(c.want)-1]) {
			t.Errorf("List(%+v) вернул id %v, а ожидались %v", c.f, g, c.want)
		}
	}
	got, _ := s.List(ctx, Filter{})
	if len(got) > 0 && (got[0].Title != "a" || got[0].Status != "active") {
		t.Errorf("List заполняет не все поля: %+v", got[0])
	}
}

func TestBuy(t *testing.T) {
	s, ctx := setup(t)
	bike := mustCreate(t, s, ctx, Ad{UserID: 2, Title: "Велосипед", Price: 4000})
	sofa := mustCreate(t, s, ctx, Ad{UserID: 1, Title: "Диван", Price: 9000})

	if err := s.Buy(ctx, bike, 1); err != nil {
		t.Fatalf("Buy(велосипед, Гоша): %v", err)
	}
	if b1, b2 := balance(t, s, 1), balance(t, s, 2); b1 != 6000 || b2 != 7000 {
		t.Errorf("после покупки балансы Гоши и Ани: %d и %d, а ожидались 6000 и 7000", b1, b2)
	}
	ad, _ := s.Get(ctx, bike)
	var deals int
	s.db.QueryRow("SELECT COUNT(*) FROM deals WHERE ad_id = ? AND buyer_id = 1 AND price = 4000", bike).Scan(&deals)
	if ad.Status != "sold" || deals != 1 {
		t.Errorf("после покупки: статус %q, сделок %d — ожидались sold и 1", ad.Status, deals)
	}

	cases := []struct {
		name      string
		ad, buyer int64
		want      error
	}{
		{"повторная покупка", bike, 3, ErrAlreadySold},
		{"своё объявление", sofa, 1, ErrOwnAd},
		{"не хватает денег", sofa, 2, ErrNoMoney},
		{"нет объявления", 99, 1, ErrNotFound},
	}
	for _, c := range cases {
		before := [3]int64{balance(t, s, 1), balance(t, s, 2), balance(t, s, 3)}
		err := s.Buy(ctx, c.ad, c.buyer)
		if errors.Is(err, context.DeadlineExceeded) {
			t.Fatalf("%s: Buy завис и упёрся в таймаут — внутри транзакции все запросы должны идти через tx, а не s.db", c.name)
		}
		if !errors.Is(err, c.want) {
			t.Errorf("%s: ошибка %v, а ожидалась %v", c.name, err, c.want)
		}
		after := [3]int64{balance(t, s, 1), balance(t, s, 2), balance(t, s, 3)}
		if before != after {
			t.Errorf("%s: балансы изменились %v → %v, а транзакция должна была откатиться", c.name, before, after)
		}
	}
	if ad, _ := s.Get(ctx, sofa); ad.Status != "active" {
		t.Error("неудачная покупка дивана всё-таки отметила его проданным")
	}
}

func TestBulkCreate(t *testing.T) {
	s, ctx := setup(t)
	err := s.BulkCreate(ctx, []Ad{{UserID: 1, Title: "a", Price: 1}, {UserID: 1, Title: "b", Price: 2}})
	if err != nil {
		t.Fatalf("BulkCreate(2 объявления): %v", err)
	}
	err = s.BulkCreate(ctx, []Ad{{UserID: 2, Title: "c", Price: 3}, {UserID: 2, Title: "d", Price: 4}, {UserID: 2, Title: "плохое", Price: -5}})
	if errors.Is(err, context.DeadlineExceeded) {
		t.Fatal("BulkCreate завис — внутри транзакции используй tx")
	}
	if err == nil {
		t.Error("BulkCreate с отрицательной ценой должен вернуть ошибку")
	}
	var n int
	s.db.QueryRow("SELECT COUNT(*) FROM ads").Scan(&n)
	if n != 2 {
		t.Errorf("в базе %d объявлений, а ожидалось 2: неудачная пачка должна откатиться целиком", n)
	}
}
