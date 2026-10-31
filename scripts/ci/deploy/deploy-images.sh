#!/bin/sh
# Fail closed so deployment cannot start with incomplete image references or missing configuration.
set -eu

# Use immutable refs produced after scanning so deploy cannot silently resolve a changed tag.
refs="${CI_PROJECT_DIR:?}/artifacts/registry-image-refs.txt"
# Treat missing artifacts or deployment configuration as errors instead of skipping the release.
test -s "$refs" || { echo "Registry image digest list is missing" >&2; exit 1; }
test -n "${DEPLOY_COMMAND:-}" || { echo "Set DEPLOY_COMMAND as a protected CI variable" >&2; exit 1; }
# Expose both file and text forms so existing deployment commands can consume refs without rewriting them.
export REGISTRY_IMAGE_REFS_FILE="$refs"
export REGISTRY_IMAGE_REFS="$(cat "$refs")"
# Run the protected deployment command and preserve its exit status for the pipeline gate.
sh -lc "$DEPLOY_COMMAND"
