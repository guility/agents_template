# Sourced by unified_ci_runner.sh.

# Stage: Integration Tests
run_integration_tests() {
    log_stage "Running integration tests..."
    
    local failed=0
    
    # Python integration tests
    if [ -d "$PROJECT_ROOT/src/tests/integration" ]; then
        if command -v pytest &> /dev/null; then
            pytest "$PROJECT_ROOT/src/tests/integration" --cov=src --cov-append || failed=1
        fi
    fi
    
    # Node.js integration tests
    if [ -f "$PROJECT_ROOT/package.json" ]; then
        if command -v pnpm &> /dev/null; then
            pnpm test:integration || failed=1
        elif command -v npm &> /dev/null; then
            npm run test:integration || failed=1
        fi
    fi
    
    # Rust integration tests
    if [ -f "$PROJECT_ROOT/Cargo.toml" ]; then
        cargo test --test '*' || failed=1
    fi
    
    # Go integration tests
    if [ -f "$PROJECT_ROOT/go.mod" ]; then
        go test ./src/tests/integration/... || failed=1
    fi
    
    if [ $failed -eq 0 ]; then
        log_success "Integration tests passed"
    else
        log_error "Integration tests failed"
        return 1
    fi
}

