#!/bin/bash
# pre-commit.sh - Pre-commit хук для автоматических проверок перед коммитом

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

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

# Получение списка измененных файлов
get_changed_files() {
    local files=()
    
    # Файлы в индексе (staged)
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            files+=("$file")
        fi
    done < <(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)
    
    echo "${files[@]}"
}

# Проверка секретов в измененных файлах
check_secrets() {
    log_step "Checking for secrets in changed files..."
    
    local files=("$@")
    
    if [ ${#files[@]} -eq 0 ]; then
        return 0
    fi
    
    if command -v gitleaks &> /dev/null; then
        # Создаем временный файл со списком файлов
        local temp_file=$(mktemp)
        printf '%s\n' "${files[@]}" > "$temp_file"
        
        # Запуск gitleaks на staged изменения
        if git diff --cached | gitleaks detect --source /dev/stdin --verbose 2>/dev/null; then
            log_info "No secrets detected in staged changes"
            rm -f "$temp_file"
            return 0
        else
            log_error "Secrets detected in staged changes!"
            rm -f "$temp_file"
            return 1
        fi
    else
        log_warn "gitleaks not found, skipping secret check"
        return 0
    fi
}

# Проверка сложности измененных файлов
check_complexity() {
    log_step "Checking complexity of changed files..."
    
    local files=("$@")
    
    if [ ${#files[@]} -eq 0 ]; then
        return 0
    fi
    
    # Фильтрация только файлов с кодом
    local code_files=()
    for file in "${files[@]}"; do
        case "$file" in
            *.py|*.js|*.ts|*.jsx|*.tsx|*.java|*.cpp|*.c|*.h|*.go|*.rb|*.swift|*.scala|*.kt|*.cs|*.m)
                code_files+=("$file")
                ;;
        esac
    done
    
    if [ ${#code_files[@]} -gt 0 ]; then
        if [ -f "$SCRIPT_DIR/common/complexity-check.sh" ]; then
            bash "$SCRIPT_DIR/common/complexity-check.sh" files "${code_files[@]}" || return 1
        else
            log_warn "complexity-check.sh not found, skipping complexity check"
        fi
    fi
}

# Форматирование измененных файлов
format_changed() {
    log_step "Formatting changed files..."
    
    local files=("$@")
    
    if [ ${#files[@]} -eq 0 ]; then
        return 0
    fi
    
    if [ -f "$SCRIPT_DIR/common/format-code.sh" ]; then
        bash "$SCRIPT_DIR/common/format-code.sh" "${files[@]}" || true
        
        # Добавляем отформатированные файлы обратно в индекс
        for file in "${files[@]}"; do
            if [ -f "$file" ]; then
                git add "$file" 2>/dev/null || true
            fi
        done
        
        log_info "Changed files formatted"
    else
        log_warn "format-code.sh not found, skipping formatting"
    fi
}

# Быстрые unit тесты для измененных файлов
run_quick_tests() {
    log_step "Running quick tests for changed files..."
    
    local files=("$@")
    
    if [ ${#files[@]} -eq 0 ]; then
        return 0
    fi
    
    # Определение затронутых тестов
    local test_files=()
    for file in "${files[@]}"; do
        case "$file" in
            *.py)
                # Поиск соответствующих тестов
                local test_file=$(echo "$file" | sed 's|/src/|/tests/unit/|' | sed 's|\.py$|_test.py|')
                if [ -f "$test_file" ]; then
                    test_files+=("$test_file")
                fi
                ;;
        esac
    done
    
    if [ ${#test_files[@]} -gt 0 ]; then
        if command -v pytest &> /dev/null; then
            log_info "Running ${#test_files[@]} affected test files..."
            pytest "${test_files[@]}" -v --tb=short 2>&1 | tail -20 || return 1
        else
            log_warn "pytest not found, skipping quick tests"
        fi
    else
        log_info "No directly affected tests found"
    fi
}

# Линтинг измененных файлов
lint_changed() {
    log_step "Linting changed files..."
    
    local files=("$@")
    
    if [ ${#files[@]} -eq 0 ]; then
        return 0
    fi
    
    local exit_code=0
    
    for file in "${files[@]}"; do
        case "$file" in
            *.py)
                if command -v flake8 &> /dev/null; then
                    flake8 "$file" --max-line-length=120 --ignore=E501,W503 || ((exit_code++))
                fi
                if command -v pylint &> /dev/null; then
                    pylint "$file" --disable=all --enable=E,F || ((exit_code++))
                fi
                ;;
            *.js|*.ts|*.jsx|*.tsx)
                if command -v eslint &> /dev/null; then
                    eslint "$file" || ((exit_code++))
                fi
                ;;
            *.rs)
                if command -v clippy &> /dev/null; then
                    cargo clippy 2>/dev/null || ((exit_code++))
                fi
                ;;
            *.go)
                if command -v golint &> /dev/null; then
                    golint "$file" || ((exit_code++))
                fi
                if command -v staticcheck &> /dev/null; then
                    staticcheck "$file" || ((exit_code++))
                fi
                ;;
            *.sh)
                if command -v shellcheck &> /dev/null; then
                    shellcheck "$file" || ((exit_code++))
                fi
                ;;
        esac
    done
    
    if [ $exit_code -gt 0 ]; then
        log_error "Linting found $exit_code issue(s)"
        return 1
    fi
    
    log_info "Linting passed"
    return 0
}

# Основная функция
main() {
    log_info "Running pre-commit checks..."
    
    local changed_files=($(get_changed_files))
    
    if [ ${#changed_files[@]} -eq 0 ]; then
        log_info "No staged changes to check"
        exit 0
    fi
    
    log_info "Found ${#changed_files[@]} staged file(s)"
    
    local exit_code=0
    
    # 1. Форматирование (может изменить файлы)
    format_changed "${changed_files[@]}" || true
    
    # 2. Проверка секретов
    check_secrets "${changed_files[@]}" || exit_code=1
    
    # 3. Проверка сложности
    check_complexity "${changed_files[@]}" || exit_code=1
    
    # 4. Линтинг
    lint_changed "${changed_files[@]}" || exit_code=1
    
    # 5. Быстрые тесты (опционально, не блокирует коммит)
    run_quick_tests "${changed_files[@]}" || log_warn "Quick tests failed, but continuing with commit"
    
    if [ $exit_code -eq 0 ]; then
        log_info "All pre-commit checks passed!"
    else
        log_error "Some pre-commit checks failed!"
        log_error "Please fix the issues and try again."
    fi
    
    return $exit_code
}

main "$@"
