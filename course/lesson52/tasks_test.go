package lesson52

import (
	"errors"
	"testing"
	"time"
)

// Проверки на этапе компиляции: все три типа — Delivery.
var (
	_ Delivery = Pickup{}
	_ Delivery = Courier{}
	_ Delivery = Post{}
)

func TestUserContact(t *testing.T) {
	if got, want := (User{"Гоша", 4.83}).Contact(), "Гоша (★4.8)"; got != want {
		t.Errorf("Contact() = %q, а ожидалось %q", got, want)
	}
	if got, want := (User{"Аня", 5}).Contact(), "Аня (★5.0)"; got != want {
		t.Errorf("Contact() = %q, а ожидалось %q", got, want)
	}
}

func TestSellerContact(t *testing.T) {
	s := Seller{User: User{"Гоша", 4.83}, Phone: "+7 900 000-00-00"}
	if got, want := s.Contact(), "Гоша (★4.8), тел. +7 900 000-00-00"; got != want {
		t.Errorf("Seller.Contact() = %q, а ожидалось %q", got, want)
	}
	if s.Name != "Гоша" {
		t.Errorf("s.Name = %q — поле встроенного User должно быть доступно напрямую", s.Name)
	}
}

func TestDeliveries(t *testing.T) {
	tests := []struct {
		d    Delivery
		km   int
		name string
		cost int
	}{
		{Pickup{}, 50, "Самовывоз", 0},
		{Courier{PerKm: 30}, 10, "Курьер", 500},
		{Courier{PerKm: 30}, 0, "Курьер", 200},
		{Post{}, 99, "Почта", 350},
		{Post{}, 250, "Почта", 450},
	}
	for _, tt := range tests {
		if got := tt.d.Name(); got != tt.name {
			t.Errorf("%T.Name() = %q, а ожидалось %q", tt.d, got, tt.name)
		}
		if got := tt.d.Cost(tt.km); got != tt.cost {
			t.Errorf("%T%+v.Cost(%d) = %d, а ожидалось %d", tt.d, tt.d, tt.km, got, tt.cost)
		}
	}
}

func TestCheapest(t *testing.T) {
	opts := []Delivery{Courier{PerKm: 30}, Post{}}
	got, err := Cheapest(opts, 5) // курьер 350, почта 350 → первый
	if err != nil || got != (Courier{PerKm: 30}) {
		t.Errorf("Cheapest(курьер, почта; 5 км) = %v, %v, а ожидался курьер (при равной цене — первый)", got, err)
	}
	got, err = Cheapest(opts, 100) // курьер 3200, почта 400
	if err != nil || got != (Post{}) {
		t.Errorf("Cheapest(курьер, почта; 100 км) = %v, %v, а ожидалась почта", got, err)
	}
	got, err = Cheapest(append(opts, Pickup{}), 100)
	if err != nil || got != (Pickup{}) {
		t.Errorf("Cheapest(…, самовывоз; 100 км) = %v, %v, а ожидался самовывоз", got, err)
	}
	if got, err := Cheapest(nil, 10); err == nil || got != nil {
		t.Errorf("Cheapest(nil) = %v, %v — ожидались nil и ошибка", got, err)
	}
}

type ad struct{}

func (ad) String() string { return "Диван — 12000 ₽" }

func TestDescribe(t *testing.T) {
	tests := []struct {
		v    any
		want string
	}{
		{Pickup{}, "доставка: Самовывоз"},
		{errors.New("нет связи"), "ошибка: нет связи"},
		{ad{}, "Диван — 12000 ₽"},
		{time.Second, "1s"}, // time.Duration — тоже Stringer
		{42, "число 42"},
		{nil, "пусто"},
		{3.14, "неизвестно"},
		{"строка", "неизвестно"},
	}
	for _, tt := range tests {
		if got := Describe(tt.v); got != tt.want {
			t.Errorf("Describe(%#v) = %q, а ожидалось %q", tt.v, got, tt.want)
		}
	}
}
