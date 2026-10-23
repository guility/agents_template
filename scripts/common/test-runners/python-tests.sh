run_python_unit_tests() {
    local test_dir="$ROOT_DIR/tests/unit"

    if [ ! -d "$test_dir" ]; then
        log_error "Python unit test directory not found: $test_dir"
        return 1
    fi

    log_step "Running Python unit tests..."

    # Проверка наличия pytest и coverage
    if ! command -v pytest &> /dev/null; then
        log_error "pytest not found; cannot run Python unit tests"
        return 1
    fi

    # Запуск с покрытием
    cd "$test_dir" || return 1

    local coverage_file=".coverage.unit"

    if pytest --cov=src --cov-report=term-missing --cov-report=html:"$ROOT_DIR/docs/coverage/unit" \
              --cov-fail-under="$COVERAGE_TARGET" \
              --junitxml="$ROOT_DIR/test-results/unit-python.xml" \
              -v 2>&1 | tee "$ROOT_DIR/test-results/unit-python.log"; then
        log_info "Python unit tests passed with ${COVERAGE_TARGET}% coverage"
    else
        log_error "Python unit tests failed"
        return 1
    fi
}

# Запуск integration тестов для Python
run_python_integration_tests() {
    local test_dir="$ROOT_DIR/tests/integration"

    if [ ! -d "$test_dir" ]; then
        log_error "Python integration test directory not found: $test_dir"
        return 1
    fi

    log_step "Running Python integration tests..."

    if ! command -v pytest &> /dev/null; then
        log_error "pytest not found; cannot run Python integration tests"
        return 1
    fi

    cd "$test_dir" || return 1

    if pytest --cov=src --cov-report=term-missing --cov-report=html:"$ROOT_DIR/docs/coverage/integration" \
              --cov-fail-under="$COVERAGE_TARGET" \
              --junitxml="$ROOT_DIR/test-results/integration-python.xml" \
              -v 2>&1 | tee "$ROOT_DIR/test-results/integration-python.log"; then
        log_info "Python integration tests passed"
    else
        log_error "Python integration tests failed"
        return 1
    fi
}

# Запуск e2e тестов для Python
run_python_e2e_tests() {
    local test_dir="$ROOT_DIR/tests/e2e"

    if [ ! -d "$test_dir" ]; then
        log_error "Python e2e test directory not found: $test_dir"
        return 1
    fi

    log_step "Running Python e2e tests..."

    if ! command -v pytest &> /dev/null; then
        log_error "pytest not found; cannot run Python e2e tests"
        return 1
    fi

    cd "$test_dir" || return 1

    if pytest --cov=src --cov-report=term-missing \
              --cov-fail-under="$COVERAGE_TARGET" \
              --junitxml="$ROOT_DIR/test-results/e2e-python.xml" \
              -v 2>&1 | tee "$ROOT_DIR/test-results/e2e-python.log"; then
        log_info "Python e2e tests passed"
    else
        log_error "Python e2e tests failed"
        return 1
    fi
}

# Мутационное тестирование для Python (cosmic-ray или mutmut)
