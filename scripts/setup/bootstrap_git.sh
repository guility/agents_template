#!/bin/bash
# Git hook setup.

# Установка pre-commit хуков
install_git_hooks() {
    log_step "Installing Git hooks..."
    
    if [ ! -d "$PROJECT_ROOT/.git" ]; then
        log_warn "Not a git repository, skipping hook installation"
        return 0
    fi
    
    # Создание директории hooks если не существует
    mkdir -p "$PROJECT_ROOT/.git/hooks"
    
    # Копирование pre-commit хука
    if [ -f "$PROJECT_ROOT/scripts/common/hooks/pre-commit.sh" ]; then
        cp "$PROJECT_ROOT/scripts/common/hooks/pre-commit.sh" "$PROJECT_ROOT/.git/hooks/pre-commit"
        chmod +x "$PROJECT_ROOT/.git/hooks/pre-commit"
        log_info "pre-commit hook installed"
    else
        log_warn "pre-commit.sh not found"
    fi
    
    # Создание symlink для удобства
    if [ -d "$PROJECT_ROOT/.git/hooks" ]; then
        ln -sf "../../scripts/common/hooks/pre-commit.sh" "$PROJECT_ROOT/.git/hooks/pre-commit-local" 2>/dev/null || true
    fi
}
