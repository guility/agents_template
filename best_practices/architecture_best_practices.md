# Лучшие практики архитектуры

## 📖 Для кого
Этот документ должны изучить:
- **Design Architect** (обязательно)
- **Enterprise Architect** (обязательно)
- **Developer** (рекомендуется)
- **Orchestrator** (обязательно)

## 🎯 Принципы чистой архитектуры

### 1. Слои архитектуры

```
┌─────────────────────────────────────────┐
│           Interface Layer                │  ← Контроллеры, DTO, Presenters
│         (зависит от Application)         │
├─────────────────────────────────────────┤
│          Application Layer               │  ← Use Cases, Ports (интерфейсы)
│        (зависит от Domain)               │
├─────────────────────────────────────────┤
│            Domain Layer                  │  ← Сущности, Value Objects, Services
│         (НЕ ЗАВИСИТ НИ ОТ ЧЕГО)          │
└─────────────────────────────────────────┘
           ↑ зависит от ↓
┌─────────────────────────────────────────┐
│       Infrastructure Layer               │  ← Реализация портов, БД, External APIs
│    (реализует интерфейсы Application)    │
└─────────────────────────────────────────┘
```

#### Правила зависимостей
- ✅ Domain → ни от чего не зависит
- ✅ Application → зависит только от Domain
- ✅ Infrastructure → зависит от Application и Domain
- ✅ Interface → зависит от Application
- ❌ Domain → НЕ должен зависеть от Infrastructure
- ❌ Application → НЕ должен зависеть от Infrastructure напрямую

### 2. DDD Паттерны

#### Сущности (Entities)
```python
# ✅ Хорошо - сущность с идентичностью
class User(Entity):
    def __init__(self, id: UserId, email: Email, name: Name):
        self.id = id  # Идентичность
        self.email = email
        self.name = name
    
    def change_email(self, new_email: Email):
        # Бизнес-логика + валидация внутри сущности
        if not self._is_email_unique(new_email):
            raise DomainException("Email already exists")
        self.email = new_email
        self.add_domain_event(UserEmailChanged(self.id, new_email))
```

#### Value Objects
```python
# ✅ Хорошо - неизменяемый объект-значение
@dataclass(frozen=True)
class Email:
    value: str
    
    def __post_init__(self):
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', self.value):
            raise ValueError("Invalid email")
    
    def __str__(self):
        return self.value
```

#### Агрегаты
```python
# ✅ Хорошо - агрегат с корнем
class Order(AggregateRoot):
    def __init__(self, id: OrderId, customer_id: CustomerId):
        super().__init__(id)
        self.customer_id = customer_id
        self.items: List[OrderItem] = []
        self.status = OrderStatus.DRAFT
    
    def add_item(self, product_id: ProductId, quantity: int):
        # Инварианты агрегата
        if self.status != OrderStatus.DRAFT:
            raise DomainException("Cannot modify completed order")
        
        item = OrderItem(product_id, quantity)
        self.items.append(item)
        self.recalculate_total()
```

#### Repository Pattern
```python
# ✅ Хорошо - интерфейс в domain layer
class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: UserId) -> Optional[User]:
        pass
    
    @abstractmethod
    def save(self, user: User) -> None:
        pass

# ✅ Хорошо - реализация в infrastructure
class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, user_id: UserId) -> Optional[User]:
        # SQLAlchemy implementation
        pass
```

### 3. Модульное проектирование

#### Критерии хорошего модуля
| Критерий | Описание | Метрика |
|----------|----------|---------|
| Независимость | Может разрабатываться отдельно | Нет циклических зависимостей |
| Параллелизм | Тесты можно писать параллельно | Четкие контракты |
| Связность | Высокая внутренняя связность | Cohesion > 0.7 |
| Слабая связанность | Минимум внешних зависимостей | Coupling < 5 |
| Явная ответственность | Одна четкая цель | Single Responsibility |

#### Пример разбивки на модули
```
src/
├── user_management/      # Управление пользователями
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── interface/
├── authentication/       # Аутентификация и авторизация
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── interface/
├── order_processing/     # Обработка заказов
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── interface/
└── notifications/        # Уведомления
    ├── domain/
    ├── application/
    ├── infrastructure/
    └── interface/
```

### 4. Контракты API

#### OpenAPI спецификация
```yaml
# contracts/user_api.yaml
openapi: 3.0.0
info:
  title: User Management API
  version: 1.0.0

paths:
  /users/{userId}:
    get:
      summary: Get user by ID
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
```

#### Внутренние интерфейсы (Python)
```python
# application/ports/user_service.py
from typing import Protocol, Optional
from domain.entities.user import User
from domain.value_objects.user_id import UserId

class UserServicePort(Protocol):
    """Порт для сервиса пользователей"""
    
    def get_user(self, user_id: UserId) -> Optional[User]:
        """Получить пользователя по ID"""
        ...
    
    def create_user(self, email: str, name: str) -> User:
        """Создать нового пользователя"""
        ...
```

### 5. Архитектурные решения (ADR)

#### Шаблон ADR
```markdown
# ADR-{N}: {Название решения}

## Статус
{proposed | accepted | rejected | deprecated | superseded}

## Контекст
Описание проблемы и контекста принятия решения.

## Решение
Подробное описание принятого решения.

## Последствия
### Положительные
- Список преимуществ

### Отрицательные
- Список trade-offs

### Риски
- Потенциальные риски

## Альтернативы
Рассмотренные альтернативы и почему они были отклонены.

## Ссылки
- Ссылки на связанные документы
```

### 6. Глобальные архитектурные принципы

### Принципы Enterprise Architect
1. **Согласованность**: Новые решения не должны противоречить предыдущим
2. **Документирование**: Все значимые решения фиксируются в ADR
3. **Прозрачность**: Противоречия явно документируются в Release Notes
4. **Эволюционность**: Архитектура развивается постепенно
5. **Стандартизация**: Единый стек технологий для подобных задач

### 7. Проверка качества архитектуры

#### Чеклист перед отправкой на ревью
- [ ] Слои архитектуры соблюдены
- [ ] Нет циклических зависимостей между модулями
- [ ] Каждый модуль независим (можно разрабатывать параллельно)
- [ ] Контракты API определены
- [ ] Доменная модель согласована с требованиями
- [ ] ADR задокументированы для ключевых решений
- [ ] Внешние интеграции явно определены
- [ ] План параллельной разработки составлен

#### Метрики
| Метрика | Порог | Инструмент |
|---------|-------|------------|
| Cyclomatic Complexity | ≤ 10 | lizard |
| Module Dependencies | ≤ 5 | custom script |
| Inheritance Depth | ≤ 3 | lizard |
| Layer Violations | 0 | architecture tests |

## 🔧 Инструменты

### Визуализация
- PlantUML / Mermaid для диаграмм
- Structurizr для C4 моделей
- Graphviz для графов зависимостей

### Валидация
```bash
# Проверка зависимостей модулей
./scripts/common/check_module_deps.sh

# Проверка противоречий ADR
./scripts/common/check_adr_conflicts.sh

# Анализ сложности
lizard -C 10 src/
```

## 📚 Дополнительные ресурсы
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/books/clean-architecture.html)
- [Domain-Driven Design by Eric Evans](https://domainlanguage.com/ddd/)
- [Implementing Domain-Driven Design by Vaughn Vernon](https://www.amazon.com/Implementing-Domain-Driven-Design-Vaughn-Vernon/dp/0321834577)
