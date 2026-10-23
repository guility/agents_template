#!/bin/bash
# Language-specific dependency installation for bootstrap.sh.

# Установка глобальных зависимостей
install_global_tools() {
    log_step "Installing global development tools..."
    
    # Python инструменты
    if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
        log_info "Installing Python tools..."
        pip install -q black isort flake8 pylint pytest pytest-cov lizard semgrep pip-audit || true
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
