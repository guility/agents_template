#!/usr/bin/env bash
set -euo pipefail

root="${CI_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"
language="${1:-${TEST_LANGUAGE:-python}}"
if [[ "$language" != "python" ]]; then
  echo "Unsupported required-test language: $language" >&2
  exit 2
fi

bash "$root/scripts/setup/fetch_language_templates.sh" "$language"
project_root="$root/src/templates/$language"
uv sync --python 3.14 --all-extras --project "$project_root"
export TEST_LANGUAGE="$language"
export PATH="$project_root/.venv/bin:$PATH"

mkdir -p "$root/test-results"
"$project_root/.venv/bin/python" -m pytest \
  "$root/src/tests/unit" \
  --junitxml="$root/test-results/repository-unit.xml"

for suite in unit integration mutation e2e; do
  runner="$root/scripts/ci/test-$suite.sh"
  test -f "$runner" || { echo "Required test runner is missing: $runner" >&2; exit 1; }
  bash "$runner"
done
