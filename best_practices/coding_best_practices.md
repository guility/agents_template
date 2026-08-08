# Лучшие практики написания кода

## 📖 Для кого
Этот документ должны изучить:
- **Developer** (обязательно)
- **Code Reviewer** (обязательно)
- **Design Architect** (рекомендуется)
- **Orchestrator** (рекомендуется)

## 🎯 Принципы качества кода

### 1. SOLID Принципы

#### S - Single Responsibility Principle
```python
# ❌ Плохо - несколько ответственностей
class UserService:
    def create_user(self, email, password):
        # Валидация
        # Хэширование пароля
        # Сохранение в БД
        # Отправка email
        pass

# ✅ Хорошо - разделение ответственностей
class UserValidator:
    def validate_email(self, email: str) -> bool:
        ...
    
    def validate_password(self, password: str) -> bool:
        ...

class PasswordHasher:
    def hash(self, password: str) -> str:
        ...

class UserRepository:
    def save(self, user: User) -> None:
        ...

class EmailService:
    def send_welcome(self, user: User) -> None:
        ...

class CreateUserUseCase:
    def execute(self, email: str, password: str) -> User:
        self.validator.validate_email(email)
        self.validator.validate_password(password)
        
        hashed = self.hasher.hash(password)
        user = User(email=email, password_hash=hashed)
        self.repo.save(user)
        self.email.send_welcome(user)
        
        return user
```

#### O - Open/Closed Principle
```python
# ❌ Плохо - закрыто для расширения
class PaymentProcessor:
    def process(self, payment_type: str, amount: float):
        if payment_type == "credit_card":
            # логика кредитной карты
        elif payment_type == "paypal":
            # логика PayPal
        elif payment_type == "crypto":
            # логика криптовалюты

# ✅ Хорошо - открыто для расширения
class PaymentStrategy(ABC):
    @abstractmethod
    def process(self, amount: float) -> None:
        pass

class CreditCardPayment(PaymentStrategy):
    def process(self, amount: float) -> None:
        ...

class PayPalPayment(PaymentStrategy):
    def process(self, amount: float) -> None:
        ...

class PaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy
    
    def process(self, amount: float) -> None:
        self.strategy.process(amount)
```

#### L - Liskov Substitution Principle
```python
# ❌ Плохо - нарушение LSP
class Rectangle:
    def set_width(self, width: float):
        self.width = width
    
    def set_height(self, height: float):
        self.height = height

class Square(Rectangle):
    def set_width(self, width: float):
        self.width = width
        self.height = width  # Нарушение инварианта!
    
    def set_height(self, height: float):
        self.height = height
        self.width = height  # Нарушение инварианта!

# ✅ Хорошо - правильное наследование
class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
    
    def area(self) -> float:
        return self.width * self.height

class Square(Shape):
    def __init__(self, side: float):
        self.side = side
    
    def area(self) -> float:
        return self.side ** 2
```

#### I - Interface Segregation Principle
```python
# ❌ Плохо - "жирный" интерфейс
class Worker(ABC):
    @abstractmethod
    def work(self):
        pass
    
    @abstractmethod
    def eat(self):
        pass
    
    @abstractmethod
    def sleep(self):
        pass

class Robot(Worker):
    def work(self):
        ...
    def eat(self):
        raise NotImplementedError()  # Нарушение ISP
    def sleep(self):
        raise NotImplementedError()  # Нарушение ISP

# ✅ Хорошо - сегрегированные интерфейсы
class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass

class Sleepable(ABC):
    @abstractmethod
    def sleep(self):
        pass

class HumanWorker(Workable, Eatable, Sleepable):
    def work(self): ...
    def eat(self): ...
    def sleep(self): ...

class RobotWorker(Workable):
    def work(self): ...
```

#### D - Dependency Inversion Principle
```python
# ❌ Плохо - зависимость от конкретики
class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # Конкретная реализация
    
    def get_user(self, user_id: int):
        return self.db.query(f"SELECT * FROM users WHERE id={user_id}")

# ✅ Хорошо - зависимость от абстракции
class Database(ABC):
    @abstractmethod
    def query(self, sql: str) -> List[Dict]:
        pass

class UserService:
    def __init__(self, db: Database):
        self.db = db  # Абстракция
    
    def get_user(self, user_id: int) -> User:
        results = self.db.query(f"SELECT * FROM users WHERE id={user_id}")
        return User.from_dict(results[0])
```

### 2. KISS и YAGNI

```python
# ❌ Плохо - избыточная сложность
class DataProcessor:
    def __init__(self):
        self.strategy_factory = AbstractFactory()
        self.observer_registry = ObserverRegistry()
        self.chain = ResponsibilityChain()
    
    def process(self, data):
        # 100 строк сложной логики с паттернами

# ✅ Хорошо - просто и понятно
class DataProcessor:
    def process(self, data):
        validated = self._validate(data)
        transformed = self._transform(validated)
        return self._save(transformed)
    
    def _validate(self, data):
        # простая валидация
        pass
    
    def _transform(self, data):
        # простая трансформация
        pass
    
    def _save(self, data):
        # простое сохранение
        pass
```

### 3. DRY (Don't Repeat Yourself)

```python
# ❌ Плохо - дублирование
def create_user(email, name):
    if not email or '@' not in email:
        raise ValueError("Invalid email")
    user = User(email=email, name=name)
    db.save(user)
    return user

def update_user(user_id, email, name):
    if not email or '@' not in email:
        raise ValueError("Invalid email")
    user = db.get(user_id)
    user.email = email
    user.name = name
    db.save(user)
    return user

# ✅ Хорошо - выделение общей логики
class EmailValidator:
    @staticmethod
    def validate(email: str) -> bool:
        if not email or '@' not in email:
            raise ValueError("Invalid email")
        return True

class UserService:
    def create_user(self, email: str, name: str) -> User:
        EmailValidator.validate(email)
        user = User(email=email, name=name)
        db.save(user)
        return user
    
    def update_user(self, user_id: int, email: str, name: str) -> User:
        EmailValidator.validate(email)
        user = db.get(user_id)
        user.email = email
        user.name = name
        db.save(user)
        return user
```

### 4. Именование

#### Правила именования
- ✅ Использовать доменный язык (Ubiquitous Language)
- ✅ Имена отражают намерение, а не реализацию
- ✅ Избегать сокращений (кроме общепринятых)
- ✅ Глаголы для методов, существительные для классов

```python
# ❌ Плохо
def proc(d):  # Что такое proc? Что такое d?
    res = d * 1.2
    return res

# ✅ Хорошо
def calculate_price_with_tax(base_price: float, tax_rate: float = 0.2) -> float:
    return base_price * (1 + tax_rate)

# ❌ Плохо
class_mgr = UserManager()

# ✅ Хорошо
user_repository = UserRepository()
user_service = UserService()
```

### 5. Обработка ошибок

```python
# ❌ Плохо - проглатывание исключений
def get_user(user_id: int):
    try:
        return db.query(f"SELECT * FROM users WHERE id={user_id}")
    except:
        pass  # Тихое игнорирование ошибки!

# ❌ Плохо - бесполезное сообщение
def get_user(user_id: int):
    try:
        return db.query(...)
    except Exception as e:
        raise Exception("Error occurred")  # Какое error?

# ✅ Хорошо - информативная обработка
class UserNotFoundException(Exception):
    def __init__(self, user_id: int):
        super().__init__(f"User with id {user_id} not found")
        self.user_id = user_id

def get_user(user_id: int) -> User:
    try:
        result = db.query("SELECT * FROM users WHERE id=?", user_id)
        if not result:
            raise UserNotFoundException(user_id)
        return User.from_dict(result)
    except DatabaseError as e:
        logger.error(f"Database error while fetching user {user_id}", exc_info=True)
        raise ServiceUnavailableException("Unable to fetch user") from e
```

### 6. Функции

#### Правила
- ✅ Длина ≤ 20 строк
- ✅ Параметры ≤ 4
- ✅ Одна ответственность
- ✅ Побочные эффекты явно обозначены

```python
# ❌ Плохо - слишком длинная функция
def process_order(order_data):
    # 50 строк кода...
    # валидация
    # расчет цены
    # проверка наличия
    # создание заказа
    # отправка уведомления
    # обновление склада
    # логирование
    pass

# ✅ Хорошо - разделение на подфункции
def process_order(order_data: OrderData) -> Order:
    validated_data = self._validate_order(order_data)
    total = self._calculate_total(validated_data)
    self._check_availability(validated_data)
    
    order = self._create_order(validated_data, total)
    self._send_notification(order)
    self._update_inventory(order)
    self._log_order(order)
    
    return order

def _validate_order(self, order_data: OrderData) -> ValidatedOrderData:
    # 5-10 строк валидации
    pass

def _calculate_total(self, data: ValidatedOrderData) -> Money:
    # 5-10 строк расчета
    pass
```

### 7. Комментарии и документация

```python
# ❌ Плохо - комментарий "что"
# Увеличиваем счетчик на 1
counter += 1

# ❌ Плохо - закомментированный код
# old_value = self.value
# self.value = new_value
self.value = new_value  # new implementation

# ✅ Хорошо - комментарий "почему"
# Используем экспоненциальную задержку для избежания thundering herd
delay = min(base_delay * (2 ** retry_count), max_delay)

# ✅ Хорошо - docstring
def calculate_compound_interest(
    principal: float,
    rate: float,
    time: int,
    compounds_per_year: int = 12
) -> float:
    """
    Рассчитывает сложный процент по формуле A = P(1 + r/n)^(nt)
    
    Args:
        principal: Начальная сумма (P)
        rate: Годовая процентная ставка (r) в десятичном формате
        time: Срок в годах (t)
        compounds_per_year: Количество начислений в год (n), по умолчанию 12
    
    Returns:
        Итоговая сумма с процентами (A)
    
    Raises:
        ValueError: Если rate < 0 или time < 0
    
    Example:
        >>> calculate_compound_interest(1000, 0.05, 10)
        1647.01
    """
    if rate < 0 or time < 0:
        raise ValueError("Rate and time must be non-negative")
    
    return principal * (1 + rate / compounds_per_year) ** (compounds_per_year * time)
```

### 8. Безопасность

```python
# ❌ Плохо - SQL инъекция
def get_user(username: str):
    query = f"SELECT * FROM users WHERE username='{username}'"
    return db.execute(query)

# ✅ Хорошо - параметризованный запрос
def get_user(username: str):
    query = "SELECT * FROM users WHERE username=?"
    return db.execute(query, [username])

# ❌ Плохо - хардкод секретов
API_KEY = "sk-1234567890abcdef"

# ✅ Хорошо - переменные окружения
import os
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ConfigurationError("API_KEY environment variable not set")

# ❌ Плохо - нет валидации входа
def transfer_funds(from_account, to_account, amount):
    accounts[to_account] += amount
    accounts[from_account] -= amount

# ✅ Хорошо - валидация и проверки
def transfer_funds(from_account: Account, to_account: Account, amount: Money):
    if amount <= Money(0, amount.currency):
        raise InvalidAmountException("Amount must be positive")
    
    if from_account.balance < amount:
        raise InsufficientFundsException("Insufficient funds")
    
    if from_account.owner != current_user:
        raise UnauthorizedException("Not authorized")
    
    # ... транзакция
```

### 9. Чеклист качества кода

Перед отправкой на ревью проверить:
- [ ] Код соответствует требованиям
- [ ] Архитектурные границы соблюдены
- [ ] SOLID принципы применены
- [ ] Функции ≤ 20 строк
- [ ] Параметры ≤ 4
- [ ] Цикломатическая сложность ≤ 10
- [ ] Нет дублирования (DRY)
- [ ] Имена отражают намерение
- [ ] Ошибки обрабатываются корректно
- [ ] Нет уязвимостей безопасности
- [ ] Документация обновлена
- [ ] Pre-commit хуки пройдены

## 🔧 Инструменты по языкам

### Python
- Форматирование: `black`, `isort`
- Линтинг: `ruff`, `flake8`, `mypy`
- Сложность: `lizard`, `radon`
- Безопасность: `bandit`, `safety`

### JavaScript/TypeScript
- Форматирование: `prettier`
- Линтинг: `eslint`, `tsc`
- Сложность: `lizard`, `complexity-checker`
- Безопасность: `npm audit`, `snyk`

### Rust
- Форматирование: `rustfmt`
- Линтинг: `clippy`
- Сложность: `lizard`
- Безопасность: `cargo-audit`

### Go
- Форматирование: `gofmt`, `goimports`
- Линтинг: `golangci-lint`
- Сложность: `lizard`, `gocyclo`
- Безопасность: `gosec`

### C#
- Форматирование: `dotnet format`
- Линтинг: `Roslyn Analyzers`
- Сложность: `lizard`, `SonarAnalyzer`
- Безопасность: `dotnet security`

## 📊 Метрики качества кода

| Метрика | Порог | Инструмент |
|---------|-------|------------|
| Cyclomatic Complexity | ≤ 10 | lizard |
| Function Length | ≤ 20 строк | lizard |
| Parameter Count | ≤ 4 | linting |
| Code Duplication | < 3% | dupli |
| Test Coverage | 100% | coverage tools |
| Linter Warnings | 0 | language-specific |
