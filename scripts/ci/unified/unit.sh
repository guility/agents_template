# Source this stage into the unified runner so unit failures appear in the common status report.

# Test isolated behavior first so failures are easier to locate than failures in full workflows.
run_unit_tests() {
    log_stage "Running unit tests..."
    
    # Use conventional test roots to determine whether this checkout has a unit suite to run.
    local test_dirs=("src/tests/unit" "src/templates/**/tests")
    # Continue through each installed language runner to expose all unit failures in one CI pass.
    local failed=0
    
    for test_dir in "${test_dirs[@]}"; do
        if [ -d "$PROJECT_ROOT/$test_dir" ]; then
            # Run repository Python tests only when the test tree and pytest tool are both available.
            if [ -d "$PROJECT_ROOT/src/tests/unit/python" ] || [ -d "$PROJECT_ROOT/src/tests/unit" ]; then
                if command -v pytest &> /dev/null; then
                    pytest "$PROJECT_ROOT/src/tests/unit" --cov=src --cov-report=xml --cov-fail-under=100 || failed=1
                fi
            fi
            
            # Use one installed package manager so projects do not need both pnpm and npm.
            if [ -f "$PROJECT_ROOT/package.json" ]; then
                if command -v pnpm &> /dev/null; then
                    pnpm test:unit || failed=1
                elif command -v npm &> /dev/null; then
                    npm run test:unit || failed=1
                fi
            fi
            
            # Test the library target because it contains unit behavior without integration fixtures.
            if [ -f "$PROJECT_ROOT/Cargo.toml" ]; then
                cargo test --lib || failed=1
            fi
            
            # Produce Go coverage data during the unit run for later reporting.
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

