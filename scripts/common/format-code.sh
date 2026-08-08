#!/bin/bash
# format-code.sh - Универсальный скрипт форматирования кода для всех языков

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

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

# Форматирование Python кода
format_python() {
    log_step "Formatting Python code..."
    
    local files=("$@")
    
    # Проверка наличия black
    if command -v black &> /dev/null; then
        if [ ${#files[@]} -gt 0 ]; then
            black "${files[@]}" 2>/dev/null || true
        else
            black "$ROOT_DIR" 2>/dev/null || true
        fi
        log_info "Python code formatted with black"
    else
        log_warn "black not found, skipping Python formatting"
    fi
    
    # Проверка наличия isort
    if command -v isort &> /dev/null; then
        if [ ${#files[@]} -gt 0 ]; then
            isort "${files[@]}" 2>/dev/null || true
        else
            isort "$ROOT_DIR" 2>/dev/null || true
        fi
        log_info "Python imports sorted with isort"
    fi
}

# Форматирование JavaScript/TypeScript кода
format_js_ts() {
    log_step "Formatting JavaScript/TypeScript code..."
    
    if [ ! -f "$ROOT_DIR/package.json" ]; then
        log_warn "package.json not found, skipping JS/TS formatting"
        return 0
    fi
    
    cd "$ROOT_DIR" || return 1
    
    # Определение менеджера пакетов
    local runner="npx prettier"
    if [ -f "pnpm-lock.yaml" ]; then
        runner="pnpm exec prettier"
    elif [ -f "yarn.lock" ]; then
        runner="yarn exec prettier"
    fi
    
    # Проверка наличия prettier
    if $runner --help &> /dev/null; then
        if [ $# -gt 0 ]; then
            $runner --write "$@" 2>/dev/null || true
        else
            $runner --write "**/*.{js,ts,jsx,tsx,json}" 2>/dev/null || true
        fi
        log_info "JS/TS code formatted with prettier"
    else
        log_warn "prettier not found, skipping JS/TS formatting"
    fi
}

# Форматирование Rust кода
format_rust() {
    log_step "Formatting Rust code..."
    
    if [ ! -f "$ROOT_DIR/Cargo.toml" ]; then
        log_warn "Cargo.toml not found, skipping Rust formatting"
        return 0
    fi
    
    if command -v rustfmt &> /dev/null; then
        cd "$ROOT_DIR" || return 1
        cargo fmt 2>/dev/null || true
        log_info "Rust code formatted with rustfmt"
    else
        log_warn "rustfmt not found, skipping Rust formatting"
    fi
}

# Форматирование Go кода
format_go() {
    log_step "Formatting Go code..."
    
    if [ ! -f "$ROOT_DIR/go.mod" ]; then
        log_warn "go.mod not found, skipping Go formatting"
        return 0
    fi
    
    if command -v gofmt &> /dev/null; then
        cd "$ROOT_DIR" || return 1
        gofmt -w . 2>/dev/null || true
        log_info "Go code formatted with gofmt"
        
        # Дополнительно: goimports для импортов
        if command -v goimports &> /dev/null; then
            goimports -w . 2>/dev/null || true
            log_info "Go imports organized with goimports"
        fi
    else
        log_warn "gofmt not found, skipping Go formatting"
    fi
}

# Форматирование C# кода
format_csharp() {
    log_step "Formatting C# code..."
    
    local sln_file=$(find "$ROOT_DIR" -name "*.sln" | head -1)
    
    if [ -z "$sln_file" ]; then
        log_warn ".sln file not found, skipping C# formatting"
        return 0
    fi
    
    if command -v dotnet &> /dev/null; then
        cd "$(dirname "$sln_file")" || return 1
        
        # Проверка наличия dotnet-format
        if dotnet tool list -g | grep -q dotnet-format; then
            dotnet format 2>/dev/null || true
            log_info "C# code formatted with dotnet-format"
        else
            log_warn "dotnet-format not found, trying built-in formatter..."
            dotnet format whitespace 2>/dev/null || true
        fi
    else
        log_warn "dotnet not found, skipping C# formatting"
    fi
}

# Форматирование YAML/JSON файлов
format_yaml_json() {
    log_step "Formatting YAML/JSON files..."
    
    if command -v prettier &> /dev/null; then
        if [ $# -gt 0 ]; then
            prettier --write "$@" 2>/dev/null || true
        else
            find "$ROOT_DIR" -type f \( -name "*.yaml" -o -name "*.yml" -o -name "*.json" \) \
                -not -path "*/node_modules/*" \
                -not -path "*/.git/*" \
                -not -path "*/target/*" \
                -not -path "*/build/*" \
                -exec prettier --write {} \; 2>/dev/null || true
        fi
        log_info "YAML/JSON files formatted with prettier"
    else
        log_warn "prettier not found, skipping YAML/JSON formatting"
    fi
}

# Форматирование Shell скриптов
format_shell() {
    log_step "Formatting Shell scripts..."
    
    if command -v shfmt &> /dev/null; then
        if [ $# -gt 0 ]; then
            shfmt -w "$@" 2>/dev/null || true
        else
            find "$ROOT_DIR" -type f -name "*.sh" \
                -not -path "*/node_modules/*" \
                -not -path "*/.git/*" \
                -exec shfmt -w {} \; 2>/dev/null || true
        fi
        log_info "Shell scripts formatted with shfmt"
    else
        log_warn "shfmt not found, skipping Shell formatting"
    fi
}

# Форматирование Markdown файлов
format_markdown() {
    log_step "Formatting Markdown files..."
    
    if command -v prettier &> /dev/null; then
        find "$ROOT_DIR" -type f -name "*.md" \
            -not -path "*/node_modules/*" \
            -not -path "*/.git/*" \
            -exec prettier --write {} \; 2>/dev/null || true
        log_info "Markdown files formatted with prettier"
    else
        log_warn "prettier not found, skipping Markdown formatting"
    fi
}

# Основная функция
main() {
    log_info "Starting code formatting..."
    
    # Если переданы файлы как аргументы, форматируем только их
    if [ $# -gt 0 ]; then
        local py_files=()
        local js_files=()
        local yaml_files=()
        local sh_files=()
        
        for file in "$@"; do
            case "$file" in
                *.py)
                    py_files+=("$file")
                    ;;
                *.js|*.ts|*.jsx|*.tsx)
                    js_files+=("$file")
                    ;;
                *.yaml|*.yml|*.json)
                    yaml_files+=("$file")
                    ;;
                *.sh)
                    sh_files+=("$file")
                    ;;
            esac
        done
        
        [ ${#py_files[@]} -gt 0 ] && format_python "${py_files[@]}"
        [ ${#js_files[@]} -gt 0 ] && format_js_ts "${js_files[@]}"
        [ ${#yaml_files[@]} -gt 0 ] && format_yaml_json "${yaml_files[@]}"
        [ ${#sh_files[@]} -gt 0 ] && format_shell "${sh_files[@]}"
    else
        # Форматирование всего проекта
        format_python
        format_js_ts
        format_rust
        format_go
        format_csharp
        format_yaml_json
        format_shell
        format_markdown
    fi
    
    log_info "Code formatting completed!"
}

main "$@"
