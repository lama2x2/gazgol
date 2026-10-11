package lesson132

import (
	"bytes"
	"io"
	"reflect"
	"testing"
	"unsafe"
)

func TestGoodLayout(t *testing.T) {
	bad, good := reflect.TypeOf(Bad{}), reflect.TypeOf(Good{})
	if good.NumField() != bad.NumField() {
		t.Fatalf("в Good %d полей, а в Bad %d — нужны те же поля", good.NumField(), bad.NumField())
	}
	for i := range bad.NumField() {
		f := bad.Field(i)
		g, ok := good.FieldByName(f.Name)
		if !ok || g.Type != f.Type {
			t.Errorf("в Good нет поля %s %s", f.Name, f.Type)
		}
	}
	if s := unsafe.Sizeof(Bad{}); s != 32 {
		t.Fatalf("Bad занимает %d байт — не меняй её", s)
	}
	if s := unsafe.Sizeof(Good{}); s != 16 {
		t.Errorf("Good занимает %d байт, а можно 16", s)
	}
}

func TestAdKeyAllocs(t *testing.T) {
	cases := []struct {
		cat  string
		max  int64
		tags []string
		want string
	}{
		{"мебель", 5000, []string{"дерево", "б/у"}, "ads:мебель:5000:дерево,б/у"},
		{"cars", 9876543210, nil, "ads:cars:9876543210:"},
		{"", -1, []string{"x"}, "ads::-1:x"},
	}
	for _, c := range cases {
		if got := AdKey(c.cat, c.max, c.tags); got != c.want {
			t.Errorf("AdKey(%q, %d, %q) = %q, а ожидалось %q", c.cat, c.max, c.tags, got, c.want)
		}
	}
	tags := []string{"новое", "доставка", "торг"}
	if a := testing.AllocsPerRun(1000, func() { _ = AdKey("электроника", 1234567, tags) }); a > 1 {
		t.Errorf("AdKey делает %.0f аллокаций на вызов, а нужно не больше 1", a)
	}
}

func TestTotalNoAllocs(t *testing.T) {
	ads := []Ad{{1, "Шкаф", 300000}, {2, "Стул", 150000}, {3, "Лампа", 70000}}
	if got := Total(ads); got != 520000 {
		t.Fatalf("Total = %d, а ожидалось 520000", got)
	}
	if a := testing.AllocsPerRun(1000, func() { _ = Total(ads) }); a > 0 {
		t.Errorf("Total делает %.0f аллокаций на вызов, а нужно 0", a)
	}
}

func TestRenderToAllocs(t *testing.T) {
	var buf bytes.Buffer
	if err := RenderTo(&buf, Ad{ID: 42, Title: "Шкаф"}); err != nil || buf.String() != `{"id":42,"title":"Шкаф"}` {
		t.Fatalf("RenderTo = %q, %v", buf.String(), err)
	}
	ad := Ad{ID: 9876543210, Title: "Велосипед Stels Navigator"}
	for range 10 { // прогреть пул
		RenderTo(io.Discard, ad)
	}
	if a := testing.AllocsPerRun(1000, func() { RenderTo(io.Discard, ad) }); a > 0 {
		t.Errorf("RenderTo делает %.0f аллокаций на вызов, а нужно 0 (sync.Pool + strconv.AppendInt)", a)
	}
}
