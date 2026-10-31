#!/usr/bin/env bash
# Stop on errors so a partial registry push cannot produce a deployable result.
set -euo pipefail

# Reuse the build manifest to publish only the images already scanned by the earlier stage.
root="${CI_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"
manifest="$root/artifacts/images/manifest.tsv"
refs="$root/artifacts/registry-image-refs.txt"
test -s "$manifest" || { echo "Build image manifest is missing" >&2; exit 1; }
# Send credentials over stdin so the registry password does not appear in the process arguments.
printf '%s\n' "$CI_REGISTRY_PASSWORD" | docker login "$CI_REGISTRY" \
  --username "$CI_REGISTRY_USER" --password-stdin
# Start a fresh ref list to prevent stale digests from a previous run reaching deploy.
: > "$refs"

# Publish each saved build; rebuilding here could make the pushed image differ from the scanned one.
while IFS=$'\t' read -r name tag; do
  # Load the archive because CI jobs may use separate Docker daemons.
  docker load --input "$root/artifacts/images/$name.tar"
  output="$(docker push "$tag")"
  # Capture the registry digest so later jobs can address immutable content.
  digest="$(printf '%s\n' "$output" | sed -n 's/.*digest: \(sha256:[0-9a-f]*\).*/\1/p' | tail -1)"
  # Fail instead of falling back to a mutable tag if the registry did not confirm the digest.
  test -n "$digest" || { echo "Registry did not return a digest for $tag" >&2; exit 1; }
  # Pass immutable refs to scanning and deployment so both stages use the pushed image bytes.
  printf '%s/%s@%s\n' "$CI_REGISTRY_IMAGE" "$name" "$digest" >> "$refs"
done < "$manifest"
