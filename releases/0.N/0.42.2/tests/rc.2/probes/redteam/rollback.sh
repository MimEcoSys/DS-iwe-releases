#!/bin/bash
# usage: rollback.sh
# 0.42.1 install with the user's own edits -> candidate (rc channel, answer y) -> ordinary channel, where the
# newest release is still 0.42.1: first without confirmation, then with a wrong word, then with ROLLBACK.
set -u
B="$(cd "$(dirname "$0")/.." && pwd)"
CASE="$B/upg"; W="$CASE/ws"; T="$W/FMT-exocortex-template"; SF="$W/.claude/settings.json"
case "$CASE" in */fable-rc2/redteam/upg) ;; *) echo "refusing: unexpected case dir"; exit 98 ;; esac
chmod -R u+w "$CASE" 2>/dev/null; rm -rf "$CASE"; cp -a "$B/upg-backup" "$CASE"
mask() { sed "s#$B#<RT>#g"; }
# the user's own edits and settings
mkdir -p "$W/extensions"; echo "my edit: keep-me" > "$W/extensions/rt-marker.md"
echo "rt_marker: keep-me" >> "$W/params.yaml"
echo "tester marker line: keep-me" >> "$W/memory/MEMORY.md"
python3 - "$SF" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p, encoding="utf-8"))
d["hooks"].setdefault("Stop", []).append({"hooks": [{"type": "command", "command": "/my/own/hook.sh"}]})
d.setdefault("permissions", {}).setdefault("allow", []).append("Bash(my-tool:*)")
json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
snap() { # hashes of everything in the workspace except git internals and runtime marks
  ( cd "$W" && find . -type f -not -path '*/.git/*' -not -path './.iwe-runtime/*' -not -path './logs/*' -print0 | sort -z | xargs -0 shasum -a 256 ) > "$1" 2>/dev/null
}
state() {
  echo "template=$(git -C "$T" describe --tags 2>/dev/null) memory-hook-registered=$(grep -c 'memory-write-permission.sh' "$SF") memory-hook-file=$([ -f "$W/.claude/hooks/memory-write-permission.sh" ] && echo present || echo absent) own-hook=$(grep -c '/my/own/hook.sh' "$SF") own-permission=$(grep -c 'Bash(my-tool' "$SF") settings-json=$(jq -e . "$SF" >/dev/null 2>&1 && echo valid || echo INVALID) ext=$(grep -c keep-me "$W/extensions/rt-marker.md" 2>/dev/null) params=$(grep -c '^rt_marker: keep-me' "$W/params.yaml") memory=$(grep -c 'tester marker line: keep-me' "$W/memory/MEMORY.md") conflict-markers=$(grep -c '^<<<<<<<\|^>>>>>>>' "$W/CLAUDE.md")"
}
step() { # step <label> <stdin text or -> <env assignment or -> [update args]
  local label="$1" input="$2" envv="$3"; shift 3
  local log="$B/raw/rt5-rollback-$label.raw.log"
  { echo "### step=$label input=$([ "$input" = - ] && echo none || echo "$input") command: ${envv#-} bash update.sh $*"; echo "### before: $(state)"; } > "$log"
  snap "$CASE/snap-before-$label.txt"
  if [ "$input" = - ]; then
    "$B/tools/run.sh" "$CASE" "$T" env ${envv#-} bash update.sh "$@" >> "$log" 2>&1 </dev/null
  else
    printf '%s\n' "$input" | "$B/tools/run.sh" "$CASE" "$T" env ${envv#-} bash update.sh "$@" >> "$log" 2>&1
  fi
  local rc=$?
  snap "$CASE/snap-after-$label.txt"
  { echo "### exit=$rc"; echo "### after:  $(state)"
    echo "### workspace files changed by this step: $(diff "$CASE/snap-before-$label.txt" "$CASE/snap-after-$label.txt" | grep -c '^[<>]')"
    diff "$CASE/snap-before-$label.txt" "$CASE/snap-after-$label.txt" | grep '^[<>]' | awk '{print $1, $3}' | sort -u -k2 | head -12 | sed 's/^/###   /'
  } >> "$log"
  echo "=========== $label"
  grep -n '^###\|Канал поставки\|ОТКАТ\|откат\|Отменено\|ВЕРДИКТ\|ROLLBACK\|settings\|слияни\|ОШИБКА\|Обновление завершено\|подтвердили\|Останов' "$log" | mask | cut -c1-360
}
step 1-to-candidate        y        IWE_UPDATE_CHANNEL=rc
step 2-back-check          -        -                     --check
step 3-back-no-answer      -        -
step 4-back-answer-y       y        -
step 5-back-yes-flag       -        -                     --yes
step 6-back-ROLLBACK       ROLLBACK -
step 7-after-rollback-again -       -
