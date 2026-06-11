#!/usr/bin/env bash
# Resize all PNGs under a directory to 256x256 in place (macOS sips, no deps).
# Usage: bash scripts/resize-pngs.sh [dir]   (default: public/candidates)
set -euo pipefail

dir="${1:-public/candidates}"

if [[ ! -d "$dir" ]]; then
  echo "error: directory not found: $dir" >&2
  exit 1
fi

count=0
while IFS= read -r -d '' png; do
  sips -z 256 256 "$png" --out "$png" >/dev/null
  count=$((count + 1))
done < <(find "$dir" -type f -name "*.png" -print0)

echo "resized $count PNGs in $dir to 256x256"
du -sh "$dir"
