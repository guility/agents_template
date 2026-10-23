#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
repository="https://github.com/guility/agents-template-langs.git"
requested="${1:-all}"
if [[ "$requested" == all ]]; then
  languages=(python nodejs rust go csharp)
else
  case "$requested" in
    python|nodejs|rust|go|csharp) languages=("$requested") ;;
    *) echo "Usage: $0 {python|nodejs|rust|go|csharp|all}" >&2; exit 2 ;;
  esac
fi

cache="$(mktemp -d)"
trap 'rm -rf "$cache"' EXIT
for language in "${languages[@]}"; do
  case "$language" in
    python) tag=python-v1.0.1 ;;
    nodejs) tag=nodejs-v1.0.1 ;;
    rust) tag=rust-v1.0.1 ;;
    go) tag=go-v1.0.1 ;;
    csharp) tag=csharp-v1.0.2 ;;
  esac
  git clone --quiet --depth 1 --branch "$tag" "$repository" "$cache/$language"
  destination="$root/src/templates/$language"
  mkdir -p "$destination"
  cp -a "$cache/$language/template/." "$destination/"
done
