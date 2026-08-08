# Python Template - DDD + Clean Architecture

## Структура проекта
```
src/
├── domain/           # Domain layer (entities, value objects)
├── application/      # Application layer (use cases, ports)
├── infrastructure/   # Infrastructure layer (реализации портов)
└── interface/        # Interface layer (controllers, DTOs)

tests/
├── unit/            # Unit tests (100% покрытие)
├── integration/     # Integration tests (100% покрытие)
├── e2e/            # E2E tests (100% покрытие)
└── mutation/       # Mutation tests (≥2 на функцию)
```

## Требования
- Python 3.9+
- uv для управления зависимостями
- 100% покрытие тестами (unit, integration, e2e)
- 2 мутационных теста на каждую функцию
- CNC ≤ 10

## Установка
```bash
uv sync
```

## Запуск тестов
```bash
# Все тесты с покрытием 100%
pytest --cov=src --cov-fail-under=100

# Только unit
pytest tests/unit --cov=src

# Только integration
pytest tests/integration

# Только e2e
pytest tests/e2e

# Мутационные тесты
python ../../scripts/testing/mutation_runner.py --generate-report
```

## Проверка качества
```bash
# Форматирование
black src tests
isort src tests

# Линтинг
flake8 src tests
mypy src

# Сложность (CNC ≤ 10)
lizard -l 10 src
```

## Best Practices

### Domain Layer
- ✅ Сущности не зависят от фреймворков
- ✅ Value Objects неизменяемы (frozen=True)
- ✅ Domain Services содержат бизнес-логику

### Application Layer  
- ✅ Use Cases координируют поток данных
- ✅ Ports определяют контракты
- ✅ Нет зависимостей от инфраструктуры

### Infrastructure Layer
- ✅ Реализует порты
- ✅ Содержит работу с БД, внешними API

### Testing
- ✅ TDD: красный → зеленый → рефакторинг
- ✅ ARRANGE → ACT → ASSERT
- ✅ ≥2 мутаций на функцию
