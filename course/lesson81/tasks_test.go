package lesson81

import (
	"context"
	"errors"
	"fmt"
	"strings"
	"testing"
)

func fieldErrors(err error) []*FieldError {
	var out []*FieldError
	var walk func(error)
	walk = func(e error) {
		if e == nil {
			return
		}
		if fe, ok := e.(*FieldError); ok {
			out = append(out, fe)
			return
		}
		if m, ok := e.(interface{ Unwrap() []error }); ok {
			for _, x := range m.Unwrap() {
				walk(x)
			}
			return
		}
		walk(errors.Unwrap(e))
	}
	walk(err)
	return out
}

func TestValidateAd(t *testing.T) {
	if err := ValidateAd(Ad{Title: "Велосипед", Price: 5000, City: "Казань"}); err != nil {
		t.Fatalf("ValidateAd(корректное) = %v (%T), а ожидался nil", err, err)
	}
	if err := ValidateAd(Ad{Title: "Даром", Price: 0, City: "Уфа"}); err != nil {
		t.Errorf("цена 0 допустима, а ValidateAd вернул %v", err)
	}
	err := ValidateAd(Ad{Title: "", Price: -1, City: ""})
	fes := fieldErrors(err)
	fields := map[string]bool{}
	for _, fe := range fes {
		fields[fe.Field] = true
	}
	if len(fes) != 3 || !fields["title"] || !fields["price"] || !fields["city"] {
		t.Errorf("ValidateAd(всё плохо) нашёл поля %v, а ожидались title, price, city — все сразу через errors.Join", fields)
	}
	var fe *FieldError
	if !errors.As(err, &fe) {
		t.Error("errors.As(err, *FieldError) не нашёл ошибку поля")
	}
	long := strings.Repeat("я", 101)
	fes = fieldErrors(ValidateAd(Ad{Title: long, Price: 1, City: "Омск"}))
	if len(fes) != 1 || fes[0].Field != "title" {
		t.Errorf("название из 101 буквы: ожидалась одна ошибка поля title, а получено %v", fes)
	}
	if err := ValidateAd(Ad{Title: strings.Repeat("я", 100), Price: 1, City: "Омск"}); err != nil {
		t.Errorf("название ровно из 100 букв допустимо (это 200 байт, но 100 символов), а получено %v", err)
	}
}

func TestFindAd(t *testing.T) {
	ads := map[int]Ad{1: {Title: "Шкаф"}}
	if ad, err := FindAd(ads, 1); err != nil || ad.Title != "Шкаф" {
		t.Errorf("FindAd(1) = %v, %v", ad, err)
	}
	_, err := FindAd(ads, 42)
	if !errors.Is(err, ErrNotFound) {
		t.Errorf("FindAd(42): errors.Is(err, ErrNotFound) = false, err = %v", err)
	}
	if err == nil || !strings.Contains(err.Error(), "42") {
		t.Errorf("в тексте ошибки нет id: %v", err)
	}
	if err == ErrNotFound {
		t.Error("ошибку нужно обернуть с контекстом, а вернулся голый ErrNotFound")
	}
}

func TestStatusCode(t *testing.T) {
	timeout, cancel := context.WithTimeout(context.Background(), 0)
	defer cancel()
	<-timeout.Done()
	tests := []struct {
		err  error
		want int
	}{
		{nil, 200},
		{fmt.Errorf("get: %w", ErrNotFound), 404},
		{fmt.Errorf("a: %w", fmt.Errorf("b: %w", ErrForbidden)), 403},
		{fmt.Errorf("create: %w", &FieldError{"price", "<0"}), 422},
		{errors.Join(&FieldError{"title", "empty"}, &FieldError{"city", "empty"}), 422},
		{fmt.Errorf("query: %w", timeout.Err()), 504},
		{errors.New("connection refused"), 500},
	}
	for _, tt := range tests {
		if got := StatusCode(tt.err); got != tt.want {
			t.Errorf("StatusCode(%v) = %d, а ожидалось %d", tt.err, got, tt.want)
		}
	}
}

func TestRetry(t *testing.T) {
	calls := 0
	err := Retry(5, func() error {
		calls++
		if calls < 3 {
			return errors.New("timeout")
		}
		return nil
	})
	if err != nil || calls != 3 {
		t.Errorf("успех с 3-й попытки: err = %v, вызовов %d, а ожидалось nil и 3", err, calls)
	}

	calls = 0
	boom := errors.New("timeout")
	err = Retry(4, func() error { calls++; return boom })
	if calls != 4 || !errors.Is(err, boom) || !strings.Contains(err.Error(), "4") {
		t.Errorf("все попытки неудачны: вызовов %d, err = %v — ожидалось 4 вызова и обёрнутая последняя ошибка с числом попыток", calls, err)
	}

	calls = 0
	err = Retry(10, func() error { calls++; return fmt.Errorf("card declined: %w", ErrPermanent) })
	if calls != 1 || !errors.Is(err, ErrPermanent) {
		t.Errorf("постоянная ошибка: вызовов %d, err = %v — повторять нельзя", calls, err)
	}
}

func TestSafeGo(t *testing.T) {
	if err := SafeGo(func() {}); err != nil {
		t.Errorf("без паники SafeGo вернул %v", err)
	}
	defer func() {
		if r := recover(); r != nil {
			t.Fatalf("SafeGo пропустил панику наружу: %v", r)
		}
	}()
	err := SafeGo(func() { panic("всё сломалось") })
	if err == nil || !strings.Contains(err.Error(), "всё сломалось") || !strings.Contains(err.Error(), "panic") {
		t.Errorf("SafeGo(panic строкой) = %v, а ожидалось \"panic: всё сломалось\"", err)
	}
	err = SafeGo(func() { panic(ErrForbidden) })
	if !errors.Is(err, ErrForbidden) {
		t.Errorf("SafeGo(panic(ErrForbidden)): errors.Is не находит ErrForbidden в %v — оберни через %%w", err)
	}
	err = SafeGo(func() {
		var m map[string]int
		m["x"] = 1
	})
	if err == nil {
		t.Error("SafeGo не поймал панику записи в nil-map")
	}
}
