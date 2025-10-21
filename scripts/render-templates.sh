#!/usr/bin/env bash
set -euo pipefail
OUTDIR="${1:-rendered}"
mkdir -p "$OUTDIR"
: "${AZURE_SUBSCRIPTION_ID:?Please set AZURE_SUBSCRIPTION_ID in env or .env}"
: "${AZURE_RESOURCE_GROUP:?Please set AZURE_RESOURCE_GROUP in env or .env}"

for f in $(git ls-files '*.md' '*.kql' '*.json' 2>/dev/null); do
  dest="$OUTDIR/$f"
  mkdir -p "$(dirname "$dest")"
  sed -e "s|{SUBSCRIPTION_ID}|${AZURE_SUBSCRIPTION_ID}|g" \
      -e "s|{RESOURCE_GROUP}|${AZURE_RESOURCE_GROUP}|g" \
      "$f" > "$dest"
done

echo "Rendered templates to $OUTDIR"
