# Source this file from the unified runner so stage functions share its paths, logs, and status context.

# Exercise complete user-facing flows because component tests cannot prove the full system works.
run_e2e_tests() {
    log_stage "Running e2e tests..."
    
    # Keep trying available E2E runners so one failure does not hide another suite's result.
    local failed=0
    
    # Run Python acceptance tests only when the repository has that test tree and pytest is installed.
    if [ -d "$PROJECT_ROOT/src/tests/e2e" ]; then
        if command -v pytest &> /dev/null; then
            pytest "$PROJECT_ROOT/src/tests/e2e" || failed=1
        fi
    fi
    
    # Delegate browser tooling to the package script so Playwright/Cypress options remain project-owned.
    if [ -f "$PROJECT_ROOT/package.json" ]; then
        if command -v pnpm &> /dev/null; then
            pnpm test:e2e || failed=1
        elif command -v npm &> /dev/null; then
            npm run test:e2e || failed=1
        fi
    fi
    
    if [ $failed -eq 0 ]; then
        log_success "E2E tests passed"
    else
        log_error "E2E tests failed"
        return 1
    fi
}

# Check test effectiveness by applying mutations and requiring tests to detect those changes.
run_mutation_tests() {
    log_stage "Running mutation tests..."
    
    if [ -f "$SCRIPTS_DIR/testing/mutation_runner.py" ]; then
        python3 "$SCRIPTS_DIR/testing/mutation_runner.py" \
            --project-root "$PROJECT_ROOT" \
            --generate-report
        log_success "Mutation tests completed"
    else
        # Some consumers adopt this optional helper before they maintain a mutation runner.
        log_warn "Mutation runner not found, skipping"
    fi
}

# Link requirements to tests so reviewers can see which expected behaviors are covered.
run_traceability_check() {
    log_stage "Running traceability check..."
    
    if [ -f "$SCRIPTS_DIR/testing/traceability_matrix.py" ]; then
        python3 "$SCRIPTS_DIR/testing/traceability_matrix.py" \
            --root "$PROJECT_ROOT" \
            --output "$PROJECT_ROOT/reports/testing/traceability_matrix.json"
        log_success "Traceability check completed"
    else
        # Make gradual adoption visible instead of implying a traceability report was produced.
        log_warn "Traceability matrix generator not found, skipping"
    fi
}

