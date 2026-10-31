#!/usr/bin/env bash
# Stop on setup or test errors so required coverage cannot be skipped and still pass.
set -euo pipefail

# Resolve paths from the checkout so local runs and CI use the same template and tests.
root="${CI_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"
language="${1:-${TEST_LANGUAGE:-python}}"
# Reject unsupported languages before installing anything so this runner cannot test the wrong template.
if [[ "$language" != "python" ]]; then
  echo "Unsupported required-test language: $language" >&2
  exit 2
fi

# Fetch the pinned language package so a fresh checkout receives its maintained test configuration.
bash "$root/scripts/setup/fetch_language_templates.sh" "$language"
project_root="$root/src/templates/$language"
# Install the template's locked tools and extras in one isolated environment for reproducible test runs.
uv sync --python 3.14 --all-extras --project "$project_root"
# Make downstream suite runners use the selected language environment and dependencies.
export TEST_LANGUAGE="$language"
export PATH="$project_root/.venv/bin:$PATH"

# Store JUnit output as a CI artifact so test results remain available outside the job log.
mkdir -p "$root/test-results"
"$project_root/.venv/bin/python" -m pytest \
  "$root/src/tests/unit" \
  --junitxml="$root/test-results/repository-unit.xml"

for suite in unit integration mutation e2e; do
  runner="$root/scripts/ci/test-$suite.sh"
  # A missing runner means a required suite was skipped, so fail before claiming a complete test run.
  test -f "$runner" || { echo "Required test runner is missing: $runner" >&2; exit 1; }
  # Keep each suite's checks isolated while propagating its failure to this mandatory job.
  bash "$runner"
done
