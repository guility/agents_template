#!/usr/bin/env bash
set -euo pipefail

suite="${1:?Usage: run-test-suite.sh unit|integration|mutation|e2e}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
found=0

for project_root in "$root"/src/templates/*; do
  [[ -d "$project_root" ]] || continue
  language="${project_root##*/}"
  [[ -z "${TEST_LANGUAGE:-}" || "$language" == "$TEST_LANGUAGE" ]] || continue
  test_dir="$project_root/tests/$suite"
  [[ -d "$test_dir" ]] || continue
  if ! find "$test_dir" -type f ! -name '__init__.py' ! -name '.gitkeep' -print -quit | grep -q .; then
    continue
  fi
  PROJECT_ROOT="$project_root" TEST_SUITE="$suite" bash "$root/scripts/common/run-tests.sh"
  found=$((found + 1))
done

if [[ "$found" -eq 0 ]]; then
  echo "No non-empty $suite test suite found in src/templates" >&2
  exit 1
fi
