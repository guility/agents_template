#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
base="${CI_MERGE_REQUEST_DIFF_BASE_SHA:?CI_MERGE_REQUEST_DIFF_BASE_SHA is required}"
head="${CI_COMMIT_SHA:?CI_COMMIT_SHA is required}"

git -C "$root" diff --check "$base" "$head"

shopt -s nullglob
linters=("$root"/scripts/ci/lint-*.sh)
if ((${#linters[@]} == 0)); then
  echo "No language-specific lint scripts found in scripts/ci/lint-*.sh" >&2
  exit 1
fi

for linter in "${linters[@]}"; do
  bash "$linter" "$root" "$base" "$head"
done
