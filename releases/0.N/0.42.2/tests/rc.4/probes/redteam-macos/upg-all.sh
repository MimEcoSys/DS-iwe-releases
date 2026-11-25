#!/bin/bash
# usage: upg-all.sh   — waits for the anonymous GitHub API quota, then: two key update variants, the
# rollback sequence with a live run after it, the file modes after rollback, the remaining variants.
set -u
RT="$(cd "$(dirname "$0")/.." && pwd)"
until [ "$(curl -s https://api.github.com/rate_limit | jq -r '.resources.core.remaining')" -gt 40 ] 2>/dev/null; do /bin/sleep 60; done
bash "$RT/tools/upg-batch.sh" "$RT/raw/rt4-variants-summary.txt" "y-plain plain y" "y-narrowed narrowed y"
bash "$RT/tools/rollback.sh" > "$RT/raw/rt5-rollback-summary.txt" 2>&1
bash "$RT/tools/probe-permissions.sh" "$RT/upg" > "$RT/logs/rt5-permissions-after-rollback.txt" 2>&1
bash "$RT/tools/live-run.sh" upg rt5-live-after-rollback-acceptEdits acceptEdits l6-after-rollback.txt > /dev/null 2>&1
bash "$RT/tools/upg-batch.sh" "$RT/raw/rt4-variants-summary-2.txt" "y-removed removed y" "check-plain plain none --check" "n-plain plain n" \
  "y-badjson badjson y" "y-symlink symlink y" "y-private private y" "y-readonly readonly y" "y-ownhooktype ownhooktype y" \
  "yes-plain plain none --yes" "y-nomerge narrowed y --no-settings-merge"
echo "quota left: $(curl -s https://api.github.com/rate_limit | jq -r '.resources.core.remaining')"
