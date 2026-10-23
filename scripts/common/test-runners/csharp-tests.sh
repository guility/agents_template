run_csharp_tests() {
    log_step "Running C# tests..."

    local sln_file
    local project_file
    sln_file=$(find "$ROOT_DIR" -name "*.sln" -print -quit)
    if [ -n "$sln_file" ]; then
        project_file="$sln_file"
    else
        project_file=$(find "$ROOT_DIR" -name "*.csproj" -print -quit)
    fi

    if [ -z "$project_file" ]; then
        log_error "No .sln or .csproj file found; cannot run C# tests"
        return 1
    fi

    if ! command -v dotnet &> /dev/null; then
        log_error "dotnet not found; cannot run C# tests"
        return 1
    fi

    cd "$(dirname "$project_file")" || return 1

    # Запуск тестов с покрытием
    if dotnet test "$project_file" --no-restore --collect:"XPlat Code Coverage" --results-directory "$ROOT_DIR/test-results/csharp" 2>&1 | tee "$ROOT_DIR/test-results/csharp-tests.log"; then
        log_info "C# tests passed"
    else
        log_error "C# tests failed"
        return 1
    fi
}

# Основная функция
