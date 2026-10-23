# Sourced by unified_ci_runner.sh.

# Stage: Contract Validation
run_contract_validation() {
    log_stage "Validating API contracts..."
    
    local contracts_dir="$PROJECT_ROOT/docs/contracts"
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

