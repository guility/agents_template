# Source this stage into the unified runner so failures are reported with the other pipeline gates.

# Exercise component boundaries to catch wiring and dependency issues that unit tests cannot reveal.
run_integration_tests() {
    log_stage "Running integration tests..."
    
    # Continue through available integration runners so one failure does not hide the rest.
    local failed=0
    
    # Append coverage to the unit report so both suites contribute to one coverage view.
    if [ -d "$PROJECT_ROOT/src/tests/integration" ]; then
        if command -v pytest &> /dev/null; then
            pytest "$PROJECT_ROOT/src/tests/integration" --cov=src --cov-append || failed=1
        fi
    fi
    
    # Prefer pnpm when installed, with npm as a fallback for existing Node projects.
    if [ -f "$PROJECT_ROOT/package.json" ]; then
        if command -v pnpm &> /dev/null; then
            pnpm test:integration || failed=1
        elif command -v npm &> /dev/null; then
            npm run test:integration || failed=1
        fi
    fi
    
    # Use Rust's integration targets because cargo test --lib does not include them.
    if [ -f "$PROJECT_ROOT/Cargo.toml" ]; then
        cargo test --test '*' || failed=1
    fi
    
    # Restrict Go discovery to integration packages so this stage reports the intended test layer.
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

