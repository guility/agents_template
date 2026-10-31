#!/usr/bin/env bash
# Fail this job when unit behavior or required line/branch coverage is incomplete.
set -euo pipefail
# Anchor the shared runner path so local and CI invocations behave the same from any directory.
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# Delegate to the common runner so suite selection and coverage rules stay consistent everywhere.
bash "$root/scripts/common/run-test-suite.sh" unit
