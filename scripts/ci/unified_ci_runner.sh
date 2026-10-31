#!/bin/bash
# Run the same quality gates in GitHub Actions, GitLab CI, or locally so results remain comparable.

# Fail on unexpected errors and unset variables; handled stage failures are recorded below for the final report.
set -euo pipefail

# Anchor paths to this file so callers can invoke the runner from any working directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load shared functions in this process so stages can use the same context and status variables.
source "$SCRIPT_DIR/unified/common.sh"
source "$SCRIPT_DIR/unified/quality.sh"
source "$SCRIPT_DIR/unified/tests.sh"
source "$SCRIPT_DIR/unified/summary.sh"

# Run all gates and preserve a failing exit code even though later stages continue for complete diagnostics.
main() {
    # Detect once for the run banner and summary so both identify the same execution environment.
    local platform=$(detect_ci_platform)
    echo "========================================"
    echo "Unified CI Runner"
    echo "Platform: $platform"
    echo "Project Root: $PROJECT_ROOT"
    echo "========================================"
    echo ""

    # Fetch maintained language helpers before tests so a fresh checkout has the same test runners as CI.
    bash "$PROJECT_ROOT/scripts/setup/fetch_language_templates.sh" all
    
    local exit_code=0
    
    # Record failures without stopping early so one CI run reports every actionable stage result.
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
    
    # Generate the report after all stages so it contains their final statuses, including failures.
    generate_summary
    
    echo ""
    echo "========================================"
    # Return a failing process status to CI even after printing the complete summary.
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ ALL STAGES PASSED${NC}"
    else
        echo -e "${RED}❌ SOME STAGES FAILED${NC}"
    fi
    echo "========================================"
    
    exit $exit_code
}

main "$@"
