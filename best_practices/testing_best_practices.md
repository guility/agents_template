# Лучшие практики тестирования

## 📖 Для кого
Этот документ должны изучить:
- **QA Engineer** (обязательно)
- **Test Reviewer** (обязательно)
- **Developer** (обязательно)
- **Orchestrator** (рекомендуется)

## 🎯 Принципы тестирования

### 1. Пирамида тестирования

```
        /¯¯¯¯¯¯¯\
       /   E2E   \      ~10% - Полные бизнес-сценарии
      /-----------\
     / Integration \    ~20% - Взаимодействие компонентов
    /---------------\
   /      Unit       \  ~70% - Функции и методы
  /-------------------\
```

### 2. TDD Цикл (Red-Green-Refactor)

#### Шаг 1: RED - Написать failing test
```python
# ✅ Хорошо - тест на поведение
def test_user_repository_returns_user_by_id():
    # Arrange
    repo = InMemoryUserRepository()
    expected_user = User(id=UserId(123), email=Email("test@example.com"))
    repo.save(expected_user)
    
    # Act
    actual_user = repo.get_by_id(UserId(123))
    
    # Assert
    assert actual_user is not None
    assert actual_user.id == UserId(123)
    assert actual_user.email == Email("test@example.com")
```

#### Шаг 2: GREEN - Минимальная реализация
```python
class InMemoryUserRepository:
    def __init__(self):
        self._storage = {}
    
    def save(self, user: User) -> None:
        self._storage[user.id] = user
    
    def get_by_id(self, user_id: UserId) -> Optional[User]:
        return self._storage.get(user_id)
```

#### Шаг 3: REFACTOR - Оптимизация
```python
# Рефакторинг кода с сохранением зеленых тестов
```

### 3. Типы тестов

#### Unit Tests
**Цель:** Тестирование изолированных единиц кода

```python
# ✅ Хорошо - unit тест с моками
def test_order_calculates_total_correctly():
    # Arrange
    order = Order(order_id=OrderId(1))
    mock_pricing_service = Mock(spec=PricingService)
    mock_pricing_service.get_price.return_value = Money(100, "USD")
    
    # Act
    order.add_item(ProductId(1), quantity=2, pricing_service=mock_pricing_service)
    
    # Assert
    assert order.total == Money(200, "USD")
    mock_pricing_service.get_price.assert_called_once_with(ProductId(1))
```

**Правила:**
- ✅ Изолировать тестируемую единицу
- ✅ Мокировать все внешние зависимости
- ✅ Тестировать один аспект за раз
- ✅ Быстрое выполнение (< 10ms на тест)

#### Integration Tests
**Цель:** Тестирование взаимодействия между компонентами

```python
# ✅ Хорошо - integration тест с Testcontainers
@pytest.mark.integration
async def test_user_service_saves_to_database():
    # Arrange
    async with PostgresContainer() as db:
        service = UserService(db.connection_string)
        
        # Act
        user = await service.create_user("test@example.com", "John")
        
        # Assert
        saved_user = await service.get_user(user.id)
        assert saved_user.email == "test@example.com"
```

**Правила:**
- ✅ Использовать Testcontainers для изоляции
- ✅ Тестировать реальные взаимодействия
- ✅ Очищать состояние после теста
- ✅ Среднее время выполнения (< 100ms на тест)

#### E2E Tests
**Цель:** Тестирование полных бизнес-сценариев

```python
# ✅ Хорошо - e2e тест полного сценария
@pytest.mark.e2e
async def test_user_registration_flow():
    # Arrange
    client = TestClient(app)
    
    # Act & Assert - полный поток
    response = await client.post("/register", json={
        "email": "new@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 201
    
    # Проверка email
    email = await email_service.get_latest()
    assert "confirm" in email.body
    
    # Подтверждение
    token = extract_token(email.body)
    response = await client.post(f"/confirm/{token}")
    assert response.status_code == 200
    
    # Вход
    response = await client.post("/login", json={
        "email": "new@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

**Правила:**
- ✅ Тестировать полные пользовательские сценарии
- ✅ Использовать реальное приложение (или максимально близкое)
- ✅ Минимизировать количество e2e тестов (только критические пути)
- ✅ Время выполнения (< 5 сек на тест)

#### Behaviour Tests (BDD)
**Цель:** Тестирование на языке бизнеса

```gherkin
# features/user_registration.feature
Feature: User Registration
  As a new visitor
  I want to create an account
  So that I can access premium features

  Scenario: Successful registration with valid data
    Given I am on the registration page
    When I fill in email "test@example.com"
    And I fill in password "SecurePass123!"
    And I submit the form
    Then I should see a confirmation message
    And I should receive a confirmation email

  Scenario: Registration with invalid email
    Given I am on the registration page
    When I fill in email "invalid-email"
    And I fill in password "SecurePass123!"
    And I submit the form
    Then I should see an error message "Invalid email format"
    And I should not receive any email
```

**Правила:**
- ✅ Использовать язык бизнеса (Ubiquitous Language)
- ✅ Формат Given-When-Then
- ✅ Понятно не-техническим специалистам
- ✅ Один сценарий = одна бизнес-цель

#### Mutation Tests
**Цель:** Проверка качества тестов через внесение мутаций

**КРИТИЧЕСКИ ВАЖНО:** 2 мутации на каждую функцию/метод

```python
# Исходный код
def calculate_discount(price: float, discount_percent: int) -> float:
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Invalid discount")
    return price * (1 - discount_percent / 100)

# Мутация 1: Изменение условия
def calculate_discount_mutant1(price: float, discount_percent: int) -> float:
    if discount_percent <= 0 or discount_percent > 100:  # < изменено на <=
        raise ValueError("Invalid discount")
    return price * (1 - discount_percent / 100)

# Мутация 2: Удаление вызова
def calculate_discount_mutant2(price: float, discount_percent: int) -> float:
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Invalid discount")
    return price  # Удалено умножение на (1 - discount_percent / 100)
```

**Правила:**
- ✅ Минимум 2 мутации на функцию
- ✅ Разные типы мутаций (операторы, вызовы, граничные значения)
- ✅ Mutation Score ≥ 95%
- ✅ Все мутанты должны быть "убиты" тестами

### 4. Именование тестов

#### Форматы именования по языкам

**Python:**
```python
def test_{unit}_{scenario}_{expected_result}():
    pass

# Примеры
def test_user_repository_returns_none_for_unknown_id():
    pass

def test_order_add_item_raises_error_when_order_completed():
    pass
```

**JavaScript/TypeScript:**
```typescript
describe('UserService', () => {
  describe('createUser', () => {
    it('should create user with valid email', async () => {
      // ...
    });
    
    it('should throw error for duplicate email', async () => {
      // ...
    });
  });
});
```

**Go:**
```go
func TestUserService_CreateUser_ValidEmail(t *testing.T) {
    // ...
}

func TestOrder_AddItem_CompletedOrder_ReturnsError(t *testing.T) {
    // ...
}
```

**Rust:**
```rust
#[test]
fn test_user_repository_returns_none_for_unknown_id() {
    // ...
}

#[test]
fn test_order_add_item_raises_error_when_completed() {
    // ...
}
```

**C#:**
```csharp
[Theory]
[InlineData("valid@example.com")]
public async Task CreateUser_ValidEmail_CreatesUser(string email) {
    // ...
}

[Fact]
public void AddItem_CompletedOrder_ThrowsDomainException() {
    // ...
}
```

### 5. Arrange-Act-Assert Паттерн

```python
# ✅ Хорошо - четкое разделение AAA
def test_user_login_success():
    # Arrange
    user = User(id=UserId(1), email="test@example.com")
    repo = InMemoryUserRepository()
    repo.save(user)
    service = AuthService(repo, password_hasher)
    
    # Act
    result = service.login("test@example.com", "correct_password")
    
    # Assert
    assert result.is_success()
    assert result.user_id == UserId(1)
    assert result.token is not None
```

### 6. Пограничные случаи (Edge Cases)

Обязательно тестировать:
- ✅ Пустые входные данные
- ✅ Null/None значения
- ✅ Максимальные/минимальные значения
- ✅ Некорректные форматы
- ✅ Дубликаты
- ✅ Таймауты внешних сервисов
- ✅ Сетевые ошибки
- ✅ Конкурентный доступ

```python
# Пример тестирования edge cases
def test_parse_int_edge_cases():
    assert parse_int("") == 0
    assert parse_int(None) == 0
    assert parse_int("0") == 0
    assert parse_int("-1") == -1
    assert parse_int("999999999999") == 999999999999
    assert parse_int("abc") == 0  # Graceful degradation
    assert parse_int("  42  ") == 42  # Trimming
```

### 7. Изоляция тестов

```python
# ❌ Плохо - тесты зависят от порядка
class TestOrder:
    order = Order()  # Общее состояние
    
    def test_add_item_1(self):
        self.order.add_item(...)  # Изменяет общее состояние
    
    def test_add_item_2(self):
        # Зависит от предыдущего теста!
        assert len(self.order.items) == 2

# ✅ Хорошо - каждый тест независим
class TestOrder:
    def test_add_item_first(self):
        order = Order()  # Свежий экземпляр
        order.add_item(...)
        assert len(order.items) == 1
    
    def test_add_item_second(self):
        order = Order()  # Свежий экземпляр
        order.add_item(...)
        assert len(order.items) == 1
```

### 8. Чеклист качества тестов

Перед отправкой на ревью проверить:
- [ ] Unit тесты для всех функций
- [ ] Integration тесты для всех взаимодействий
- [ ] E2E тесты для критических сценариев
- [ ] BDD сценарии на языке бизнеса
- [ ] 2 мутационных теста на функцию
- [ ] Тесты изолированы и независимы
- [ ] Имена отражают поведение
- [ ] Покрыты edge cases
- [ ] Используется AAA паттерн
- [ ] Нет дублирования в тестах
- [ ] Моки используются корректно
- [ ] Стиль соответствует языку

## 🔧 Инструменты по языкам

### Python
- Unit: `pytest`, `unittest`
- Integration: `pytest + testcontainers`
- E2E: `playwright`, `selenium`
- BDD: `pytest-bdd`, `behave`
- Mutation: `mutmut`, `cosmic-ray`
- Coverage: `coverage.py`, `pytest-cov`

### JavaScript/TypeScript
- Unit: `Jest`, `Vitest`
- Integration: `supertest + testcontainers`
- E2E: `Playwright`, `Cypress`
- BDD: `Cucumber`, `Jest BDD`
- Mutation: `Stryker`
- Coverage: встроенная

### Rust
- Unit: встроенный `#[test]`
- Integration: `testcontainers-modules`
- E2E: `fantoccini`
- BDD: `cucumber-rust`
- Mutation: `cargo-mutants`
- Coverage: `cargo-tarpaulin`

### Go
- Unit: встроенный `testing`
- Integration: `testcontainers-go`
- E2E: `godog`
- BDD: `ginkgo`, `godog`
- Mutation: `gobugfree/mutgo`
- Coverage: встроенный

### C#
- Unit: `xUnit`, `NUnit`
- Integration: `testcontainers-dotnet`
- E2E: `SpecFlow`, `Playwright`
- BDD: `SpecFlow`
- Mutation: `Stryker.NET`
- Coverage: `coverlet`

## 📊 Метрики качества

| Метрика | Порог | Инструмент |
|---------|-------|------------|
| Line Coverage | 100% | coverage.py, Istanbul |
| Branch Coverage | 100% | coverage.py, Istanbul |
| Mutation Score | ≥ 95% | mutmut, Stryker |
| Flaky Tests | 0% | CI анализ |
| Test Duration | < 10 мин | CI тайминги |
