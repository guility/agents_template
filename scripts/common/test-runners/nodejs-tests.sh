run_nodejs_unit_tests() {
    local test_dir="$ROOT_DIR/tests/unit"

    if [ ! -d "$test_dir" ]; then
        log_error "Node.js unit test directory not found: $test_dir"
        return 1
    fi

    log_step "Running Node.js unit tests..."

    # Проверка наличия package.json
    if [ ! -f "$ROOT_DIR/package.json" ]; then
        log_error "package.json not found; cannot run Node.js tests"
        return 1
    fi

    cd "$ROOT_DIR" || return 1

    # Определение менеджера пакетов
    local runner="npm test"
    if [ -f "pnpm-lock.yaml" ]; then
        runner="pnpm test"
    elif [ -f "yarn.lock" ]; then
        runner="yarn test"
    fi

    if $runner 2>&1 | tee "$ROOT_DIR/test-results/unit-nodejs.log"; then
        log_info "Node.js unit tests passed"
    else
        log_error "Node.js unit tests failed"
        return 1
    fi
}

# Мутационное тестирование для Node.js (stryker)
run_nodejs_mutation_tests() {
    log_step "Running Node.js mutation testing..."

    if [ ! -f "$ROOT_DIR/package.json" ]; then
        return 0
    fi

    cd "$ROOT_DIR" || return 1

    # Проверка наличия stryker
    if npx stryker --help &> /dev/null; then
        log_info "Using stryker for mutation testing..."

        if npx stryker run 2>&1 | tee "$ROOT_DIR/test-results/mutation-nodejs.log"; then
            log_info "Mutation testing completed"
        else
            log_warn "Stryker found weaknesses in test suite"
        fi
    else
        log_error "Stryker not found; cannot run Node.js mutation testing"
        return 1
    fi
}

# Запуск тестов для Rust
