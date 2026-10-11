package lesson82

import (
	"testing"
)

// Напиши тесты для ShippingCost из tasks.go.
//
// Проверка запустит их дважды:
//   - на правильной реализации — все тесты должны пройти;
//   - на 7 «мутантах» — копиях ShippingCost с подложенным багом.
//     Мутант считается пойманным, если хотя бы один твой тест на нём упал.
//
// Думай о границах (что ровно на 5 км? ровно 10 кг?), об ошибках
// и о сочетаниях правил. Одного «обычного» случая мало.

func TestShippingCost(t *testing.T) {
	tests := []struct {
		name     string
		weight   float64
		distance int
		express  bool
		want     int
	}{
		{"обычная доставка", 2, 20, false, 400},
		// TODO: добавь свои случаи
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ShippingCost(tt.weight, tt.distance, tt.express)
			if err != nil {
				t.Fatalf("ShippingCost(%v, %d, %v): неожиданная ошибка %v", tt.weight, tt.distance, tt.express, err)
			}
			if got != tt.want {
				t.Errorf("ShippingCost(%v, %d, %v) = %d, а ожидалось %d", tt.weight, tt.distance, tt.express, got, tt.want)
			}
		})
	}
}

// TODO: отдельный тест на ошибки — проверяй их через errors.Is.
