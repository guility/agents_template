#!/bin/sh
set -eu

refs="${CI_PROJECT_DIR:?}/artifacts/registry-image-refs.txt"
test -s "$refs" || { echo "Registry image digest list is missing" >&2; exit 1; }
test -n "${DEPLOY_COMMAND:-}" || { echo "Set DEPLOY_COMMAND as a protected CI variable" >&2; exit 1; }
export REGISTRY_IMAGE_REFS_FILE="$refs"
export REGISTRY_IMAGE_REFS="$(cat "$refs")"
sh -lc "$DEPLOY_COMMAND"
