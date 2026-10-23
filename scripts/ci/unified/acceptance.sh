# Sourced by unified_ci_runner.sh.

# Stage: E2E Tests
run_e2e_tests() {
    log_stage "Running e2e tests..."
    
    local failed=0
    
    # Python e2e tests
    if [ -d "$PROJECT_ROOT/src/tests/e2e" ]; then
        if command -v pytest &> /dev/null; then
            pytest "$PROJECT_ROOT/src/tests/e2e" || failed=1
        fi
    fi
    
    # Node.js e2e tests (Playwright/Cypress)
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

# Stage: Mutation Tests
run_mutation_tests() {
    log_stage "Running mutation tests..."
    
    if [ -f "$SCRIPTS_DIR/testing/mutation_runner.py" ]; then
        python3 "$SCRIPTS_DIR/testing/mutation_runner.py" \
            --project-root "$PROJECT_ROOT" \
            --generate-report
        log_success "Mutation tests completed"
    else
        log_warn "Mutation runner not found, skipping"
    fi
}

# Stage: Traceability Check
run_traceability_check() {
    log_stage "Running traceability check..."
    
    if [ -f "$SCRIPTS_DIR/testing/traceability_matrix.py" ]; then
        python3 "$SCRIPTS_DIR/testing/traceability_matrix.py" \
            --root "$PROJECT_ROOT" \
            --output "$PROJECT_ROOT/reports/testing/traceability_matrix.json"
        log_success "Traceability check completed"
    else
        log_warn "Traceability matrix generator not found, skipping"
    fi
}

