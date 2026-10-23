run_python_mutation_tests() {
    log_step "Running Python mutation testing..."

    local src_dir="$ROOT_DIR/src"

    if [ ! -d "$src_dir" ]; then
        log_error "Python source directory not found: $src_dir"
        return 1
    fi

    # Попытка использовать cosmic-ray
    if command -v cosmic-ray &> /dev/null; then
        log_info "Using cosmic-ray for mutation testing..."

        cd "$ROOT_DIR" || return 1

        # Инициализация (если нужно)
        if [ ! -f "cr-init.json" ]; then
            cosmic-ray init src tests/unit cr-init.json 2>/dev/null || true
        fi

        # Запуск мутаций
        if cosmic-ray exec cr-init.json 2>&1 | tee "$ROOT_DIR/test-results/mutation-python.log"; then
            local report
            report=$(cosmic-ray report cr-init.json)
            echo "$report"

            # Проверка процента выживших мутаций
            local survival_rate
            survival_rate=$(echo "$report" | grep -E "Survival rate:" | awk '{print $3}' | tr -d '%' || echo "100")

            if (( $(echo "$survival_rate < 50" | bc -l 2>/dev/null || echo 1) )); then
                log_info "Mutation testing passed (survival rate: ${survival_rate}%)"
            else
                log_warn "High mutation survival rate: ${survival_rate}%"
            fi
        else
            log_error "Mutation testing execution failed"
            return 1
        fi
    elif command -v mutmut &> /dev/null; then
        log_info "Using mutmut for mutation testing..."

        cd "$ROOT_DIR" || return 1

        if mutmut run 2>&1 | tee "$ROOT_DIR/test-results/mutation-python.log"; then
            mutmut results >> "$ROOT_DIR/test-results/mutation-python.log"
            log_info "Mutation testing completed"
        else
            log_warn "Mutmut found surviving mutations (this may be expected)"
        fi
    else
        log_error "No mutation testing tool found (cosmic-ray or mutmut)"
        return 1
    fi
}

# Запуск unit тестов для Node.js/TypeScript
