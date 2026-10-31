#!/usr/bin/env bash
# Fail this job when the mutation suite is incomplete or tests fail to catch required changes.
set -euo pipefail
# Anchor the shared runner path so local and CI invocations behave the same from any directory.
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# Delegate to the common runner so mutation thresholds and reports are applied uniformly.
bash "$root/scripts/common/run-test-suite.sh" mutation
