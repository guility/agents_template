run_rust_tests() {
    log_step "Running Rust tests..."

    local cargo_toml="$ROOT_DIR/Cargo.toml"

    if [ ! -f "$cargo_toml" ]; then
        log_error "Cargo.toml not found; cannot run Rust tests"
        return 1
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
        log_error "cargo-mutants not found; cannot run Rust mutation testing"
        return 1
    fi
}

# Запуск тестов для Go
