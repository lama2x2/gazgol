package lesson11

import "testing"

func TestGreeting(t *testing.T) {
	tests := []struct {
		name string
		want string
	}{
		{"Гоша", "Привет, Гоша!"},
		{"Go", "Привет, Go!"},
		{"Анна-Мария", "Привет, Анна-Мария!"},
	}
	for _, tt := range tests {
		if got := Greeting(tt.name); got != tt.want {
			t.Errorf("Greeting(%q) = %q, а ожидалось %q", tt.name, got, tt.want)
		}
	}
}

func TestPriceTag(t *testing.T) {
	tests := []struct {
		title string
		price int
		want  string
	}{
		{"Велосипед", 5000, "Велосипед: 5000 ₽"},
		{"Ручка", 0, "Ручка: 0 ₽"},
	}
	for _, tt := range tests {
		if got := PriceTag(tt.title, tt.price); got != tt.want {
			t.Errorf("PriceTag(%q, %d) = %q, а ожидалось %q", tt.title, tt.price, got, tt.want)
		}
	}
}

func TestReceipt(t *testing.T) {
	want := "Товар: Чайник\nКол-во: 2\nИтого: 3000 ₽"
	if got := Receipt("Чайник", 2, 1500); got != want {
		t.Errorf("Receipt(\"Чайник\", 2, 1500) =\n%s\nа ожидалось:\n%s", got, want)
	}
	want = "Товар: Диван\nКол-во: 1\nИтого: 12000 ₽"
	if got := Receipt("Диван", 1, 12000); got != want {
		t.Errorf("Receipt(\"Диван\", 1, 12000) =\n%s\nа ожидалось:\n%s", got, want)
	}
}
