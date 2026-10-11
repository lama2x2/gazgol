// Lyceum — локальная проверяющая система курса.
//
// Отдаёт конспект и позволяет решать домашки прямо на странице:
// код сохраняется в course/lessonXX/tasks.go и проверяется теми же тестами,
// что и ./course/check.sh.
//
//	go run ./course/cmd/lyceum
//	→ http://localhost:4001
package main

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"flag"
	"go/format"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
	"sync"
	"time"
)

// Номер урока: модуль (1–18) + номер урока в модуле: 11, 12 … 62, 71 … 182.
var lessonRe = regexp.MustCompile(`^([1-9]|1[0-8])[1-9]$`)

// Страницы конспекта по частям курса.
var pages = map[string]string{
	"/":      "konspekt.html",
	"/part2": "part2.html",
	"/part3": "part3.html",
}

type server struct {
	courseDir string
	mu        sync.Mutex // одна проверка за раз: тесты 6.x и так грузят процессор
}

func main() {
	addr := flag.String("addr", "127.0.0.1:4001", "адрес сервера")
	dir := flag.String("course", "course", "путь к папке курса")
	flag.Parse()

	abs, err := filepath.Abs(*dir)
	if err != nil {
		log.Fatal(err)
	}
	if _, err := os.Stat(filepath.Join(abs, "konspekt.html")); err != nil {
		log.Fatalf("не нашёл %s/konspekt.html — запускай из корня репозитория: go run ./course/cmd/lyceum", abs)
	}
	s := &server{courseDir: abs}

	mux := http.NewServeMux()
	for path, file := range pages {
		pattern := "GET " + path
		if path == "/" {
			pattern = "GET /{$}"
		}
		mux.HandleFunc(pattern, s.page(file))
	}
	mux.HandleFunc("GET /api/ping", func(w http.ResponseWriter, r *http.Request) { w.Write([]byte("ok")) })
	mux.HandleFunc("GET /api/lessons/{n}/code", s.readCode)
	mux.HandleFunc("PUT /api/lessons/{n}/code", s.writeCode)
	mux.HandleFunc("POST /api/lessons/{n}/check", s.check)

	log.Printf("конспект с редактором: http://localhost%s", (*addr)[strings.LastIndex(*addr, ":"):])
	log.Fatal(http.ListenAndServe(*addr, localOnly(mux)))
}

// localOnly пускает только запросы, адресованные localhost.
// Защита от DNS rebinding: чужой сайт не сможет писать файлы через этот сервер.
func localOnly(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		host, _, err := net.SplitHostPort(r.Host)
		if err != nil {
			host = r.Host
		}
		if host != "localhost" && host != "127.0.0.1" {
			http.Error(w, "только localhost", http.StatusForbidden)
			return
		}
		next.ServeHTTP(w, r)
	})
}

// page отдаёт страницу конспекта. Файл-артефакт пишется без <html>/<head> —
// добавляем минимальный каркас.
func (s *server) page(file string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		s.servePage(w, file)
	}
}

func (s *server) servePage(w http.ResponseWriter, file string) {
	body, err := os.ReadFile(filepath.Join(s.courseDir, file))
	if err != nil {
		http.Error(w, "страница ещё не собрана: python3 course/tools/build.py", http.StatusNotFound)
		return
	}
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	w.Header().Set("Cache-Control", "no-store")
	io.WriteString(w, `<!doctype html><html lang="ru"><head><meta charset="utf-8">`+
		`<meta name="viewport" content="width=device-width, initial-scale=1"></head><body>`)
	w.Write(body)
	io.WriteString(w, `</body></html>`)
}

// tasksPath проверяет номер урока и возвращает путь к файлу, который правит ученик.
func (s *server) tasksPath(w http.ResponseWriter, r *http.Request) (string, bool) {
	n := r.PathValue("n")
	if !lessonRe.MatchString(n) {
		http.Error(w, "нет такого урока", http.StatusNotFound)
		return "", false
	}
	dir := filepath.Join(s.courseDir, "lesson"+n)
	// В уроках, где пишешь тесты ты (8.2), редактируется student_test.go.
	if _, err := os.Stat(filepath.Join(dir, "student_test.go")); err == nil {
		return filepath.Join(dir, "student_test.go"), true
	}
	return filepath.Join(dir, "tasks.go"), true
}

func (s *server) readCode(w http.ResponseWriter, r *http.Request) {
	path, ok := s.tasksPath(w, r)
	if !ok {
		return
	}
	code, err := os.ReadFile(path)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.Write(code)
}

// writeCode сохраняет код. Если он синтаксически верный — сначала форматирует его,
// как gofmt; отформатированный текст возвращается, чтобы редактор его показал.
func (s *server) writeCode(w http.ResponseWriter, r *http.Request) {
	path, ok := s.tasksPath(w, r)
	if !ok {
		return
	}
	code, err := io.ReadAll(http.MaxBytesReader(w, r.Body, 256<<10))
	if err != nil {
		http.Error(w, "слишком большой файл", http.StatusRequestEntityTooLarge)
		return
	}
	if formatted, err := format.Source(code); err == nil {
		code = formatted
	}
	if err := os.WriteFile(path, code, 0o644); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.Write(code)
}

type testResult struct {
	Name   string   `json:"name"`
	Pass   bool     `json:"pass"`
	Output []string `json:"output"`
}

type checkResult struct {
	BuildError string        `json:"build_error,omitempty"`
	Tests      []*testResult `json:"tests"`
}

// testEvent — строка вывода go test -json.
type testEvent struct {
	Action string
	Test   string
	Output string
}

func (s *server) check(w http.ResponseWriter, r *http.Request) {
	path, ok := s.tasksPath(w, r)
	if !ok {
		return
	}
	s.mu.Lock()
	defer s.mu.Unlock()

	args := []string{"test", "-json", "-count=1", "-timeout=60s"}
	if t, err := os.ReadFile(filepath.Join(filepath.Dir(path), "tasks_test.go")); err == nil && bytes.Contains(t, []byte("lyceum:race")) {
		args = append(args, "-race") // уроки про конкурентность: ловим гонки данных
	}
	ctx, cancel := context.WithTimeout(r.Context(), 90*time.Second)
	defer cancel()
	cmd := exec.CommandContext(ctx, "go", append(args, ".")...)
	cmd.Dir = filepath.Dir(path)
	out, runErr := cmd.CombinedOutput()

	res := checkResult{Tests: []*testResult{}}
	byName := map[string]*testResult{}
	var other []string // вывод сборки и всё, что не относится к конкретному тесту

	sc := bufio.NewScanner(bytes.NewReader(out))
	sc.Buffer(make([]byte, 1<<20), 1<<20)
	for sc.Scan() {
		var ev testEvent
		if err := json.Unmarshal(sc.Bytes(), &ev); err != nil {
			other = append(other, sc.Text())
			continue
		}
		top, _, _ := strings.Cut(ev.Test, "/")
		switch {
		case ev.Action == "build-output":
			other = append(other, strings.TrimRight(ev.Output, "\n"))
		case top == "":
			continue
		case ev.Action == "run" && byName[top] == nil:
			byName[top] = &testResult{Name: top}
			res.Tests = append(res.Tests, byName[top])
		case ev.Action == "output" && byName[top] != nil:
			line := strings.TrimRight(ev.Output, "\n")
			// Сообщения t.Errorf выглядят как "    tasks_test.go:20: …" (и продолжения с отступом).
			if strings.HasPrefix(line, "    ") && !strings.HasPrefix(strings.TrimSpace(line), "---") {
				byName[top].Output = append(byName[top].Output, strings.TrimSpace(line))
			}
		case ev.Action == "pass" && ev.Test == top && byName[top] != nil:
			byName[top].Pass = true
		}
	}

	switch {
	case errors.Is(ctx.Err(), context.DeadlineExceeded):
		res.BuildError = "Проверка не уложилась в 90 секунд — возможно, в коде бесконечный цикл или горутины ждут друг друга."
	case len(res.Tests) == 0:
		msg := strings.TrimSpace(strings.Join(other, "\n"))
		if msg == "" && runErr != nil {
			msg = runErr.Error()
		}
		res.BuildError = msg
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(res)
}
