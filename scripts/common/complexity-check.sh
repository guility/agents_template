#!/bin/bash
# complexity-check.sh - Проверка цикломатической сложности кода с помощью lizard

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Порог сложности (максимально допустимая CNC)
COMPLEXITY_THRESHOLD=${COMPLEXITY_THRESHOLD:-10}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия lizard
check_lizard() {
    if ! command -v lizard &> /dev/null; then
        log_warn "lizard not found, installing..."
        if command -v pip &> /dev/null; then
            pip install lizard 2>/dev/null || true
        elif command -v pip3 &> /dev/null; then
            pip3 install lizard 2>/dev/null || true
        else
            log_error "pip not found, cannot install lizard"
            return 1
        fi
    fi
    return 0
}

# Анализ сложности
check_complexity() {
    local target_dir="${1:-$ROOT_DIR}"
    
    log_info "Checking code complexity in $target_dir (threshold: $COMPLEXITY_THRESHOLD)..."
    
    if ! check_lizard; then
        log_error "Cannot proceed without lizard"
        return 1
    fi
    
    # Запуск lizard с порогом сложности
    # -C устанавливает порог, функции выше порога генерируют предупреждения
    local lizard_output
    lizard_output=$(lizard "$target_dir" \
        -C "$COMPLEXITY_THRESHOLD" \
        --languages python,java,script,cpp,go,ruby,swift,scala,kotlin,typescript,csharp,objective-c,tsk,rust,tsx,vue,fortran,zig 2>&1) || true
    
    # Проверяем есть ли функции с превышением порога
    if echo "$lizard_output" | grep -q "warning:"; then
        log_error "Functions exceeding complexity threshold ($COMPLEXITY_THRESHOLD):"
        echo "$lizard_output" | grep -A5 "warning:" || echo "$lizard_output"
        return 1
    fi
    
    # Полный отчет для статистики
    log_info "Running full complexity analysis..."
    local full_report
    full_report=$(lizard "$target_dir" \
        --languages python,java,script,cpp,go,ruby,swift,scala,kotlin,typescript,csharp,objective-c,tsk,rust,tsx,vue,fortran,zig \
        2>&1) || true
    
    # Сохранение отчета в файл
    local report_file="$ROOT_DIR/docs/complexity-report-$(date +%Y%m%d-%H%M%S).txt"
    mkdir -p "$(dirname "$report_file")"
    echo "$full_report" > "$report_file"
    log_info "Full complexity report saved to: $report_file"
    
    # Извлечение статистики
    local total_functions
    local avg_complexity
    
    total_functions=$(echo "$full_report" | grep -E "^[0-9]+.*functions?" | tail -1 | awk '{print $1}' || echo "unknown")
    avg_complexity=$(echo "$full_report" | grep -E "average CCN" | awk '{print $NF}' || echo "unknown")
    
    log_info "Total functions analyzed: $total_functions"
    log_info "Average cyclomatic complexity: $avg_complexity"
    
    log_info "All functions are within complexity threshold ($COMPLEXITY_THRESHOLD)!"
    return 0
}

# Проверка конкретных файлов (для pre-commit хука)
check_files() {
    local files=("$@")
    
    if [ ${#files[@]} -eq 0 ]; then
        log_warn "No files to check"
        return 0
    fi
    
    log_info "Checking complexity for ${#files[@]} files..."
    
    if ! check_lizard; then
        return 1
    fi
    
    local failed=0
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            local result
            result=$(lizard "$file" --CCN "$COMPLEXITY_THRESHOLD" --warning_only 2>&1) || true
            
            if [ -n "$result" ]; then
                log_error "Complexity issues in $file:"
                echo "$result"
                ((failed++))
            fi
        fi
    done
    
    if [ $failed -gt 0 ]; then
        log_error "$failed file(s) exceeded complexity threshold"
        return 1
    fi
    
    log_info "All checked files passed complexity check!"
    return 0
}

# Основная функция
main() {
    case "${1:-full}" in
        full)
            check_complexity "${2:-$ROOT_DIR}"
            ;;
        files)
            shift
            check_files "$@"
            ;;
        *)
            echo "Usage: $0 [full|files] [args...]"
            echo "  full [directory] - Check entire directory (default: root)"
            echo "  files <file1> <file2> ... - Check specific files"
            exit 1
            ;;
    esac
}

main "$@"
