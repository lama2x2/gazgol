package lesson82

// Проверяющая система урока 8.2. Не меняй этот файл.
//
// Каждый тест копирует твой student_test.go во временный модуль вместе
// с одной из реализаций ShippingCost и запускает go test:
//   - с правильной реализацией твои тесты должны пройти;
//   - с мутантом (реализацией с подложенным багом) хотя бы один тест должен упасть.

import (
	"context"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

// runStudentTests запускает student_test.go против реализации из implPath.
// Возвращает вывод go test -v и то, упал ли хотя бы один тест.
func runStudentTests(t *testing.T, implPath string) (out string, failed bool) {
	t.Helper()
	if os.Getenv("LYCEUM_META") != "" {
		t.Skip("вложенный запуск")
	}
	student, err := os.ReadFile("student_test.go")
	if err != nil {
		t.Fatalf("не нашёл student_test.go: %v", err)
	}
	impl, err := os.ReadFile(implPath)
	if err != nil {
		t.Fatalf("не нашёл реализацию %s: %v", implPath, err)
	}
	dir := t.TempDir()
	files := map[string][]byte{
		"go.mod":          []byte("module mutant\n\ngo 1.24\n"),
		"tasks.go":        impl,
		"student_test.go": student,
	}
	for name, data := range files {
		if err := os.WriteFile(filepath.Join(dir, name), data, 0o644); err != nil {
			t.Fatal(err)
		}
	}
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()
	cmd := exec.CommandContext(ctx, "go", "test", "-v", "-count=1", ".")
	cmd.Dir = dir
	cmd.Env = append(os.Environ(), "LYCEUM_META=1", "GOWORK=off", "GOFLAGS=-mod=mod")
	b, _ := cmd.CombinedOutput()
	out = string(b)
	if strings.Contains(out, "[build failed]") || strings.Contains(out, "[setup failed]") {
		t.Fatalf("твои тесты не компилируются:\n%s", out)
	}
	return out, strings.Contains(out, "--- FAIL")
}

func TestYourTestsPass(t *testing.T) {
	t.Parallel()
	out, failed := runStudentTests(t, "tasks.go")
	if failed {
		t.Errorf("на ПРАВИЛЬНОЙ реализации твои тесты падают — значит, в тестах ошибка в ожиданиях:\n%s", out)
	}
	if !strings.Contains(out, "--- PASS") {
		t.Error("не нашёл ни одного теста в student_test.go")
	}
}

func killMutant(t *testing.T, name, hint string) {
	t.Helper()
	t.Parallel()
	_, failed := runStudentTests(t, filepath.Join("testdata", "mutants", name+".go.txt"))
	if !failed {
		t.Errorf("мутант выжил: все твои тесты прошли на реализации с багом. Подсказка: %s", hint)
	}
}

func TestKillsFreeZoneBoundary(t *testing.T) {
	killMutant(t, "free_zone", "что происходит ровно на границе бесплатной зоны?")
}

func TestKillsHeavyBoundary(t *testing.T) {
	killMutant(t, "heavy_boundary", "посылка ровно 10 кг — тяжёлая или нет?")
}

func TestKillsExpressOrder(t *testing.T) {
	killMutant(t, "express_order", "а если посылка и тяжёлая, и экспресс одновременно?")
}

func TestKillsMaxWeight(t *testing.T) {
	killMutant(t, "max_weight", "можно ли отправить ровно 30 кг?")
}

func TestKillsZeroWeight(t *testing.T) {
	killMutant(t, "zero_weight", "что если вес равен нулю?")
}

func TestKillsNegativeDistance(t *testing.T) {
	killMutant(t, "negative_distance", "проверены ли все ошибки?")
}

func TestKillsExpressFree(t *testing.T) {
	killMutant(t, "express_free", "экспресс на короткое расстояние — бесплатно?")
}
