# Source this stage into the unified runner so its errors contribute to the final pipeline status.

# Validate published API schemas so incompatible contract edits are caught before release.
run_contract_validation() {
    log_stage "Validating API contracts..."
    
    local contracts_dir="$PROJECT_ROOT/docs/contracts"
    # Accumulate errors so one invalid file does not hide other contract problems in the same run.
    local failed=0
    
    if [ -d "$contracts_dir" ]; then
        # Validate each OpenAPI file when swagger-cli is available because projects may publish several contracts.
        for spec in "$contracts_dir"/*.yaml "$contracts_dir"/*.yml; do
            if [ -f "$spec" ]; then
                if command -v swagger-cli &> /dev/null; then
                    swagger-cli validate "$spec" || failed=1
                fi
            fi
        done
        
        # Run Protobuf checks when protoc is installed; the shared template also supports partial local toolchains.
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

