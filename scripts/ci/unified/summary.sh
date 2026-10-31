# Source summary generation into the runner so it can report the final status of every stage.

# Persist a stage report so failures remain diagnosable after CI logs expire.
generate_summary() {
    log_stage "Generating pipeline summary..."
    
    local summary_file="$PROJECT_ROOT/reports/ci_summary_$(date +%Y%m%d_%H%M%S).md"
    # Include the provider so reviewers can distinguish hosted pipeline results from local runs.
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

    # Add a human-readable next step based on recorded statuses for quick triage.
    if grep -q "FAILED\|ERROR" "$summary_file" 2>/dev/null; then
        echo "- 🔴 Review failed stages and fix issues" >> "$summary_file"
    else
        echo "- ✅ All stages passed, ready for deployment" >> "$summary_file"
    fi
    
    echo ""
    log_success "Summary report generated: $summary_file"
}

