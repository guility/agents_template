# Sourced by unified_ci_runner.sh.

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

