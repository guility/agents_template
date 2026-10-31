# Source shared helpers into the runner so every stage uses the same provider, colors, and log format.

# Identify the runner context so reports distinguish hosted CI from local checks.
detect_ci_platform() {
    if [ -n "${GITHUB_ACTIONS:-}" ]; then
        echo "github"
    elif [ -n "${GITLAB_CI:-}" ]; then
        echo "gitlab"
    else
        echo "local"
    fi
}

# Use color only to make human-readable logs scannable; job status still comes from exit codes.
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_stage() {
    echo -e "${BLUE}[STAGE]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

