package lesson51

import (
	"fmt"
	"testing"
)

func TestNewAd(t *testing.T) {
	ad, err := NewAd("Велосипед", 5000)
	if err != nil {
		t.Fatalf("NewAd(\"Велосипед\", 5000) вернул ошибку: %v", err)
	}
	if ad == nil || ad.Title != "Велосипед" || ad.price != 5000 || ad.sold {
		t.Errorf("NewAd(\"Велосипед\", 5000) = %#v, а ожидалось Title=Велосипед, price=5000, sold=false", ad)
	}
	for _, title := range []string{"", "   "} {
		if ad, err := NewAd(title, 100); err == nil || ad != nil {
			t.Errorf("NewAd(%q, 100) = %v, %v — ожидались nil и ошибка", title, ad, err)
		}
	}
	if ad, err := NewAd("Стул", -1); err == nil || ad != nil {
		t.Errorf("NewAd(\"Стул\", -1) = %v, %v — ожидались nil и ошибка", ad, err)
	}
	if _, err := NewAd("Даром", 0); err != nil {
		t.Errorf("NewAd(\"Даром\", 0): цена 0 допустима, а вернулась ошибка %v", err)
	}
}

func TestGetters(t *testing.T) {
	ad := &Ad{Title: "Шкаф", price: 3000, sold: true}
	if ad.Price() != 3000 || !ad.IsSold() {
		t.Errorf("Price(), IsSold() = %d, %v, а ожидалось 3000, true", ad.Price(), ad.IsSold())
	}
}

func TestMarkSold(t *testing.T) {
	ad := &Ad{Title: "Шкаф", price: 3000}
	ad.MarkSold()
	if !ad.sold {
		t.Error("после MarkSold() объявление всё ещё не продано")
	}
}

func TestDiscount(t *testing.T) {
	ad := &Ad{Title: "Телевизор", price: 10000}
	if err := ad.Discount(15); err != nil || ad.price != 8500 {
		t.Fatalf("Discount(15) на 10000: цена %d, ошибка %v — ожидалось 8500, <nil>", ad.price, err)
	}
	for _, p := range []int{0, -5, 91, 100} {
		if err := ad.Discount(p); err == nil {
			t.Errorf("Discount(%d) должен вернуть ошибку", p)
		}
		if ad.price != 8500 {
			t.Fatalf("Discount(%d) с ошибкой изменил цену на %d", p, ad.price)
		}
	}
	ad.sold = true
	if err := ad.Discount(10); err == nil || ad.price != 8500 {
		t.Errorf("Discount у проданного: ошибка %v, цена %d — ожидались ошибка и 8500", err, ad.price)
	}
}

func TestString(t *testing.T) {
	ad := Ad{Title: "Велосипед", price: 5000}
	if got, want := ad.String(), "Велосипед — 5000 ₽"; got != want {
		t.Errorf("String() = %q, а ожидалось %q", got, want)
	}
	ad.sold = true
	if got, want := fmt.Sprint(ad), "Велосипед — 5000 ₽ (продано)"; got != want {
		t.Errorf("fmt.Sprint(ad) для проданного = %q, а ожидалось %q", got, want)
	}
}
