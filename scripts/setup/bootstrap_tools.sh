#!/bin/bash
# Language-specific project initialization functions.

# Инициализация Python проекта с uv
init_python() {
    if [ -f "$PROJECT_ROOT/pyproject.toml" ] || [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        log_step "Initializing Python project..."
        
        if command -v uv &> /dev/null; then
            cd "$PROJECT_ROOT"
            uv sync --all-extras
            log_info "Python project initialized with uv"
        else
            log_warn "uv not found, please install: curl -LsSf https://astral.sh/uv/install.sh | sh"
        fi
    fi
}

# Инициализация Node.js проекта
init_nodejs() {
    if [ -f "$PROJECT_ROOT/package.json" ]; then
        log_step "Initializing Node.js project..."
        
        cd "$PROJECT_ROOT"
        
        if [ -f "$PROJECT_ROOT/pnpm-lock.yaml" ]; then
            pnpm install --frozen-lockfile
            log_info "Node.js project initialized with pnpm"
        elif [ -f "$PROJECT_ROOT/yarn.lock" ]; then
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
    if [ -f "$PROJECT_ROOT/Cargo.toml" ]; then
        log_step "Initializing Rust project..."
        cd "$PROJECT_ROOT"
        cargo fetch
        log_info "Rust project initialized"
    fi
}

# Инициализация Go проекта
init_go() {
    if [ -f "$PROJECT_ROOT/go.mod" ]; then
        log_step "Initializing Go project..."
        cd "$PROJECT_ROOT"
        go mod download
        log_info "Go project initialized"
    fi
}

# Инициализация C# проекта
init_csharp() {
    if [ -n "$(find "$PROJECT_ROOT" -name '*.csproj' | head -1)" ]; then
        log_step "Initializing C# project..."
        cd "$PROJECT_ROOT"
        dotnet restore
        log_info "C# project initialized"
    fi
}
