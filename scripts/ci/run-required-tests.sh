#!/usr/bin/env bash
set -euo pipefail

root="${CI_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"
bash "$root/scripts/setup/fetch_language_templates.sh" all
for suite in unit integration mutation e2e; do
  runner="$root/scripts/ci/test-$suite.sh"
  test -f "$runner" || { echo "Required test runner is missing: $runner" >&2; exit 1; }
  bash "$runner"
done
