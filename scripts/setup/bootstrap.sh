#!/bin/bash
# bootstrap.sh - Скрипт инициализации проекта и установки pre-commit хуков

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Установка pre-commit хуков
install_git_hooks() {
    log_step "Installing Git hooks..."
    
    if [ ! -d "$SCRIPT_DIR/.git" ]; then
        log_warn "Not a git repository, skipping hook installation"
        return 0
    fi
    
    # Создание директории hooks если не существует
    mkdir -p "$SCRIPT_DIR/.git/hooks"
    
    # Копирование pre-commit хука
    if [ -f "$SCRIPT_DIR/scripts/hooks/pre-commit.sh" ]; then
        cp "$SCRIPT_DIR/scripts/hooks/pre-commit.sh" "$SCRIPT_DIR/.git/hooks/pre-commit"
        chmod +x "$SCRIPT_DIR/.git/hooks/pre-commit"
        log_info "pre-commit hook installed"
    else
        log_warn "pre-commit.sh not found"
    fi
    
    # Создание symlink для удобства
    if [ -d "$SCRIPT_DIR/.git/hooks" ]; then
        ln -sf "../../scripts/hooks/pre-commit.sh" "$SCRIPT_DIR/.git/hooks/pre-commit-local" 2>/dev/null || true
    fi
}

# Установка глобальных зависимостей
install_global_tools() {
    log_step "Installing global development tools..."
    
    # Python инструменты
    if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
        log_info "Installing Python tools..."
        pip install -q black isort flake8 pylint pytest pytest-cov lizard-linter semgrep pip-audit || true
    fi
    
    # Node.js инструменты (если есть npm)
    if command -v npm &> /dev/null; then
        log_info "Installing Node.js tools..."
        npm install -g prettier eslint typescript ts-node 2>/dev/null || true
    fi
    
    # Rust инструменты
    if command -v cargo &> /dev/null; then
        log_info "Installing Rust tools..."
        cargo install cargo-audit cargo-deny cargo-mutants 2>/dev/null || true
    fi
    
    # Go инструменты
    if command -v go &> /dev/null; then
        log_info "Installing Go tools..."
        go install golang.org/x/tools/cmd/goimports@latest 2>/dev/null || true
        go install honnef.co/go/tools/cmd/staticcheck@latest 2>/dev/null || true
    fi
    
    # Shell инструменты
    if command -v brew &> /dev/null; then
        brew install shellcheck shfmt 2>/dev/null || true
    elif command -v apt-get &> /dev/null; then
        apt-get install -y shellcheck 2>/dev/null || true
    fi
}

# Инициализация Python проекта с uv
init_python() {
    if [ -f "$SCRIPT_DIR/pyproject.toml" ] || [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        log_step "Initializing Python project..."
        
        if command -v uv &> /dev/null; then
            cd "$SCRIPT_DIR"
            uv sync --all-extras
            log_info "Python project initialized with uv"
        else
            log_warn "uv not found, please install: curl -LsSf https://astral.sh/uv/install.sh | sh"
        fi
    fi
}

# Инициализация Node.js проекта
init_nodejs() {
    if [ -f "$SCRIPT_DIR/package.json" ]; then
        log_step "Initializing Node.js project..."
        
        cd "$SCRIPT_DIR"
        
        if [ -f "$SCRIPT_DIR/pnpm-lock.yaml" ]; then
            pnpm install --frozen-lockfile
            log_info "Node.js project initialized with pnpm"
        elif [ -f "$SCRIPT_DIR/yarn.lock" ]; then
            yarn install --frozen-lockfile
            log_info "Node.js project initialized with yarn"
        else
            npm ci
            log_info "Node.js project initialized with npm"
        fi
    fi
}

# Инициализация Rust проекта
init_rust() {
    if [ -f "$SCRIPT_DIR/Cargo.toml" ]; then
        log_step "Initializing Rust project..."
        cd "$SCRIPT_DIR"
        cargo fetch
        log_info "Rust project initialized"
    fi
}

# Инициализация Go проекта
init_go() {
    if [ -f "$SCRIPT_DIR/go.mod" ]; then
        log_step "Initializing Go project..."
        cd "$SCRIPT_DIR"
        go mod download
        log_info "Go project initialized"
    fi
}

# Инициализация C# проекта
init_csharp() {
    if [ -n "$(find "$SCRIPT_DIR" -name '*.csproj' | head -1)" ]; then
        log_step "Initializing C# project..."
        cd "$SCRIPT_DIR"
        dotnet restore
        log_info "C# project initialized"
    fi
}

# Проверка CI платформы
detect_ci_platform() {
    log_step "Detecting CI platform..."
    
    if [ -d "$SCRIPT_DIR/.github/workflows" ]; then
        log_info "GitHub Actions detected"
        echo "github" > "$SCRIPT_DIR/.ci-platform"
    elif [ -d "$SCRIPT_DIR/.gitlab/ci" ]; then
        log_info "GitLab CI detected"
        echo "gitlab" > "$SCRIPT_DIR/.ci-platform"
    else
        log_warn "No CI platform configuration found"
    fi
}

# Создание структуры проекта (если пустая)
create_project_structure() {
    if [ ! -d "$SCRIPT_DIR/src" ]; then
        log_step "Creating project structure..."
        
        mkdir -p "$SCRIPT_DIR/src/domain"
        mkdir -p "$SCRIPT_DIR/src/application"
        mkdir -p "$SCRIPT_DIR/src/infrastructure"
        mkdir -p "$SCRIPT_DIR/src/interface"
        mkdir -p "$SCRIPT_DIR/tests/unit"
        mkdir -p "$SCRIPT_DIR/tests/integration"
        mkdir -p "$SCRIPT_DIR/tests/e2e"
        mkdir -p "$SCRIPT_DIR/contracts"
        mkdir -p "$SCRIPT_DIR/docs"
        
        # Создание .gitkeep файлов
        find "$SCRIPT_DIR/src" "$SCRIPT_DIR/tests" "$SCRIPT_DIR/contracts" "$SCRIPT_DIR/docs" \
            -type d -exec touch {}/.gitkeep \;
        
        log_info "Project structure created"
    fi
}

# Генерация README
generate_readme() {
    if [ ! -f "$SCRIPT_DIR/README.md" ]; then
        log_step "Generating README.md..."
        
        cat > "$SCRIPT_DIR/README.md" << 'EOF'
# Project Template

Шаблон проекта с поддержкой DDD, чистой архитектуры и адаптивного CI/CD.

## Структура проекта

```
project/
├── src/
│   ├── domain/          # Domain слой (сущности, value objects)
│   ├── application/     # Application слой (use cases, ports)
│   ├── infrastructure/  # Infrastructure слой (реализация портов)
│   └── interface/       # Interface слой (controllers, DTOs)
├── tests/
│   ├── unit/            # Unit тесты
│   ├── integration/     # Integration тесты
│   └── e2e/             # E2E тесты
├── contracts/           # OpenAPI/Protobuf спецификации
├── scripts/             # Скрипты автоматизации
└── docs/                # Документация
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
EOF
        
        log_info "README.md generated"
    fi
}

# Основная функция
main() {
    log_info "Starting project bootstrap..."
    
    detect_ci_platform
    install_git_hooks
    install_global_tools
    init_python
    init_nodejs
    init_rust
    init_go
    init_csharp
    create_project_structure
    generate_readme
    
    log_info "Bootstrap completed successfully!"
    log_info ""
    log_info "Next steps:"
    log_info "1. Review AGENTS.md for development guidelines"
    log_info "2. Start developing in src/domain/"
    log_info "3. Write tests in tests/"
    log_info "4. Commit with automatic pre-commit checks"
}

main "$@"
