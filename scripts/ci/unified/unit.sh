# Sourced by unified_ci_runner.sh.

# Stage: Unit Tests
run_unit_tests() {
    log_stage "Running unit tests..."
    
    local test_dirs=("src/tests/unit" "src/templates/**/tests")
    local failed=0
    
    for test_dir in "${test_dirs[@]}"; do
        if [ -d "$PROJECT_ROOT/$test_dir" ]; then
            # Python tests
            if [ -d "$PROJECT_ROOT/src/tests/unit/python" ] || [ -d "$PROJECT_ROOT/src/tests/unit" ]; then
                if command -v pytest &> /dev/null; then
                    pytest "$PROJECT_ROOT/src/tests/unit" --cov=src --cov-report=xml --cov-fail-under=100 || failed=1
                fi
            fi
            
            # Node.js tests
            if [ -f "$PROJECT_ROOT/package.json" ]; then
                if command -v pnpm &> /dev/null; then
                    pnpm test:unit || failed=1
                elif command -v npm &> /dev/null; then
                    npm run test:unit || failed=1
                fi
            fi
            
            # Rust tests
            if [ -f "$PROJECT_ROOT/Cargo.toml" ]; then
                cargo test --lib || failed=1
            fi
            
            # Go tests
            if [ -f "$PROJECT_ROOT/go.mod" ]; then
                go test ./... -coverprofile=coverage.out || failed=1
            fi
        fi
    done
    
    if [ $failed -eq 0 ]; then
        log_success "Unit tests passed"
    else
        log_error "Unit tests failed"
        return 1
    fi
}

