#!/usr/bin/env bash
# Collects all repos for SpiralCloudOmega using GitHub CLI.
# Usage: ./scripts/collect-repos-gh.sh
set -euo pipefail

OWNER="${1:-SpiralCloudOmega}"
LIMIT="${LIMIT:-1000}"
OUTPUT_DIR="${OUTPUT_DIR:-repos}"
mkdir -p "$OUTPUT_DIR"

echo "Fetching repos for $OWNER..."
gh repo list "$OWNER" --limit "$LIMIT" \
  --json nameWithOwner,url,isFork,isPrivate,description,primaryLanguage,repositoryTopics,updatedAt,isArchived,diskUsage,visibility \
  > "$OUTPUT_DIR/raw-gh-output.json"

echo "Done. Raw data saved to $OUTPUT_DIR/raw-gh-output.json"
if command -v jq >/dev/null 2>&1; then
  echo "Total repos: $(jq 'length' "$OUTPUT_DIR/raw-gh-output.json")"
else
  python - <<'PY' "$OUTPUT_DIR/raw-gh-output.json"
import json, sys
with open(sys.argv[1]) as fh:
    print(f"Total repos: {len(json.load(fh))}")
PY
fi
