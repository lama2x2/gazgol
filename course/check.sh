#!/usr/bin/env bash
# Проверяющая система курса: прогоняет тесты и показывает, сколько задач засчитано.
#
#   ./course/check.sh          — все уроки
#   ./course/check.sh 22       — только урок 2.2
#   ./course/check.sh 22 -v    — урок 2.2 с подробными ошибками
#   ./course/check.sh 101      — урок 10.1

cd "$(dirname "$0")/.." || exit 1

only="$1"
verbose="$2"
total_ok=0
total_all=0

for num in $(ls -d course/lesson*/ | sed 's#course/lesson##; s#/##' | sort -n); do
	dir="course/lesson$num/"
	[[ -n "$only" && "$num" != "$only" ]] && continue

	flags=()
	cat "$dir"*_test.go 2>/dev/null | grep -q "lyceum:race" && flags=(-race) # уроки про конкурентность: ловим гонки данных
	out=$(go test -v -timeout=60s "${flags[@]}" "./$dir" 2>&1)
	ok=$(grep -c '^--- PASS' <<<"$out")
	fail=$(grep -c '^--- FAIL' <<<"$out")
	all=$((ok + fail))
	title=$(sed -n '1{s|^// Урок ||;s|\.$||;p;}' "$dir/tasks.go")

	if [[ $all -eq 0 ]]; then
		echo "💥 ${title}: не компилируется"
		[[ -n "$verbose" || -n "$only" ]] && grep -v '^FAIL' <<<"$out" | sed 's/^/     /'
		continue
	fi

	mark="❌"
	[[ $ok -eq $all ]] && mark="✅"
	printf '%s %s: %d/%d\n' "$mark" "$title" "$ok" "$all"
	total_ok=$((total_ok + ok))
	total_all=$((total_all + all))

	if [[ -n "$verbose" ]]; then
		grep -E '_test\.go:[0-9]+:' <<<"$out" | sed -E 's/^[[:space:]]*/     /'
	fi
done

if [[ -z "$only" ]]; then echo "Итого: ${total_ok}/${total_all} задач"; fi
