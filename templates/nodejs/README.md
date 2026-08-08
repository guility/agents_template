# DDD Node.js/TypeScript Template

Шаблон Node.js проекта с архитектурой DDD и чистой архитектурой.

## Структура

```
nodejs/
├── src/
│   ├── domain/          # Сущности, Value Objects
│   ├── application/     # Use Cases, Ports
│   ├── infrastructure/  # Реализация портов
│   └── interface/       # Controllers, DTOs
├── tests/
│   ├── unit/            # Unit тесты
│   ├── integration/     # Integration тесты
│   ├── e2e/             # E2E тесты
│   └── mutation/        # Мутационные тесты
├── package.json
├── tsconfig.json
└── jest.config.js
```

## Быстрый старт

```bash
# Установка зависимостей
pnpm install

# Запуск тестов
pnpm test

# Форматирование
pnpm format

# Линтинг
pnpm lint

# Сборка
pnpm build
```

## Требования

- Node.js >= 18
- pnpm >= 8

## Тестирование

- 100% покрытие unit/integration/e2e
- 2 мутационных теста на каждую функцию
