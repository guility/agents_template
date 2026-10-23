# Project Template

Шаблон проекта с поддержкой DDD, чистой архитектуры и адаптивного CI/CD.

## Структура проекта

```
project/
├── src/
│   ├── core/
│   │   ├── domain/          # Domain слой (сущности, value objects)
│   │   ├── application/     # Application слой (use cases, ports)
│   │   ├── infrastructure/  # Infrastructure слой (реализация портов)
│   │   └── interface/       # Interface слой (controllers, DTOs)
│   └── tests/
│       ├── unit/            # Unit тесты
│       ├── integration/     # Integration тесты
│       ├── mutation/        # Mutation тесты
│       └── e2e/             # E2E тесты
├── deploy/                  # Dockerfiles и Compose-конфигурации
├── docs/
│   └── contracts/       # OpenAPI/Protobuf спецификации
├── scripts/             # Скрипты автоматизации
```

## Требования

- Python 3.9+ (с uv)
- Node.js 18+ (с pnpm)
- Rust (опционально)
- Go (опционально)
- .NET 8+ (опционально)

## Быстрый старт

### Установка зависимостей

```bash
./scripts/setup/bootstrap.sh
```

### Запуск тестов

```bash
./scripts/common/run-tests.sh
```

### Форматирование кода

```bash
./scripts/common/format-code.sh
```

### Pre-commit проверки

Хуки устанавливаются автоматически при запуске bootstrap.sh

## CI/CD

Шаблон поддерживает как GitHub Actions, так и GitLab CI автоматически.

### GitHub Actions

Конфигурация: `.github/workflows/ci-cd.yml`

### GitLab CI

Конфигурация: `.gitlab/ci/.gitlab-ci.yml`

## Безопасность

Автоматические проверки включают:
- gitleaks (секреты)
- trivy (уязвимости)
- semgrep (статический анализ)
- lizard (цикломатическая сложность)

## Тестирование

- 100% покрытие unit, integration, e2e тестами
- Мутационное тестирование (2 мутации на функцию)

## Лицензия

MIT
