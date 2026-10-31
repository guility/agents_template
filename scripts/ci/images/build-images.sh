#!/usr/bin/env bash
# Stop on errors and unset variables so a partial image set cannot be reported as a successful build.
set -euo pipefail

# Resolve CI and local paths from the checkout so every stage uses the same artifact locations.
root="${CI_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"
dockerfiles="$root/deploy/Dockerfiles"
output="$root/artifacts/images"
context="${DOCKER_CONTEXT:-$root}"
# Reset the manifest so later jobs cannot accidentally consume entries from an earlier run.
mkdir -p "$output"
: > "$output/manifest.tsv"

# Discover Dockerfiles once so build, scan, and push stages operate on the same image set.
while IFS= read -r -d '' dockerfile; do
  # Derive names from file names so adding an image does not require a second hand-maintained list.
  file="${dockerfile##*/}"
  name="$file"
  name="${name#Dockerfile}"
  name="${name#.}"
  name="${name%.dockerfile}"
  name="${name:-$CI_PROJECT_PATH_SLUG}"
  # Normalize names to registry-safe lowercase tags with hyphens.
  name="$(printf '%s' "$name" | sed 's/_/-/g' | tr '[:upper:]' '[:lower:]')"
  # Tag the build with its commit so the originating source is visible in the registry.
  tag="$CI_REGISTRY_IMAGE/$name:$CI_COMMIT_SHA"
  archive="$output/$name.tar"
  # Refresh base layers, then archive this exact build for later scan and push jobs.
  docker build --pull --file "$dockerfile" --tag "$tag" "$context"
  docker save --output "$archive" "$tag"
  # Record the tag so downstream jobs do not rebuild a different image set.
  printf '%s\t%s\n' "$name" "$tag" >> "$output/manifest.tsv"
# Use NUL separators so spaces or newlines in Dockerfile paths cannot split a build entry.
done < <(find "$dockerfiles" -maxdepth 1 -type f \( -name 'Dockerfile*' -o -name '*.dockerfile' \) -print0)

# Reject an empty build so a missing Dockerfile cannot make the pipeline pass without doing work.
test -s "$output/manifest.tsv" || { echo "No production Dockerfiles found" >&2; exit 1; }
