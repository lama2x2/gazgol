// Урок 12.1 — Git, Linux, Docker, CI.
//
// Здесь пишешь не Go-код, а конфигурацию: Dockerfile, compose.yaml и CI-workflow.
// Тесты работают как линтер и проверяют лучшие практики из конспекта.
// Сервис, для которого всё это пишется: Go-модуль, main-пакет в ./cmd/api, слушает порт 8080.
//
// Проверка: go test ./course/lesson121/
package lesson121

// Задачи 1–2. Dockerfile для сервиса.
const Dockerfile = `
# TODO: напиши Dockerfile
`

// Задача 3. compose.yaml: сервис api (собирается из Dockerfile) и база PostgreSQL.
// Отступы — пробелами, как в любом YAML.
const Compose = `
# TODO: напиши compose.yaml
`

// Задача 4. GitHub Actions: .github/workflows/ci.yml
const CI = `
# TODO: напиши workflow
`
