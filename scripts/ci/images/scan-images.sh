#!/usr/bin/env bash
set -euo pipefail

root="${CI_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"
manifest="$root/artifacts/images/manifest.tsv"
test -s "$manifest" || { echo "Build image manifest is missing" >&2; exit 1; }

while IFS=$'\t' read -r name tag; do
  archive="$root/artifacts/images/$name.tar"
  test -s "$archive" || { echo "Missing image archive: $archive" >&2; exit 1; }
  trivy image --input "$archive" --severity HIGH,CRITICAL --exit-code 1
done < "$manifest"
