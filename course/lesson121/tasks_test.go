package lesson121

import (
	"regexp"
	"strings"
	"testing"
)

type instr struct {
	cmd  string // FROM, COPY, RUN...
	args string
}

// parseDockerfile разбирает Dockerfile на инструкции: без комментариев, со склейкой строк через \.
func parseDockerfile(src string) []instr {
	var out []instr
	var cur string
	for _, line := range strings.Split(src, "\n") {
		t := strings.TrimSpace(line)
		if t == "" || strings.HasPrefix(t, "#") {
			continue
		}
		if strings.HasSuffix(t, "\\") {
			cur += strings.TrimSuffix(t, "\\") + " "
			continue
		}
		t = cur + t
		cur = ""
		cmd, args, _ := strings.Cut(t, " ")
		out = append(out, instr{strings.ToUpper(cmd), strings.TrimSpace(args)})
	}
	return out
}

func stages(ins []instr) [][]instr {
	var st [][]instr
	for _, in := range ins {
		if in.cmd == "FROM" {
			st = append(st, nil)
		}
		if len(st) > 0 {
			st[len(st)-1] = append(st[len(st)-1], in)
		}
	}
	return st
}

func TestDockerfileMultiStage(t *testing.T) {
	st := stages(parseDockerfile(Dockerfile))
	if len(st) < 2 {
		t.Fatalf("стадий (FROM) %d, а нужно хотя бы 2: сборка и итоговый образ", len(st))
	}
	first := strings.Fields(st[0][0].args)
	if len(first) < 3 || !strings.HasPrefix(first[0], "golang") || !strings.EqualFold(first[1], "AS") {
		t.Errorf("первая стадия должна быть вида «FROM golang:<версия> AS build», а она %q", st[0][0].args)
	}
	last := st[len(st)-1]
	img := strings.Fields(last[0].args)[0]
	if strings.HasPrefix(img, "golang") {
		t.Errorf("итоговая стадия на образе %s — в ней не должно быть компилятора Go", img)
	}
	hasFrom := false
	for _, in := range last {
		if in.cmd == "COPY" && strings.Contains(in.args, "--from=") {
			hasFrom = true
		}
	}
	if !hasFrom {
		t.Error("в итоговой стадии бинарник нужно скопировать из стадии сборки: COPY --from=build ...")
	}
}

func TestDockerfileBestPractices(t *testing.T) {
	ins := parseDockerfile(Dockerfile)
	st := stages(ins)
	if len(st) < 2 {
		t.Fatal("сначала сделай multi-stage сборку (задача 1)")
	}
	idx := func(pred func(instr) bool) int {
		for i, in := range st[0] {
			if pred(in) {
				return i
			}
		}
		return -1
	}
	modCopy := idx(func(in instr) bool { return in.cmd == "COPY" && strings.Contains(in.args, "go.mod") })
	download := idx(func(in instr) bool { return in.cmd == "RUN" && strings.Contains(in.args, "go mod download") })
	allCopy := idx(func(in instr) bool {
		f := strings.Fields(in.args)
		return in.cmd == "COPY" && len(f) == 2 && f[0] == "."
	})
	if modCopy < 0 || download < 0 || allCopy < 0 || !(modCopy < download && download < allCopy) {
		t.Error("для кэша слоёв порядок такой: COPY go.mod go.sum ./ → RUN go mod download → COPY . .")
	}
	cgo := false
	for _, in := range st[0] {
		if (in.cmd == "RUN" || in.cmd == "ENV" || in.cmd == "ARG") && strings.Contains(in.args, "CGO_ENABLED=0") {
			cgo = true
		}
	}
	if !cgo {
		t.Error("собирай статический бинарник: CGO_ENABLED=0 go build ...")
	}
	for _, in := range ins {
		if strings.Contains(in.args, " #") && in.cmd != "RUN" {
			t.Errorf("%s %s: комментарий в конце строки — в Dockerfile так нельзя, # станет частью аргументов. Пиши комментарии отдельной строкой", in.cmd, in.args)
		}
	}
	last := st[len(st)-1]
	user, entry := "", ""
	for _, in := range last {
		switch in.cmd {
		case "USER":
			user = in.args
		case "ENTRYPOINT", "CMD":
			entry = in.args
		}
	}
	if user == "" || user == "root" || user == "0" || strings.HasPrefix(user, "root:") || strings.HasPrefix(user, "0:") {
		t.Errorf("в итоговой стадии нужен USER с не-root пользователем, а сейчас %q", user)
	}
	if !strings.HasPrefix(entry, "[") {
		t.Errorf("ENTRYPOINT/CMD в shell-форме (%q) — PID 1 будет /bin/sh, и SIGTERM не дойдёт до приложения. Нужна exec-форма: [\"/app\"]", entry)
	}
}

// services разбирает compose.yaml грубо: имя сервиса → его текст.
func services(src string) map[string]string {
	res := map[string]string{}
	lines := strings.Split(src, "\n")
	in := false
	cur := ""
	head := regexp.MustCompile(`^  ([A-Za-z0-9_-]+):\s*$`)
	for _, l := range lines {
		if strings.HasPrefix(l, "services:") {
			in = true
			continue
		}
		if in && l != "" && !strings.HasPrefix(l, " ") && !strings.HasPrefix(l, "#") {
			in = false
		}
		if !in {
			continue
		}
		if m := head.FindStringSubmatch(l); m != nil {
			cur = m[1]
			continue
		}
		if cur != "" {
			res[cur] += l + "\n"
		}
	}
	return res
}

func TestCompose(t *testing.T) {
	svcs := services(Compose)
	db := ""
	for name, body := range svcs {
		if regexp.MustCompile(`image:\s*["']?postgres`).MatchString(body) {
			db = name
		}
	}
	if db == "" {
		t.Fatalf("не нашёл сервис с image: postgres... среди %d сервисов (сервисы — ключи под services: с отступом в 2 пробела)", len(svcs))
	}
	if !strings.Contains(svcs[db], "healthcheck:") {
		t.Errorf("у сервиса %s нет healthcheck — без него api не узнает, что база готова", db)
	}
	if !strings.Contains(svcs[db], "volumes:") {
		t.Errorf("у сервиса %s нет volumes — данные пропадут при пересоздании контейнера", db)
	}
	api := ""
	for name, body := range svcs {
		if name != db && strings.Contains(body, "DATABASE_URL") {
			api = name
		}
	}
	if api == "" {
		t.Fatal("не нашёл сервис приложения с переменной DATABASE_URL")
	}
	body := svcs[api]
	if !strings.Contains(body, "service_healthy") {
		t.Errorf("сервис %s должен ждать базу: depends_on → %s → condition: service_healthy", api, db)
	}
	url := regexp.MustCompile(`DATABASE_URL[=:]\s*["']?(\S+)`).FindStringSubmatch(body)
	if url == nil || strings.Contains(url[1], "localhost") || strings.Contains(url[1], "127.0.0.1") || !strings.Contains(url[1], "@"+db) {
		t.Errorf("DATABASE_URL должен указывать на хост %q (имя сервиса), а не localhost; сейчас: %v", db, url)
	}
	if !strings.Contains(body, "build:") {
		t.Errorf("сервис %s должен собираться из Dockerfile: build: .", api)
	}
}

func TestCI(t *testing.T) {
	need := []struct{ re, msg string }{
		{`(?m)^\s*push:|on:\s*\[.*push`, "триггер push"},
		{`pull_request`, "триггер pull_request"},
		{`actions/checkout@`, "шаг actions/checkout"},
		{`actions/setup-go@`, "шаг actions/setup-go"},
		{`go vet \./\.\.\.`, "шаг go vet ./..."},
		{`go test[^\n]*-race[^\n]*\./\.\.\.|go test[^\n]*\./\.\.\.[^\n]*-race`, "шаг go test -race ./..."},
	}
	for _, n := range need {
		if !regexp.MustCompile(n.re).MatchString(CI) {
			t.Errorf("в workflow нет: %s", n.msg)
		}
	}
}
