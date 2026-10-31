#!/usr/bin/env bash
# Fail this job when an integration path or its required coverage is incomplete.
set -euo pipefail
# Anchor the shared runner path so local and CI invocations behave the same from any directory.
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# Delegate to the common runner so suite selection and reporting stay consistent across entry points.
bash "$root/scripts/common/run-test-suite.sh" integration
