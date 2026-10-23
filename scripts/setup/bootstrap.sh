#!/bin/bash
# bootstrap.sh - Скрипт инициализации проекта и установки pre-commit хуков

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || (cd "$SCRIPT_DIR/../.." && pwd))"

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

source "$SCRIPT_DIR/bootstrap_global_tools.sh"
source "$SCRIPT_DIR/bootstrap_tools.sh"
source "$SCRIPT_DIR/bootstrap_git.sh"
source "$SCRIPT_DIR/bootstrap_structure.sh"
source "$SCRIPT_DIR/bootstrap_readme.sh"

# Проверка CI платформы
detect_ci_platform() {
    log_step "Detecting CI platform..."
    
    if [ -d "$PROJECT_ROOT/.github/workflows" ]; then
        log_info "GitHub Actions detected"
        echo "github" > "$PROJECT_ROOT/.ci-platform"
    elif [ -d "$PROJECT_ROOT/.gitlab/ci" ]; then
        log_info "GitLab CI detected"
        echo "gitlab" > "$PROJECT_ROOT/.ci-platform"
    else
        log_warn "No CI platform configuration found"
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
    log_info "2. Start developing in src/core/domain/"
    log_info "3. Write tests in src/tests/"
    log_info "4. Commit with automatic pre-commit checks"
}

main "$@"
