#!/bin/bash
# detect-ci-platform.sh - Определяет платформу CI/CD (GitHub или GitLab)

set -e

detect_platform() {
    # Проверка переменных окружения GitHub Actions
    if [ -n "$GITHUB_ACTIONS" ] && [ "$GITHUB_ACTIONS" = "true" ]; then
        echo "github"
        return 0
    fi
    
    # Проверка переменных окружения GitLab CI
    if [ -n "$GITLAB_CI" ] && [ "$GITLAB_CI" = "true" ]; then
        echo "gitlab"
        return 0
    fi
    
    # Проверка наличия директорий как fallback
    if [ -d ".github/workflows" ] && [ ! -d ".gitlab/ci" ]; then
        echo "github"
        return 0
    fi
    
    if [ -d ".gitlab/ci" ] && [ ! -d ".github/workflows" ]; then
        echo "gitlab"
        return 0
    fi
    
    # Если обе директории существуют, проверяем наличие remote
    if [ -d ".git" ]; then
        REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
        
        if echo "$REMOTE_URL" | grep -q "github.com"; then
            echo "github"
            return 0
        fi
        
        if echo "$REMOTE_URL" | grep -q "gitlab.com"; then
            echo "gitlab"
            return 0
        fi
    fi
    
    # По умолчанию возвращаем github
    echo "github"
    return 0
}

# Экспорт переменной для использования в других скриптах
export CI_PLATFORM=$(detect_platform)
echo "Detected CI platform: $CI_PLATFORM"

# Функция для получения пути к скриптам common
get_common_script() {
    local script_name=$1
    echo "$(dirname "$0")/common/${script_name}"
}

# Функция для запуска общего скрипта
run_common() {
    local script_name=$1
    shift
    local script_path=$(get_common_script "$script_name")
    
    if [ -f "$script_path" ]; then
        bash "$script_path" "$@"
    else
        echo "Error: Common script '$script_name' not found at $script_path"
        exit 1
    fi
}

# Если скрипт вызывается напрямую, выводим платформу
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    case "${1:-}" in
        --platform)
            echo "$CI_PLATFORM"
            ;;
        --github)
            [ "$CI_PLATFORM" = "github" ] && exit 0 || exit 1
            ;;
        --gitlab)
            [ "$CI_PLATFORM" = "gitlab" ] && exit 0 || exit 1
            ;;
        *)
            echo "Usage: $0 [--platform|--github|--gitlab]"
            echo "Current platform: $CI_PLATFORM"
            ;;
    esac
fi
