#!/bin/bash
# Detect the active CI provider so shared scripts can choose provider-specific behavior reliably.

set -e

detect_platform() {
    # Prefer explicit runner markers because they identify the current execution, not just repository files.
    if [ -n "$GITHUB_ACTIONS" ] && [ "$GITHUB_ACTIONS" = "true" ]; then
        echo "github"
        return 0
    fi
    
    # Check GitLab's marker next for the same reason, before using local repository clues.
    if [ -n "$GITLAB_CI" ] && [ "$GITLAB_CI" = "true" ]; then
        echo "gitlab"
        return 0
    fi
    
    # Infer from workflow directories only when exactly one provider configuration is present.
    if [ -d ".github/workflows" ] && [ ! -d ".gitlab/ci" ]; then
        echo "github"
        return 0
    fi
    
    if [ -d ".gitlab/ci" ] && [ ! -d ".github/workflows" ]; then
        echo "gitlab"
        return 0
    fi
    
    # If both configurations exist, use known origin host markers to break the tie.
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
    
    # Keep local tooling usable when no CI marker or provider-specific repository clue exists.
    echo "github"
    return 0
}

# Export once so downstream helpers share the same detected provider.
export CI_PLATFORM=$(detect_platform)
echo "Detected CI platform: $CI_PLATFORM"

# Resolve shared helpers relative to this script so callers can run from any working directory.
get_common_script() {
    local script_name=$1
    echo "$(dirname "$0")/common/${script_name}"
}

# Reuse common implementations and fail clearly when the requested helper is missing.
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

# Expose CLI status checks only for direct execution; sourcing this file keeps its helpers available.
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
