package lesson151

import (
	"context"
	"database/sql"
	"errors"
	"slices"
	"strings"
	"sync"
	"testing"
)

func open(t *testing.T) *sql.DB {
	t.Helper()
	db, err := Open()
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { db.Close() })
	return db
}

func written(t *testing.T, q string) {
	t.Helper()
	if strings.TrimSpace(strings.ReplaceAll(strings.ReplaceAll(q, "-- TODO: твой запрос", ""), "-- TODO: CREATE INDEX ...", "")) == "" {
		t.Fatal("запрос ещё не написан")
	}
}

type row struct{ id, price int64 }

func TestKeysetPagination(t *testing.T) {
	written(t, NextPageSQL)
	db := open(t)
	var all []row
	rows, _ := db.Query("SELECT id, price FROM ads WHERE status = 'active' ORDER BY price, id")
	for rows.Next() {
		var r row
		rows.Scan(&r.id, &r.price)
		all = append(all, r)
	}
	rows.Close()

	var got []row
	last := row{-1, -1}
	for page := 0; page < 200; page++ {
		rs, err := db.Query(NextPageSQL, last.price, last.id, 50)
		if err != nil {
			t.Fatalf("ошибка SQL: %v", err)
		}
		n := 0
		for rs.Next() {
			var r row
			if err := rs.Scan(&r.id, &r.price); err != nil {
				t.Fatalf("колонки должны быть id, price: %v", err)
			}
			got = append(got, r)
			last = r
			n++
		}
		rs.Close()
		if n > 50 {
			t.Fatalf("страница из %d строк при размере 50", n)
		}
		if n < 50 {
			break
		}
	}
	if !slices.Equal(got, all) {
		t.Errorf("пройдя все страницы, получили %d строк вместо %d (или в другом порядке) — потери или дубли на границах страниц", len(got), len(all))
	}
}

func TestIndexPlan(t *testing.T) {
	written(t, IndexSQL)
	db := open(t)
	if _, err := db.Exec(IndexSQL); err != nil {
		t.Fatalf("ошибка в CREATE INDEX: %v", err)
	}
	rows, err := db.Query("EXPLAIN QUERY PLAN SELECT id, price FROM ads WHERE category = ? AND status = 'active' ORDER BY price LIMIT 20", "мебель")
	if err != nil {
		t.Fatal(err)
	}
	var plan []string
	for rows.Next() {
		var id, parent, notused int
		var detail string
		rows.Scan(&id, &parent, &notused, &detail)
		plan = append(plan, detail)
	}
	rows.Close()
	p := strings.Join(plan, " | ")
	if !strings.Contains(p, "SEARCH") || !strings.Contains(p, "INDEX") {
		t.Errorf("план: %s — запрос должен искать по индексу (SEARCH ... USING INDEX), а не сканировать таблицу", p)
	}
	if strings.Contains(p, "TEMP B-TREE") {
		t.Errorf("план: %s — есть сортировка во временном дереве; добавь колонку сортировки в конец индекса", p)
	}
}

func TestClaimJobs(t *testing.T) {
	db := open(t)
	ctx := context.Background()
	ids, err := ClaimJobs(ctx, db, "w0", 3)
	slices.Sort(ids) // порядок строк в RETURNING не гарантирован
	if err != nil || !slices.Equal(ids, []int64{1, 2, 3}) {
		t.Fatalf("ClaimJobs(w0, 3) = %v, %v — ожидались задачи 1, 2, 3", ids, err)
	}
	var mu sync.Mutex
	seen := map[int64]string{1: "w0", 2: "w0", 3: "w0"}
	var wg sync.WaitGroup
	for w := range 5 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			name := string(rune('a' + w))
			for {
				ids, err := ClaimJobs(ctx, db, name, 4)
				if err != nil {
					t.Error(err)
					return
				}
				if len(ids) == 0 {
					return
				}
				mu.Lock()
				for _, id := range ids {
					if prev, dup := seen[id]; dup {
						t.Errorf("задачу %d взяли и %s, и %s", id, prev, name)
					}
					seen[id] = name
				}
				mu.Unlock()
			}
		}()
	}
	wg.Wait()
	if len(seen) != 30 {
		t.Errorf("разобрано %d задач из 30", len(seen))
	}
	var running int
	db.QueryRow("SELECT COUNT(*) FROM jobs WHERE status = 'running' AND worker IS NOT NULL").Scan(&running)
	if running != 30 {
		t.Errorf("в статусе running с воркером %d задач, а ожидалось 30", running)
	}
}

func TestOptimisticLock(t *testing.T) {
	db := open(t)
	ctx := context.Background()
	if err := UpdatePrice(ctx, db, 10, 1, 999); err != nil {
		t.Fatalf("UpdatePrice с верной версией: %v", err)
	}
	var price, version int64
	db.QueryRow("SELECT price, version FROM ads WHERE id = 10").Scan(&price, &version)
	if price != 999 || version != 2 {
		t.Errorf("после обновления price=%d version=%d, ожидалось 999 и 2", price, version)
	}
	if err := UpdatePrice(ctx, db, 10, 1, 500); !errors.Is(err, ErrConflict) {
		t.Errorf("обновление со старой версией 1: %v, а ожидался ErrConflict", err)
	}
	if err := UpdatePrice(ctx, db, 99999, 1, 500); !errors.Is(err, ErrNotFound) {
		t.Errorf("несуществующее объявление: %v, а ожидался ErrNotFound", err)
	}
	db.QueryRow("SELECT price FROM ads WHERE id = 10").Scan(&price)
	if price != 999 {
		t.Error("конфликтное обновление всё-таки изменило цену")
	}
}

func TestUpsertViews(t *testing.T) {
	db := open(t)
	ctx := context.Background()
	var wg sync.WaitGroup
	for range 100 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if err := CountView(ctx, db, 7, "2026-10-11"); err != nil {
				t.Error(err)
			}
		}()
	}
	wg.Wait()
	CountView(ctx, db, 7, "2026-10-12")
	var a, b int
	db.QueryRow("SELECT views FROM ad_views WHERE ad_id = 7 AND day = '2026-10-11'").Scan(&a)
	db.QueryRow("SELECT views FROM ad_views WHERE ad_id = 7 AND day = '2026-10-12'").Scan(&b)
	if a != 100 || b != 1 {
		t.Errorf("просмотры: %d и %d, а ожидалось 100 и 1", a, b)
	}
}
