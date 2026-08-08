#!/bin/bash
# security-scan.sh - Универсальный скрипт проверки безопасности для всех языков

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Проверка наличия инструмента
check_tool() {
    local tool=$1
    if ! command -v "$tool" &> /dev/null; then
        log_warn "$tool not found, skipping..."
        return 1
    fi
    return 0
}

# Сканирование на секреты с помощью gitleaks
scan_secrets() {
    log_info "Running secret scan with gitleaks..."
    
    if check_tool "gitleaks"; then
        # Проверка на наличие .git директории
        if [ -d "$ROOT_DIR/.git" ]; then
            if gitleaks detect --source "$ROOT_DIR" --verbose --redact; then
                log_info "No secrets detected"
            else
                log_error "Secrets detected!"
                return 1
            fi
        else
            log_warn "Not a git repository, skipping gitleaks"
        fi
    fi
}

# Сканирование уязвимостей с помощью trivy
scan_vulnerabilities() {
    log_info "Running vulnerability scan with trivy..."
    
    if check_tool "trivy"; then
        # Сканирование файловой системы
        if trivy fs "$ROOT_DIR" --severity HIGH,CRITICAL --exit-code 1; then
            log_info "No critical vulnerabilities detected"
        else
            log_error "Critical vulnerabilities found!"
            return 1
        fi
    fi
}

# Статический анализ с помощью semgrep
scan_semgrep() {
    log_info "Running static analysis with semgrep..."
    
    if check_tool "semgrep"; then
        # Автоопределение языков и запуск правил
        if semgrep --config auto "$ROOT_DIR" --error; then
            log_info "Semgrep passed"
        else
            log_error "Semgrep found issues!"
            return 1
        fi
    fi
}

# Специфичные проверки для JavaScript/TypeScript
scan_js_ts() {
    log_info "Running JS/TS security checks..."
    
    local package_locks=$(find "$ROOT_DIR" -name "package-lock.json" -o -name "pnpm-lock.yaml" -o -name "yarn.lock" 2>/dev/null)
    
    if [ -n "$package_locks" ]; then
        if check_tool "npm"; then
            for lock_file in $package_locks; do
                local dir=$(dirname "$lock_file")
                log_info "Checking npm audit in $dir"
                cd "$dir" && npm audit --audit-level high || true
            done
        fi
        
        if check_tool "yarn"; then
            for lock_file in $package_locks; do
                if [[ "$lock_file" == *"yarn.lock"* ]]; then
                    local dir=$(dirname "$lock_file")
                    log_info "Checking yarn audit in $dir"
                    cd "$dir" && yarn audit --level high || true
                fi
            done
        fi
    fi
}

# Специфичные проверки для Python
scan_python() {
    log_info "Running Python security checks..."
    
    local requirements_files=$(find "$ROOT_DIR" -name "requirements*.txt" -o -name "pyproject.toml" -o -name "uv.lock" 2>/dev/null)
    
    if [ -n "$requirements_files" ]; then
        if check_tool "pip-audit"; then
            for req_file in $requirements_files; do
                if [[ "$req_file" == *"requirements"* ]]; then
                    log_info "Checking pip-audit for $req_file"
                    pip-audit -r "$req_file" || true
                fi
            done
        fi
        
        if check_tool "safety"; then
            log_info "Running safety check..."
            safety check || true
        fi
    fi
}

# Специфичные проверки для Rust
scan_rust() {
    log_info "Running Rust security checks..."
    
    local cargo_tomls=$(find "$ROOT_DIR" -name "Cargo.toml" 2>/dev/null)
    
    if [ -n "$cargo_tomls" ]; then
        if check_tool "cargo-audit"; then
            for cargo_toml in $cargo_tomls; do
                local dir=$(dirname "$cargo_toml")
                log_info "Running cargo audit in $dir"
                cd "$dir" && cargo audit || true
            done
        fi
        
        if check_tool "cargo-deny"; then
            for cargo_toml in $cargo_tomls; do
                local dir=$(dirname "$cargo_toml")
                log_info "Running cargo deny in $dir"
                cd "$dir" && cargo deny check || true
            done
        fi
    fi
}

# Специфичные проверки для Go
scan_go() {
    log_info "Running Go security checks..."
    
    local go_mods=$(find "$ROOT_DIR" -name "go.mod" 2>/dev/null)
    
    if [ -n "$go_mods" ]; then
        if check_tool "govulncheck"; then
            for go_mod in $go_mods; do
                local dir=$(dirname "$go_mod")
                log_info "Running govulncheck in $dir"
                cd "$dir" && govulncheck ./... || true
            done
        fi
    fi
}

# Специфичные проверки для C#
scan_csharp() {
    log_info "Running C# security checks..."
    
    local csproj_files=$(find "$ROOT_DIR" -name "*.csproj" 2>/dev/null)
    
    if [ -n "$csproj_files" ]; then
        if check_tool "dotnet"; then
            for csproj in $csproj_files; do
                local dir=$(dirname "$csproj")
                log_info "Running dotnet list vulnerabilities in $dir"
                cd "$dir" && dotnet list package --vulnerable || true
            done
        fi
    fi
}

# Проверка YAML/JSON файлов на безопасность
scan_yaml_json() {
    log_info "Running YAML/JSON security checks..."
    
    # Проверка Dockerfile на лучшие практики
    local dockerfiles=$(find "$ROOT_DIR" -name "Dockerfile*" -o -name "*.dockerfile" 2>/dev/null)
    
    if [ -n "$dockerfiles" ] && check_tool "hadolint"; then
        for dockerfile in $dockerfiles; do
            log_info "Linting $dockerfile with hadolint"
            hadolint "$dockerfile" || true
        done
    fi
    
    # Проверка Kubernetes манифестов
    local k8s_files=$(find "$ROOT_DIR" -name "*.yaml" -o -name "*.yml" | grep -E "(k8s|kubernetes|deployment|service)" 2>/dev/null)
    
    if [ -n "$k8s_files" ] && check_tool "kube-score"; then
        for k8s_file in $k8s_files; do
            log_info "Scoring $k8s_file with kube-score"
            kube-score score "$k8s_file" || true
        done
    fi
}

# Основная функция
main() {
    log_info "Starting security scan..."
    
    local exit_code=0
    
    # Базовые сканеры (работают всегда)
    scan_secrets || exit_code=1
    scan_vulnerabilities || exit_code=1
    scan_semgrep || exit_code=1
    
    # Языко-специфичные сканеры
    scan_js_ts || exit_code=1
    scan_python || exit_code=1
    scan_rust || exit_code=1
    scan_go || exit_code=1
    scan_csharp || exit_code=1
    scan_yaml_json || exit_code=1
    
    if [ $exit_code -eq 0 ]; then
        log_info "All security checks passed!"
    else
        log_error "Some security checks failed!"
    fi
    
    return $exit_code
}

# Запуск
main "$@"
