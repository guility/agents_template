#!/bin/sh
# Fail closed so missing build artifacts or high-severity findings block publication.
set -eu

# Read the build manifest so scanning covers the exact set that the push job will publish.
root="${CI_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"
manifest="$root/artifacts/images/manifest.tsv"
test -s "$manifest" || { echo "Build image manifest is missing" >&2; exit 1; }

# Keep the delimiter explicit so image names and tags remain separate manifest fields.
tab=$(printf '\t')
while IFS="$tab" read -r name tag; do
  archive="$root/artifacts/images/$name.tar"
  # Refuse to skip an image when the build job failed to preserve its archive.
  test -s "$archive" || { echo "Missing image archive: $archive" >&2; exit 1; }
  # Scan the saved build rather than a mutable registry tag to avoid build/scan drift.
  trivy image --input "$archive" --severity HIGH,CRITICAL --exit-code 1
done < "$manifest"
