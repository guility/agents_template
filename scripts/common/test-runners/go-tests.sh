run_go_tests() {
    log_step "Running Go tests..."

    local go_mod="$ROOT_DIR/go.mod"

    if [ ! -f "$go_mod" ]; then
        log_error "go.mod not found; cannot run Go tests"
        return 1
    fi

    cd "$ROOT_DIR" || return 1

    # Запуск тестов с покрытием
    if go test ./... -v -coverprofile="$ROOT_DIR/test-results/go-coverage.out" 2>&1 | tee "$ROOT_DIR/test-results/go-tests.log"; then
        log_info "Go tests passed"

        # Генерация HTML отчета
        go tool cover -html="$ROOT_DIR/test-results/go-coverage.out" -o "$ROOT_DIR/docs/coverage/go/coverage.html" 2>/dev/null || true
    else
        log_error "Go tests failed"
        return 1
    fi
}

# Мутационное тестирование для Go (ginkgo/gomega или go-mutesting)
run_go_mutation_tests() {
    log_step "Running Go mutation testing..."

    local go_mod="$ROOT_DIR/go.mod"

    if [ ! -f "$go_mod" ]; then
        return 0
    fi

    if command -v go-mutesting &> /dev/null; then
        cd "$ROOT_DIR" || return 1

        if go-mutesting github.com/$(basename "$ROOT_DIR")/... 2>&1 | tee "$ROOT_DIR/test-results/mutation-go.log"; then
            log_info "Go mutation testing completed"
        else
            log_warn "Go mutation testing found issues"
        fi
    else
        log_error "go-mutesting not found; cannot run Go mutation testing"
        return 1
    fi
}

# Запуск тестов для C#
