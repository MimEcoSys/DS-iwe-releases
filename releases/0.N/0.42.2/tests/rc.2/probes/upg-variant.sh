#!/bin/bash
# usage: upg-variant.sh <label> <kind: plain|userown|retired> <answer: y|none> [update.sh args...]
# Restores the disposable 0.42.1 install from its backup, shapes the workspace settings.json,
# runs the candidate update through the rc channel and reports what happened to settings.json.
set -u
B="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="$1"; KIND="$2"; ANSWER="$3"; shift 3
CASE="$B/upg"; W="$CASE/ws"; S="$W/.claude/settings.json"; LOG="$B/logs/line2-$LABEL.raw.log"
case "$CASE" in */fable-rc2/upg) ;; *) echo "refusing: unexpected case dir"; exit 98 ;; esac
rm -rf "$CASE/ws" "$CASE/home" "$CASE/tmp"
cp -a "$B/upg-backup/ws" "$B/upg-backup/home" "$CASE/"
python3 - "$S" "$KIND" <<'PY'
import json, sys
path, kind = sys.argv[1:3]
data = json.load(open(path, encoding="utf-8"))
if kind == "userown":
    data["hooks"].setdefault("Stop", []).append({"hooks": [{"type": "command", "command": "/my/own/hook.sh"}]})
    data.setdefault("permissions", {}).setdefault("allow", []).append("Bash(my-tool:*)")
if kind == "retired":
    data.setdefault("permissions", {})["defaultMode"] = "acceptEdits"
if kind != "plain":
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
before=$(shasum -a 256 "$S" | cut -c1-16)
{
  echo "### variant=$LABEL kind=$KIND answer=$ANSWER args: IWE_UPDATE_CHANNEL=rc bash update.sh $*"
  echo "### settings.json before: sha=$before memory-write-permission=$(grep -c 'memory-write-permission.sh' "$S") own-hook=$(grep -c '/my/own/hook.sh' "$S") own-permission=$(grep -c 'Bash(my-tool:\*)' "$S") defaultMode=$(jq -r '.permissions.defaultMode' "$S")"
} > "$LOG"
if [ "$ANSWER" = y ]; then
  printf 'y\n' | "$B/tools/run.sh" "$CASE" "$W/FMT-exocortex-template" env IWE_UPDATE_CHANNEL=rc bash update.sh "$@" >> "$LOG" 2>&1
else
  "$B/tools/run.sh" "$CASE" "$W/FMT-exocortex-template" env IWE_UPDATE_CHANNEL=rc bash update.sh "$@" >> "$LOG" 2>&1 </dev/null
fi
rc=$?
after=$(shasum -a 256 "$S" | cut -c1-16)
same=changed; [ "$before" = "$after" ] && same=unchanged
equal=differs; cmp -s "$S" "$W/FMT-exocortex-template/.claude/settings.json" && equal=equal
{
  echo "### exit=$rc"
  echo "### settings.json after: sha=$after ($same) memory-write-permission=$(grep -c 'memory-write-permission.sh' "$S") own-hook=$(grep -c '/my/own/hook.sh' "$S") own-permission=$(grep -c 'Bash(my-tool:\*)' "$S") defaultMode=$(jq -r '.permissions.defaultMode' "$S") vs-candidate-settings=$equal"
  echo "### preview file: $(ls "$W/.claude/" | grep -c 'settings.merged.preview.json') ; backups: $(ls "$W/.claude/" | grep -c 'settings.json.bak')"
  echo "### user edits: ext-ws=$(grep -c 'моя правка' "$W/extensions/test-marker.md") ext-template=$(grep -c 'моя правка' "$W/FMT-exocortex-template/extensions/test-marker.md") params=$(grep -c '^test_marker: keep-me' "$W/params.yaml") memory=$(grep -c 'tester marker line: keep-me' "$W/memory/MEMORY.md") conflict-markers-CLAUDE.md=$(grep -c '^<<<<<<<\|^>>>>>>>' "$W/CLAUDE.md")"
} >> "$LOG"
grep -n '^###\|Канал поставки\|settings\|Применить слияние\|ОШИБКА\|Обновление завершено' "$LOG" | cut -c1-400
