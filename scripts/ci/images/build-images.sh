#!/usr/bin/env bash
set -euo pipefail

root="${CI_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"
dockerfiles="$root/deploy/Dockerfiles"
output="$root/artifacts/images"
context="${DOCKER_CONTEXT:-$root}"
mkdir -p "$output"
: > "$output/manifest.tsv"

while IFS= read -r -d '' dockerfile; do
  file="${dockerfile##*/}"
  name="$file"
  name="${name#Dockerfile}"
  name="${name#.}"
  name="${name%.dockerfile}"
  name="${name:-$CI_PROJECT_PATH_SLUG}"
  name="$(printf '%s' "$name" | sed 's/_/-/g' | tr '[:upper:]' '[:lower:]')"
  tag="$CI_REGISTRY_IMAGE/$name:$CI_COMMIT_SHA"
  archive="$output/$name.tar"
  docker build --pull --file "$dockerfile" --tag "$tag" "$context"
  docker save --output "$archive" "$tag"
  printf '%s\t%s\n' "$name" "$tag" >> "$output/manifest.tsv"
done < <(find "$dockerfiles" -maxdepth 1 -type f \( -name 'Dockerfile*' -o -name '*.dockerfile' \) -print0)

test -s "$output/manifest.tsv" || { echo "No production Dockerfiles found" >&2; exit 1; }
