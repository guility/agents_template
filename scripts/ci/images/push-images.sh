#!/usr/bin/env bash
set -euo pipefail

root="${CI_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"
manifest="$root/artifacts/images/manifest.tsv"
refs="$root/artifacts/registry-image-refs.txt"
test -s "$manifest" || { echo "Build image manifest is missing" >&2; exit 1; }
printf '%s\n' "$CI_REGISTRY_PASSWORD" | docker login "$CI_REGISTRY" \
  --username "$CI_REGISTRY_USER" --password-stdin
: > "$refs"

while IFS=$'\t' read -r name tag; do
  docker load --input "$root/artifacts/images/$name.tar"
  output="$(docker push "$tag")"
  digest="$(printf '%s\n' "$output" | sed -n 's/.*digest: \(sha256:[0-9a-f]*\).*/\1/p' | tail -1)"
  test -n "$digest" || { echo "Registry did not return a digest for $tag" >&2; exit 1; }
  printf '%s/%s@%s\n' "$CI_REGISTRY_IMAGE" "$name" "$digest" >> "$refs"
done < "$manifest"
