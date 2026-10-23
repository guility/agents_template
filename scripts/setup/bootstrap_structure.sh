#!/bin/bash
# Project directory structure setup.

# Создание структуры проекта (если пустая)
create_project_structure() {
    if [ ! -d "$PROJECT_ROOT/src" ]; then
        log_step "Creating project structure..."
        
        mkdir -p "$PROJECT_ROOT/src/core/domain"
        mkdir -p "$PROJECT_ROOT/src/core/application"
        mkdir -p "$PROJECT_ROOT/src/core/infrastructure"
        mkdir -p "$PROJECT_ROOT/src/core/interface"
        mkdir -p "$PROJECT_ROOT/deploy/Dockerfiles/tests"
        mkdir -p "$PROJECT_ROOT/deploy/composes/tests"
        mkdir -p "$PROJECT_ROOT/deploy/composes/manual"
        mkdir -p "$PROJECT_ROOT/src/tests/unit"
        mkdir -p "$PROJECT_ROOT/src/tests/integration"
        mkdir -p "$PROJECT_ROOT/src/tests/mutation"
        mkdir -p "$PROJECT_ROOT/src/tests/e2e"
        mkdir -p "$PROJECT_ROOT/docs"
        mkdir -p "$PROJECT_ROOT/docs/contracts"
        
        # Создание .gitkeep файлов
        find "$PROJECT_ROOT/src" "$PROJECT_ROOT/docs" \
            -type d -exec touch {}/.gitkeep \;
        
        log_info "Project structure created"
    fi
}
