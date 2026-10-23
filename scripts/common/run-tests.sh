#!/bin/bash
# run-tests.sh - Универсальный скрипт запуска тестов с покрытием и мутационным тестированием

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${PROJECT_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
if [[ -d "$ROOT_DIR/.venv/bin" ]]; then
    export PATH="$ROOT_DIR/.venv/bin:$PATH"
fi

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

source "$SCRIPT_DIR/test-runners/logging.sh"
for runner in python-tests python-mutation nodejs-tests rust-tests go-tests csharp-tests; do
    source "$SCRIPT_DIR/test-runners/$runner.sh"
done
source "$SCRIPT_DIR/test-runners/suite-dispatch.sh"

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
    local requested_suite="${1:-${TEST_SUITE:-all}}"
    
    [ -f "$ROOT_DIR/requirements.txt" ] || [ -f "$ROOT_DIR/pyproject.toml" ] || [ -f "$ROOT_DIR/uv.lock" ] && has_python=true
    [ -f "$ROOT_DIR/package.json" ] && has_nodejs=true
    [ -f "$ROOT_DIR/Cargo.toml" ] && has_rust=true
    [ -f "$ROOT_DIR/go.mod" ] && has_go=true
    [ -n "$(find "$ROOT_DIR" -name '*.csproj' | head -1)" ] && has_csharp=true
    
    if [ "$has_python" != true ] && [ "$has_nodejs" != true ] && \
       [ "$has_rust" != true ] && [ "$has_go" != true ] && [ "$has_csharp" != true ]; then
        log_error "No supported language project found in $ROOT_DIR"
        return 1
    fi

    run_requested_suite "$requested_suite" "$has_python" "$has_nodejs" \
        "$has_rust" "$has_go" "$has_csharp" || exit_code=1
    
    if [ $exit_code -eq 0 ]; then
        log_info "All tests passed!"
    else
        log_error "Some tests failed!"
    fi
    
    return $exit_code
}

main "$@"
