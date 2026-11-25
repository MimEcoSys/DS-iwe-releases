#!/bin/bash
# usage: line1-checks.sh — update --check (default and rc channel), setup --validate and hook registration on the clean install
B="$(cd "$(dirname "$0")/.." && pwd)"; W="$B/live/ws"; F="$W/FMT-exocortex-template"
r() { "$B/tools/run-deps.sh" "$B/live" "$F" bash -c "$1; echo \"### exit=\$?\""; }
r 'bash update.sh --check' > "$B/logs/line1-update-check.raw.log" 2>&1
r 'IWE_UPDATE_CHANNEL=rc bash update.sh --check' > "$B/logs/line1-update-check-rc.raw.log" 2>&1
r 'bash setup.sh --validate' > "$B/logs/line1-setup-validate.raw.log" 2>&1
{
  echo "== PermissionRequest hooks registered in the workspace .claude/settings.json"
  jq -c '.hooks.PermissionRequest' "$W/.claude/settings.json"
  echo "== installed hook files equal the candidate tag"
  for h in memory-write-permission.sh session-open-gate.sh; do
    a=$(git -C "$B/src/FMT" rev-parse "v0.42.2-rc.4:.claude/hooks/$h"); b=$(git hash-object "$W/.claude/hooks/$h")
    echo "$h tag=$a installed=$b $([ "$a" = "$b" ] && echo same || echo DIFFERENT)"
  done
} > "$B/logs/line1-hook-registered.raw.log" 2>&1
for f in line1-update-check line1-update-check-rc line1-setup-validate; do echo "== $f"; grep -n 'ВЕРДИКТ\|актуально\|Канал\|Валидация\|### exit\|ОШИБКА' "$B/logs/$f.raw.log" | cut -c1-200; done
cat "$B/logs/line1-hook-registered.raw.log"
