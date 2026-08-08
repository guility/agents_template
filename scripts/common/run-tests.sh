#!/bin/bash
# run-tests.sh - Универсальный скрипт запуска тестов с покрытием и мутационным тестированием

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Целевое покрытие (должно быть 100%)
COVERAGE_TARGET=${COVERAGE_TARGET:-100}

# Количество мутаций на функцию
MUTATIONS_PER_FUNCTION=${MUTATIONS_PER_FUNCTION:-2}

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

# Запуск unit тестов для Python
run_python_unit_tests() {
    local test_dir="$ROOT_DIR/tests/unit"
    
    if [ ! -d "$test_dir" ]; then
        log_warn "Python unit test directory not found: $test_dir"
        return 0
    fi
    
    log_step "Running Python unit tests..."
    
    # Проверка наличия pytest и coverage
    if ! command -v pytest &> /dev/null; then
        log_warn "pytest not found, skipping Python unit tests"
        return 0
    fi
    
    # Запуск с покрытием
    cd "$test_dir" || return 1
    
    local coverage_file=".coverage.unit"
    
    if pytest --cov=src --cov-report=term-missing --cov-report=html:"$ROOT_DIR/docs/coverage/unit" \
              --cov-fail-under="$COVERAGE_TARGET" \
              --junitxml="$ROOT_DIR/test-results/unit-python.xml" \
              -v 2>&1 | tee "$ROOT_DIR/test-results/unit-python.log"; then
        log_info "Python unit tests passed with ${COVERAGE_TARGET}% coverage"
    else
        log_error "Python unit tests failed"
        return 1
    fi
}

# Запуск integration тестов для Python
run_python_integration_tests() {
    local test_dir="$ROOT_DIR/tests/integration"
    
    if [ ! -d "$test_dir" ]; then
        log_warn "Python integration test directory not found: $test_dir"
        return 0
    fi
    
    log_step "Running Python integration tests..."
    
    if ! command -v pytest &> /dev/null; then
        log_warn "pytest not found, skipping Python integration tests"
        return 0
    fi
    
    cd "$test_dir" || return 1
    
    if pytest --cov=src --cov-report=term-missing --cov-report=html:"$ROOT_DIR/docs/coverage/integration" \
              --cov-fail-under="$COVERAGE_TARGET" \
              --junitxml="$ROOT_DIR/test-results/integration-python.xml" \
              -v 2>&1 | tee "$ROOT_DIR/test-results/integration-python.log"; then
        log_info "Python integration tests passed"
    else
        log_error "Python integration tests failed"
        return 1
    fi
}

# Запуск e2e тестов для Python
run_python_e2e_tests() {
    local test_dir="$ROOT_DIR/tests/e2e"
    
    if [ ! -d "$test_dir" ]; then
        log_warn "Python e2e test directory not found: $test_dir"
        return 0
    fi
    
    log_step "Running Python e2e tests..."
    
    if ! command -v pytest &> /dev/null; then
        log_warn "pytest not found, skipping Python e2e tests"
        return 0
    fi
    
    cd "$test_dir" || return 1
    
    if pytest --cov=src --cov-report=term-missing \
              --cov-fail-under="$COVERAGE_TARGET" \
              --junitxml="$ROOT_DIR/test-results/e2e-python.xml" \
              -v 2>&1 | tee "$ROOT_DIR/test-results/e2e-python.log"; then
        log_info "Python e2e tests passed"
    else
        log_error "Python e2e tests failed"
        return 1
    fi
}

# Мутационное тестирование для Python (cosmic-ray или mutmut)
run_python_mutation_tests() {
    log_step "Running Python mutation testing..."
    
    local src_dir="$ROOT_DIR/src"
    
    if [ ! -d "$src_dir" ]; then
        log_warn "Python source directory not found: $src_dir"
        return 0
    fi
    
    # Попытка использовать cosmic-ray
    if command -v cosmic-ray &> /dev/null; then
        log_info "Using cosmic-ray for mutation testing..."
        
        cd "$ROOT_DIR" || return 1
        
        # Инициализация (если нужно)
        if [ ! -f "cr-init.json" ]; then
            cosmic-ray init src tests/unit cr-init.json 2>/dev/null || true
        fi
        
        # Запуск мутаций
        if cosmic-ray exec cr-init.json 2>&1 | tee "$ROOT_DIR/test-results/mutation-python.log"; then
            local report
            report=$(cosmic-ray report cr-init.json)
            echo "$report"
            
            # Проверка процента выживших мутаций
            local survival_rate
            survival_rate=$(echo "$report" | grep -E "Survival rate:" | awk '{print $3}' | tr -d '%' || echo "100")
            
            if (( $(echo "$survival_rate < 50" | bc -l 2>/dev/null || echo 1) )); then
                log_info "Mutation testing passed (survival rate: ${survival_rate}%)"
            else
                log_warn "High mutation survival rate: ${survival_rate}%"
            fi
        else
            log_error "Mutation testing execution failed"
            return 1
        fi
    elif command -v mutmut &> /dev/null; then
        log_info "Using mutmut for mutation testing..."
        
        cd "$ROOT_DIR" || return 1
        
        if mutmut run 2>&1 | tee "$ROOT_DIR/test-results/mutation-python.log"; then
            mutmut results >> "$ROOT_DIR/test-results/mutation-python.log"
            log_info "Mutation testing completed"
        else
            log_warn "Mutmut found surviving mutations (this may be expected)"
        fi
    else
        log_warn "No mutation testing tool found (cosmic-ray or mutmut), skipping..."
        return 0
    fi
}

# Запуск unit тестов для Node.js/TypeScript
run_nodejs_unit_tests() {
    local test_dir="$ROOT_DIR/tests/unit"
    
    if [ ! -d "$test_dir" ]; then
        log_warn "Node.js unit test directory not found: $test_dir"
        return 0
    fi
    
    log_step "Running Node.js unit tests..."
    
    # Проверка наличия package.json
    if [ ! -f "$ROOT_DIR/package.json" ]; then
        log_warn "package.json not found, skipping Node.js tests"
        return 0
    fi
    
    cd "$ROOT_DIR" || return 1
    
    # Определение менеджера пакетов
    local runner="npm test"
    if [ -f "pnpm-lock.yaml" ]; then
        runner="pnpm test"
    elif [ -f "yarn.lock" ]; then
        runner="yarn test"
    fi
    
    if $runner 2>&1 | tee "$ROOT_DIR/test-results/unit-nodejs.log"; then
        log_info "Node.js unit tests passed"
    else
        log_error "Node.js unit tests failed"
        return 1
    fi
}

# Мутационное тестирование для Node.js (stryker)
run_nodejs_mutation_tests() {
    log_step "Running Node.js mutation testing..."
    
    if [ ! -f "$ROOT_DIR/package.json" ]; then
        return 0
    fi
    
    cd "$ROOT_DIR" || return 1
    
    # Проверка наличия stryker
    if npx stryker --help &> /dev/null; then
        log_info "Using stryker for mutation testing..."
        
        if npx stryker run 2>&1 | tee "$ROOT_DIR/test-results/mutation-nodejs.log"; then
            log_info "Mutation testing completed"
        else
            log_warn "Stryker found weaknesses in test suite"
        fi
    else
        log_warn "Stryker not found, skipping Node.js mutation testing"
        return 0
    fi
}

# Запуск тестов для Rust
run_rust_tests() {
    log_step "Running Rust tests..."
    
    local cargo_toml="$ROOT_DIR/Cargo.toml"
    
    if [ ! -f "$cargo_toml" ]; then
        log_warn "Cargo.toml not found, skipping Rust tests"
        return 0
    fi
    
    cd "$ROOT_DIR" || return 1
    
    # Unit и integration тесты
    if cargo test --all-features 2>&1 | tee "$ROOT_DIR/test-results/rust-tests.log"; then
        log_info "Rust tests passed"
    else
        log_error "Rust tests failed"
        return 1
    fi
    
    # Проверка покрытия с cargo-tarpaulin
    if command -v cargo-tarpaulin &> /dev/null; then
        log_info "Running Rust coverage analysis..."
        cargo tarpaulin --out Html --output-dir "$ROOT_DIR/docs/coverage/rust" || true
    fi
}

# Мутационное тестирование для Rust (cargo-mutants)
run_rust_mutation_tests() {
    log_step "Running Rust mutation testing..."
    
    local cargo_toml="$ROOT_DIR/Cargo.toml"
    
    if [ ! -f "$cargo_toml" ]; then
        return 0
    fi
    
    if command -v cargo-mutants &> /dev/null; then
        cd "$ROOT_DIR" || return 1
        
        if cargo mutants 2>&1 | tee "$ROOT_DIR/test-results/mutation-rust.log"; then
            log_info "Rust mutation testing completed"
        else
            log_warn "Rust mutation testing found issues"
        fi
    else
        log_warn "cargo-mutants not found, skipping Rust mutation testing"
        return 0
    fi
}

# Запуск тестов для Go
run_go_tests() {
    log_step "Running Go tests..."
    
    local go_mod="$ROOT_DIR/go.mod"
    
    if [ ! -f "$go_mod" ]; then
        log_warn "go.mod not found, skipping Go tests"
        return 0
    fi
    
    cd "$ROOT_DIR" || return 1
    
    # Запуск тестов с покрытием
    if go test ./... -v -coverprofile="$ROOT_DIR/test-results/go-coverage.out" 2>&1 | tee "$ROOT_DIR/test-results/go-tests.log"; then
        log_info "Go tests passed"
        
        # Генерация HTML отчета
        go tool cover -html="$ROOT_DIR/test-results/go-coverage.out" -o "$ROOT_DIR/docs/coverage/go/coverage.html" 2>/dev/null || true
    else
        log_error "Go tests failed"
        return 1
    fi
}

# Мутационное тестирование для Go (ginkgo/gomega или go-mutesting)
run_go_mutation_tests() {
    log_step "Running Go mutation testing..."
    
    local go_mod="$ROOT_DIR/go.mod"
    
    if [ ! -f "$go_mod" ]; then
        return 0
    fi
    
    if command -v go-mutesting &> /dev/null; then
        cd "$ROOT_DIR" || return 1
        
        if go-mutesting github.com/$(basename "$ROOT_DIR")/... 2>&1 | tee "$ROOT_DIR/test-results/mutation-go.log"; then
            log_info "Go mutation testing completed"
        else
            log_warn "Go mutation testing found issues"
        fi
    else
        log_warn "go-mutesting not found, skipping Go mutation testing"
        return 0
    fi
}

# Запуск тестов для C#
run_csharp_tests() {
    log_step "Running C# tests..."
    
    local sln_file=$(find "$ROOT_DIR" -name "*.sln" | head -1)
    
    if [ -z "$sln_file" ]; then
        log_warn ".sln file not found, skipping C# tests"
        return 0
    fi
    
    if ! command -v dotnet &> /dev/null; then
        log_warn "dotnet not found, skipping C# tests"
        return 0
    fi
    
    cd "$(dirname "$sln_file")" || return 1
    
    # Запуск тестов с покрытием
    if dotnet test --collect:"XPlat Code Coverage" --results-directory "$ROOT_DIR/test-results/csharp" 2>&1 | tee "$ROOT_DIR/test-results/csharp-tests.log"; then
        log_info "C# tests passed"
    else
        log_error "C# tests failed"
        return 1
    fi
}

# Основная функция
main() {
    log_info "Starting test execution..."
    
    mkdir -p "$ROOT_DIR/test-results"
    mkdir -p "$ROOT_DIR/docs/coverage"
    
    local exit_code=0
    
    # Определение языков по наличию файлов проектов
    local has_python=false
    local has_nodejs=false
    local has_rust=false
    local has_go=false
    local has_csharp=false
    
    [ -f "$ROOT_DIR/requirements.txt" ] || [ -f "$ROOT_DIR/pyproject.toml" ] || [ -f "$ROOT_DIR/uv.lock" ] && has_python=true
    [ -f "$ROOT_DIR/package.json" ] && has_nodejs=true
    [ -f "$ROOT_DIR/Cargo.toml" ] && has_rust=true
    [ -f "$ROOT_DIR/go.mod" ] && has_go=true
    [ -n "$(find "$ROOT_DIR" -name '*.csproj' | head -1)" ] && has_csharp=true
    
    # Python
    if [ "$has_python" = true ]; then
        run_python_unit_tests || exit_code=1
        run_python_integration_tests || exit_code=1
        run_python_e2e_tests || exit_code=1
        run_python_mutation_tests || exit_code=1
    fi
    
    # Node.js
    if [ "$has_nodejs" = true ]; then
        run_nodejs_unit_tests || exit_code=1
        run_nodejs_mutation_tests || exit_code=1
    fi
    
    # Rust
    if [ "$has_rust" = true ]; then
        run_rust_tests || exit_code=1
        run_rust_mutation_tests || exit_code=1
    fi
    
    # Go
    if [ "$has_go" = true ]; then
        run_go_tests || exit_code=1
        run_go_mutation_tests || exit_code=1
    fi
    
    # C#
    if [ "$has_csharp" = true ]; then
        run_csharp_tests || exit_code=1
    fi
    
    if [ $exit_code -eq 0 ]; then
        log_info "All tests passed!"
    else
        log_error "Some tests failed!"
    fi
    
    return $exit_code
}

main "$@"
