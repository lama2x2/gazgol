// sqlrun — песочница для урока 10.1: выполняет SQL на учебной базе Барахолки.
//
//	go run ./course/cmd/sqlrun "SELECT * FROM ads WHERE status = 'active'"
package main

import (
	"database/sql"
	"fmt"
	"os"
	"strings"
	"text/tabwriter"

	"gazgol/course/lesson101"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println(`использование: go run ./course/cmd/sqlrun "SELECT ..."`)
		fmt.Println("таблицы: users(id, name, city), ads(id, user_id, title, price, category, status), deals(id, ad_id, buyer_id, price)")
		os.Exit(2)
	}
	db, err := lesson101.OpenFixture()
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	defer db.Close()

	rows, err := db.Query(strings.Join(os.Args[1:], " "))
	if err != nil {
		fmt.Fprintln(os.Stderr, "ошибка SQL:", err)
		os.Exit(1)
	}
	defer rows.Close()

	cols, _ := rows.Columns()
	w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
	fmt.Fprintln(w, strings.Join(cols, "\t"))
	n := 0
	for rows.Next() {
		vals := make([]sql.NullString, len(cols))
		ptrs := make([]any, len(cols))
		for i := range vals {
			ptrs[i] = &vals[i]
		}
		rows.Scan(ptrs...)
		cells := make([]string, len(cols))
		for i, v := range vals {
			cells[i] = v.String
			if !v.Valid {
				cells[i] = "NULL"
			}
		}
		fmt.Fprintln(w, strings.Join(cells, "\t"))
		n++
	}
	w.Flush()
	fmt.Printf("строк: %d\n", n)
}
