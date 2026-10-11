package lesson71

import (
	"slices"
	"testing"
)

func TestTruncate(t *testing.T) {
	tests := []struct {
		s    string
		n    int
		want string
	}{
		{"Велосипед Stels", 9, "Велосипед…"},
		{"Диван", 10, "Диван"},
		{"Диван", 5, "Диван"},
		{"Шкаф-купе", 4, "Шкаф…"},
		{"", 3, ""},
		{"abc", 0, "…"},
	}
	for _, tt := range tests {
		if got := Truncate(tt.s, tt.n); got != tt.want {
			t.Errorf("Truncate(%q, %d) = %q, а ожидалось %q", tt.s, tt.n, got, tt.want)
		}
	}
}

func TestRemoveAt(t *testing.T) {
	s := []int{1, 2, 3, 4}
	got := RemoveAt(s, 1)
	if !slices.Equal(got, []int{1, 3, 4}) {
		t.Errorf("RemoveAt([1 2 3 4], 1) = %v, а ожидалось [1 3 4]", got)
	}
	if !slices.Equal(s, []int{1, 2, 3, 4}) {
		t.Errorf("RemoveAt испортил исходный слайс: стал %v", s)
	}
	if got := RemoveAt([]int{7}, 0); len(got) != 0 {
		t.Errorf("RemoveAt([7], 0) = %v, а ожидался пустой слайс", got)
	}
	s = []int{1, 2, 3}
	got = RemoveAt(s, 2)
	got = append(got, 99)
	if s[2] != 3 {
		t.Errorf("append к результату RemoveAt изменил исходный слайс: %v — результат должен быть независимым", s)
	}
}

func TestChunks(t *testing.T) {
	s := []int{1, 2, 3, 4, 5}
	got := Chunks(s, 2)
	want := [][]int{{1, 2}, {3, 4}, {5}}
	if len(got) != len(want) {
		t.Fatalf("Chunks([1 2 3 4 5], 2) = %v, а ожидалось %v", got, want)
	}
	for i := range want {
		if !slices.Equal(got[i], want[i]) {
			t.Fatalf("Chunks([1 2 3 4 5], 2) = %v, а ожидалось %v", got, want)
		}
	}
	_ = append(got[0], 100)
	if got[1][0] != 3 || s[2] != 3 {
		t.Errorf("append к первому куску испортил второй кусок или исходный слайс: куски %v, исходный %v", got, s)
	}
	if got := Chunks([]int{1, 2, 3}, 5); len(got) != 1 || !slices.Equal(got[0], []int{1, 2, 3}) {
		t.Errorf("Chunks([1 2 3], 5) = %v, а ожидалось [[1 2 3]]", got)
	}
	if got := Chunks(nil, 3); len(got) != 0 {
		t.Errorf("Chunks(nil, 3) = %v, а ожидалось []", got)
	}
}

func TestJoin(t *testing.T) {
	tests := []struct {
		words []string
		sep   string
		want  string
	}{
		{[]string{"a", "b", "c"}, ", ", "a, b, c"},
		{[]string{"один"}, "-", "один"},
		{nil, "-", ""},
		{[]string{"", ""}, "|", "|"},
	}
	for _, tt := range tests {
		if got := Join(tt.words, tt.sep); got != tt.want {
			t.Errorf("Join(%q, %q) = %q, а ожидалось %q", tt.words, tt.sep, got, tt.want)
		}
	}
	words := []string{"велосипед", "диван", "шкаф", "лампа", "стол", "стул", "чайник", "ковёр"}
	allocs := testing.AllocsPerRun(100, func() { _ = Join(words, ", ") })
	if allocs > 1 {
		t.Errorf("Join делает %.0f аллокаций на вызов, а нужно не больше 1 — посчитай длину и вызови Grow", allocs)
	}
}

func TestCompact(t *testing.T) {
	tests := []struct{ in, want []string }{
		{[]string{"a", "a", "b", "a", "a"}, []string{"a", "b", "a"}},
		{[]string{"x", "y", "z"}, []string{"x", "y", "z"}},
		{[]string{"k", "k", "k"}, []string{"k"}},
		{[]string{}, []string{}},
	}
	for _, tt := range tests {
		in := slices.Clone(tt.in)
		if got := Compact(in); !slices.Equal(got, tt.want) {
			t.Errorf("Compact(%q) = %q, а ожидалось %q", tt.in, got, tt.want)
		}
	}
	data := []string{"a", "a", "b", "b", "c"}
	buf := make([]string, len(data))
	allocs := testing.AllocsPerRun(100, func() {
		copy(buf, data)
		_ = Compact(buf)
	})
	if allocs > 0 {
		t.Errorf("Compact делает %.0f аллокаций, а нужно 0 — работай в том же массиве", allocs)
	}
	s := []string{"a", "a", "b"}
	if got := Compact(s); len(got) > 0 && &got[0] != &s[0] {
		t.Errorf("Compact вернул слайс на другой массив — нужно переиспользовать исходный")
	}
}
