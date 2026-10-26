#!/usr/bin/env bash
set -euo pipefail

root="${1:?repository root is required}"
base="${2:?diff base is required}"
head="${3:?diff head is required}"

if ! command -v shellcheck >/dev/null || ! command -v shfmt >/dev/null; then
  echo "The lint image must provide shellcheck and shfmt" >&2
  exit 1
fi

files=()
while IFS= read -r -d '' path; do
  if [[ -f "$root/$path" ]]; then
    files+=("$root/$path")
  fi
done < <(git -C "$root" diff --name-only -z "$base" "$head" -- '*.sh')

if ((${#files[@]} == 0)); then
  exit 0
fi

shellcheck "${files[@]}"
shfmt -i 2 -d "${files[@]}"
