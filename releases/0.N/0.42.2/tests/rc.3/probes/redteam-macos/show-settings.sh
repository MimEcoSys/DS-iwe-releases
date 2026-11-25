#!/bin/bash
# usage: show-settings.sh <settings.json> [other settings.json]  — summary of hooks/permissions, optional diff
set -u
A="$1"; B="${2:-}"
summ() {
  jq -r '.hooks | to_entries[] | .key as $e | .value[] | "\($e) | \(.matcher // "-") | \([.hooks[] | (.command // "?") + (if .timeout then " [timeout=\(.timeout)]" else "" end)] | join(" ; "))"' "$1" | sed 's#\$CLAUDE_PROJECT_DIR/.claude/hooks/##g; s#"##g' | cut -c1-230
  echo "permissions keys: $(jq -c '.permissions | keys' "$1"); allow=$(jq '.permissions.allow | length' "$1"); deny=$(jq '(.permissions.deny // []) | length' "$1"); defaultMode=$(jq -r '.permissions.defaultMode // "-"' "$1")"
  echo "top-level keys: $(jq -c 'keys' "$1"); environment keys: $(jq -c '(.["env"] // {}) | keys' "$1")"
}
if [ -n "$B" ]; then diff <(summ "$A") <(summ "$B"); else summ "$A"; fi
