#!/bin/bash
# Security Policy Engine - Unified security scanning for all supported languages
# Integrates gitleaks, trivy, semgrep with custom policy rules

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REPORT_DIR="$PROJECT_ROOT/reports/security"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$REPORT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install tools if missing (optional)
install_tools() {
    if ! command_exists gitleaks; then
        log_warn "gitleaks not found. Install with: go install github.com/zricethezav/gitleaks/v8@latest"
    fi
    if ! command_exists trivy; then
        log_warn "trivy not found. Install from: https://aquasecurity.github.io/trivy/"
    fi
    if ! command_exists semgrep; then
        log_warn "semgrep not found. Install with: pip install semgrep"
    fi
}

# Run gitleaks for secret detection
run_gitleaks() {
    log_info "Running gitleaks for secret detection..."
    
    if ! command_exists gitleaks; then
        log_warn "Skipping gitleaks - not installed"
        return 0
    fi
    
    local report_file="$REPORT_DIR/gitleaks_${TIMESTAMP}.json"
    
    cd "$PROJECT_ROOT"
    if gitleaks detect --source . --report-path "$report_file" --report-format json 2>/dev/null; then
        log_info "✓ gitleaks: No secrets detected"
        return 0
    else
        log_error "✗ gitleaks: Secrets detected! Check $report_file"
        cat "$report_file" | jq '.[] | {Description: .Description, File: .File, Secret: .Secret}' 2>/dev/null || true
        return 1
    fi
}

# Run trivy for vulnerability scanning
run_trivy() {
    log_info "Running trivy for vulnerability scanning..."
    
    if ! command_exists trivy; then
        log_warn "Skipping trivy - not installed"
        return 0
    fi
    
    local report_file="$REPORT_DIR/trivy_${TIMESTAMP}.json"
    
    cd "$PROJECT_ROOT"
    
    # Scan filesystem for vulnerabilities
    if trivy fs --format json --output "$report_file" --severity HIGH,CRITICAL --exit-code 1 . 2>/dev/null; then
        log_info "✓ trivy: No HIGH/CRITICAL vulnerabilities detected"
        return 0
    else
        log_error "✗ trivy: Vulnerabilities detected! Check $report_file"
        trivy fs --format table --severity HIGH,CRITICAL . 2>/dev/null || true
        return 1
    fi
}

# Run semgrep for static analysis with custom rules
run_semgrep() {
    log_info "Running semgrep for static analysis..."
    
    if ! command_exists semgrep; then
        log_warn "Skipping semgrep - not installed"
        return 0
    fi
    
    local report_file="$REPORT_DIR/semgrep_${TIMESTAMP}.json"
    local config_dir="$SCRIPT_DIR/security_rules"
    
    cd "$PROJECT_ROOT"
    
    # Build semgrep command with custom rules if they exist
    local semgrep_cmd="semgrep --json --output $report_file --error --strict"
    
    if [ -d "$config_dir" ]; then
        semgrep_cmd="$semgrep_cmd --config $config_dir"
        log_info "Using custom security rules from $config_dir"
    fi
    
    # Add language-specific rules
    semgrep_cmd="$semgrep_cmd --config auto"
    
    if eval "$semgrep_cmd" . 2>/dev/null; then
        log_info "✓ semgrep: No issues detected"
        return 0
    else
        log_error "✗ semgrep: Issues detected! Check $report_file"
        eval "semgrep --output text --config auto . 2>/dev/null" | head -50 || true
        return 1
    fi
}

# Custom security policy checks
run_custom_policies() {
    log_info "Running custom security policy checks..."
    
    local policies_failed=0
    
    # Policy 1: Check for hardcoded credentials in config files
    log_info "Checking for hardcoded credentials..."
    if grep -r "password\s*=\s*['\"][^'\"]+['\"]" --include="*.py" --include="*.js" --include="*.ts" --include="*.yaml" --include="*.yml" --include="*.json" "$PROJECT_ROOT" 2>/dev/null | grep -v "test" | grep -v "example" | grep -v ".env.example"; then
        log_error "✗ Policy violated: Hardcoded passwords detected"
        policies_failed=1
    else
        log_info "✓ No hardcoded passwords detected"
    fi
    
    # Policy 2: Check for eval() usage in Python/JS
    log_info "Checking for dangerous eval() usage..."
    if grep -rn "eval(" --include="*.py" --include="*.js" --include="*.ts" "$PROJECT_ROOT/src" 2>/dev/null | grep -v "__eval__" | grep -v "test"; then
        log_warn "⚠ Potential unsafe eval() usage detected - review required"
    else
        log_info "✓ No dangerous eval() usage detected"
    fi
    
    # Policy 3: Check for SQL injection risks
    log_info "Checking for SQL injection risks..."
    if grep -rn "execute.*%s\|execute.*f\"" --include="*.py" "$PROJECT_ROOT/src" 2>/dev/null | head -5; then
        log_warn "⚠ Potential SQL injection risk detected - review required"
    else
        log_info "✓ No obvious SQL injection risks detected"
    fi
    
    # Policy 4: Check for shell injection risks
    log_info "Checking for shell injection risks..."
    if grep -rn "os.system\|subprocess.*shell=True" --include="*.py" "$PROJECT_ROOT/src" 2>/dev/null | head -5; then
        log_warn "⚠ Potential shell injection risk detected - review required"
    else
        log_info "✓ No obvious shell injection risks detected"
    fi
    
    return $policies_failed
}

# Generate unified security report
generate_report() {
    local gitleaks_result=$1
    local trivy_result=$2
    local semgrep_result=$3
    local policies_result=$4
    
    local summary_file="$REPORT_DIR/security_summary_${TIMESTAMP}.md"
    
    cat > "$summary_file" << EOF
# Security Scan Report
**Generated:** $(date -Iseconds)
**Project Root:** $PROJECT_ROOT

## Summary

| Tool | Status |
|------|--------|
| gitleaks | $([ $gitleaks_result -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") |
| trivy | $([ $trivy_result -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") |
| semgrep | $([ $semgrep_result -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") |
| Custom Policies | $([ $policies_result -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") |

## Detailed Reports

- gitleaks: \`$REPORT_DIR/gitleaks_${TIMESTAMP}.json\`
- trivy: \`$REPORT_DIR/trivy_${TIMESTAMP}.json\`
- semgrep: \`$REPORT_DIR/semgrep_${TIMESTAMP}.json\`

## Recommendations

EOF

    if [ $gitleaks_result -ne 0 ]; then
        echo "- 🔴 **CRITICAL**: Remove exposed secrets immediately" >> "$summary_file"
    fi
    if [ $trivy_result -ne 0 ]; then
        echo "- 🔴 **HIGH**: Update vulnerable dependencies" >> "$summary_file"
    fi
    if [ $semgrep_result -ne 0 ]; then
        echo "- 🟡 **MEDIUM**: Fix code quality and security issues" >> "$summary_file"
    fi
    if [ $policies_result -ne 0 ]; then
        echo "- 🟡 **MEDIUM**: Review and fix policy violations" >> "$summary_file"
    fi
    
    log_info "Security report generated: $summary_file"
}

# Main execution
main() {
    log_info "Starting Security Policy Engine..."
    log_info "Project root: $PROJECT_ROOT"
    
    install_tools
    
    local gitleaks_result=0
    local trivy_result=0
    local semgrep_result=0
    local policies_result=0
    
    run_gitleaks || gitleaks_result=1
    run_trivy || trivy_result=1
    run_semgrep || semgrep_result=1
    run_custom_policies || policies_result=1
    
    generate_report $gitleaks_result $trivy_result $semgrep_result $policies_result
    
    local total_failures=$((gitleaks_result + trivy_result + semgrep_result + policies_result))
    
    if [ $total_failures -eq 0 ]; then
        log_info "✅ All security checks passed!"
        exit 0
    else
        log_error "❌ $total_failures security check(s) failed. Review reports in $REPORT_DIR"
        exit 1
    fi
}

main "$@"
