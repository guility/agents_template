# Source quality stages into the unified runner so their failures share its summary and exit code.

# Find known security issues before a change can move toward build or deployment.
run_security_scan() {
    log_stage "Running security scans..."
    
    if [ -f "$SCRIPTS_DIR/security/security_engine.sh" ]; then
        bash "$SCRIPTS_DIR/security/security_engine.sh"
        log_success "Security scans completed"
    else
        # Keep the common template usable by projects that have not adopted this optional engine yet.
        log_warn "Security engine not found, skipping"
    fi
}

# Flag overly complex code early so it can be simplified before review and release.
run_complexity_analysis() {
    log_stage "Running complexity analysis..."
    
    if command -v python3 &> /dev/null; then
        python3 "$SCRIPTS_DIR/testing/complexity_analyzer.py" --root "$PROJECT_ROOT" --max-complexity 10
        log_success "Complexity analysis completed"
    else
        # The analyzer needs Python, so report the unavailable prerequisite instead of running nothing silently.
        log_warn "Python3 not available, skipping complexity analysis"
    fi
}

