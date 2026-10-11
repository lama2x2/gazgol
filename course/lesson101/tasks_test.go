package lesson101

import (
	"database/sql"
	"fmt"
	"strings"
	"testing"
)

func runQuery(t *testing.T, q string) ([]string, [][]string) {
	t.Helper()
	if strings.TrimSpace(strings.ReplaceAll(q, "-- TODO: твой запрос", "")) == "" {
		t.Fatal("запрос ещё не написан")
	}
	db, err := OpenFixture()
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	rows, err := db.Query(q)
	if err != nil {
		t.Fatalf("ошибка SQL: %v", err)
	}
	defer rows.Close()
	cols, _ := rows.Columns()
	var out [][]string
	for rows.Next() {
		raw := make([]sql.NullString, len(cols))
		ptrs := make([]any, len(cols))
		for i := range raw {
			ptrs[i] = &raw[i]
		}
		if err := rows.Scan(ptrs...); err != nil {
			t.Fatal(err)
		}
		row := make([]string, len(cols))
		for i, v := range raw {
			row[i] = v.String
			if !v.Valid {
				row[i] = "NULL"
			}
		}
		out = append(out, row)
	}
	if err := rows.Err(); err != nil {
		t.Fatal(err)
	}
	return cols, out
}

func check(t *testing.T, q string, wantCols []string, want [][]string) {
	t.Helper()
	cols, got := runQuery(t, q)
	for i := range cols {
		cols[i] = strings.ToLower(cols[i])
	}
	if strings.Join(cols, ",") != strings.Join(wantCols, ",") {
		t.Errorf("колонки %v, а ожидались %v (используй AS для имён)", cols, wantCols)
	}
	if fmt.Sprint(got) != fmt.Sprint(want) {
		t.Errorf("результат:\n  %v\nа ожидалось:\n  %v", got, want)
	}
}

func TestCheapActiveInCity(t *testing.T) {
	check(t, CheapActiveInCity, []string{"title", "price"}, [][]string{
		{"Стул", "1500"}, {"Чайник", "1500"}, {"Самокат", "3000"}, {"Велосипед Stels", "8000"},
	})
}

func TestAdsPerCategory(t *testing.T) {
	check(t, AdsPerCategory, []string{"category", "cnt"}, [][]string{
		{"спорт", "3"}, {"техника", "3"}, {"мебель", "2"},
	})
}

func TestTopSellers(t *testing.T) {
	check(t, TopSellers, []string{"name", "revenue"}, [][]string{
		{"Гоша", "11000"}, {"Ильдар", "6500"}, {"Аня", "6000"},
	})
}

func TestUsersWithoutAds(t *testing.T) {
	check(t, UsersWithoutAds, []string{"name"}, [][]string{{"Петя"}, {"Саша"}})
}

func TestMostExpensivePerCategory(t *testing.T) {
	check(t, MostExpensivePerCategory, []string{"category", "title", "price"}, [][]string{
		{"книги", "Книга про Go", "900"}, {"мебель", "Диван", "25000"},
		{"спорт", "Велосипед Stels", "8000"}, {"техника", "Ноутбук", "45000"},
	})
	if !strings.Contains(strings.ToUpper(MostExpensivePerCategory), "OVER") {
		t.Error("здесь нужна оконная функция (… OVER (PARTITION BY …))")
	}
}
