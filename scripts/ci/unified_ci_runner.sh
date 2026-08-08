#!/bin/bash
# Unified CI Runner - Adapts to GitHub Actions or GitLab CI
# Detects platform and runs appropriate pipeline stages

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Detect CI platform
detect_ci_platform() {
    if [ -n "${GITHUB_ACTIONS:-}" ]; then
        echo "github"
    elif [ -n "${GITLAB_CI:-}" ]; then
        echo "gitlab"
    else
        echo "local"
    fi
}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_stage() {
    echo -e "${BLUE}[STAGE]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Stage: Security Scanning
run_security_scan() {
    log_stage "Running security scans..."
    
    if [ -f "$SCRIPTS_DIR/security/security_engine.sh" ]; then
        bash "$SCRIPTS_DIR/security/security_engine.sh"
        log_success "Security scans completed"
    else
        log_warn "Security engine not found, skipping"
    fi
}

# Stage: Complexity Analysis
run_complexity_analysis() {
    log_stage "Running complexity analysis..."
    
    if command -v python3 &> /dev/null; then
        python3 "$SCRIPTS_DIR/testing/complexity_analyzer.py" --root "$PROJECT_ROOT" --max-complexity 10
        log_success "Complexity analysis completed"
    else
        log_warn "Python3 not available, skipping complexity analysis"
    fi
}

# Stage: Unit Tests
run_unit_tests() {
    log_stage "Running unit tests..."
    
    local test_dirs=("tests/unit" "src/**/tests")
    local failed=0
    
    for test_dir in "${test_dirs[@]}"; do
        if [ -d "$PROJECT_ROOT/$test_dir" ]; then
            # Python tests
            if [ -d "$PROJECT_ROOT/tests/unit/python" ] || [ -d "$PROJECT_ROOT/src/tests/unit" ]; then
                if command -v pytest &> /dev/null; then
                    pytest "$PROJECT_ROOT/tests/unit" --cov=src --cov-report=xml --cov-fail-under=100 || failed=1
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

# Stage: Integration Tests
run_integration_tests() {
    log_stage "Running integration tests..."
    
    local failed=0
    
    # Python integration tests
    if [ -d "$PROJECT_ROOT/tests/integration" ]; then
        if command -v pytest &> /dev/null; then
            pytest "$PROJECT_ROOT/tests/integration" --cov=src --cov-append || failed=1
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
        go test ./tests/integration/... || failed=1
    fi
    
    if [ $failed -eq 0 ]; then
        log_success "Integration tests passed"
    else
        log_error "Integration tests failed"
        return 1
    fi
}

# Stage: E2E Tests
run_e2e_tests() {
    log_stage "Running e2e tests..."
    
    local failed=0
    
    # Python e2e tests
    if [ -d "$PROJECT_ROOT/tests/e2e" ]; then
        if command -v pytest &> /dev/null; then
            pytest "$PROJECT_ROOT/tests/e2e" || failed=1
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

# Stage: Contract Validation
run_contract_validation() {
    log_stage "Validating API contracts..."
    
    local contracts_dir="$PROJECT_ROOT/contracts"
    local failed=0
    
    if [ -d "$contracts_dir" ]; then
        # Validate OpenAPI specs
        for spec in "$contracts_dir"/*.yaml "$contracts_dir"/*.yml; do
            if [ -f "$spec" ]; then
                if command -v swagger-cli &> /dev/null; then
                    swagger-cli validate "$spec" || failed=1
                fi
            fi
        done
        
        # Validate Protobuf specs
        for proto in "$contracts_dir"/*.proto; do
            if [ -f "$proto" ]; then
                if command -v protoc &> /dev/null; then
                    protoc --proto_path="$contracts_dir" --decode_raw < "$proto" >/dev/null 2>&1 || failed=1
                fi
            fi
        done
    fi
    
    if [ $failed -eq 0 ]; then
        log_success "Contract validation passed"
    else
        log_error "Contract validation failed"
        return 1
    fi
}

# Stage: Generate Summary Report
generate_summary() {
    log_stage "Generating pipeline summary..."
    
    local summary_file="$PROJECT_ROOT/reports/ci_summary_$(date +%Y%m%d_%H%M%S).md"
    local platform=$(detect_ci_platform)
    
    cat > "$summary_file" << EOF
# CI Pipeline Summary

**Platform:** $platform
**Timestamp:** $(date -Iseconds)
**Commit:** ${GITHUB_SHA:-${CI_COMMIT_SHA:-unknown}}
**Branch:** ${GITHUB_REF_NAME:-${CI_COMMIT_REF_NAME:-unknown}}

## Pipeline Stages

| Stage | Status |
|-------|--------|
| Security Scan | ${SECURITY_STATUS:-pending} |
| Complexity Analysis | ${COMPLEXITY_STATUS:-pending} |
| Unit Tests | ${UNIT_TESTS_STATUS:-pending} |
| Integration Tests | ${INTEGRATION_TESTS_STATUS:-pending} |
| E2E Tests | ${E2E_TESTS_STATUS:-pending} |
| Mutation Tests | ${MUTATION_TESTS_STATUS:-pending} |
| Traceability Check | ${TRACEABILITY_STATUS:-pending} |
| Contract Validation | ${CONTRACT_STATUS:-pending} |

## Artifacts

- Security Reports: \`$PROJECT_ROOT/reports/security/\`
- Test Reports: \`$PROJECT_ROOT/reports/testing/\`
- Complexity Reports: \`$PROJECT_ROOT/reports/complexity/\`
- Contract Reports: \`$PROJECT_ROOT/reports/contracts/\`

## Next Steps

EOF

    if grep -q "FAILED\|ERROR" "$summary_file" 2>/dev/null; then
        echo "- 🔴 Review failed stages and fix issues" >> "$summary_file"
    else
        echo "- ✅ All stages passed, ready for deployment" >> "$summary_file"
    fi
    
    echo ""
    log_success "Summary report generated: $summary_file"
}

# Main execution
main() {
    local platform=$(detect_ci_platform)
    echo "========================================"
    echo "Unified CI Runner"
    echo "Platform: $platform"
    echo "Project Root: $PROJECT_ROOT"
    echo "========================================"
    echo ""
    
    local exit_code=0
    
    # Run all stages with error tracking
    run_security_scan || { SECURITY_STATUS="❌ FAILED"; exit_code=1; } || true
    SECURITY_STATUS="${SECURITY_STATUS:-✅ PASSED}"
    
    run_complexity_analysis || { COMPLEXITY_STATUS="❌ FAILED"; exit_code=1; } || true
    COMPLEXITY_STATUS="${COMPLEXITY_STATUS:-✅ PASSED}"
    
    run_unit_tests || { UNIT_TESTS_STATUS="❌ FAILED"; exit_code=1; } || true
    UNIT_TESTS_STATUS="${UNIT_TESTS_STATUS:-✅ PASSED}"
    
    run_integration_tests || { INTEGRATION_TESTS_STATUS="❌ FAILED"; exit_code=1; } || true
    INTEGRATION_TESTS_STATUS="${INTEGRATION_TESTS_STATUS:-✅ PASSED}"
    
    run_e2e_tests || { E2E_TESTS_STATUS="❌ FAILED"; exit_code=1; } || true
    E2E_TESTS_STATUS="${E2E_TESTS_STATUS:-✅ PASSED}"
    
    run_mutation_tests || { MUTATION_TESTS_STATUS="❌ FAILED"; exit_code=1; } || true
    MUTATION_TESTS_STATUS="${MUTATION_TESTS_STATUS:-✅ PASSED}"
    
    run_traceability_check || { TRACEABILITY_STATUS="❌ FAILED"; exit_code=1; } || true
    TRACEABILITY_STATUS="${TRACEABILITY_STATUS:-✅ PASSED}"
    
    run_contract_validation || { CONTRACT_STATUS="❌ FAILED"; exit_code=1; } || true
    CONTRACT_STATUS="${CONTRACT_STATUS:-✅ PASSED}"
    
    generate_summary
    
    echo ""
    echo "========================================"
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ ALL STAGES PASSED${NC}"
    else
        echo -e "${RED}❌ SOME STAGES FAILED${NC}"
    fi
    echo "========================================"
    
    exit $exit_code
}

main "$@"
