#!/bin/bash
# usage: upg-variant.sh <label> <shape> <answer: y|n|none> [update.sh args...]
# Restores the disposable 0.42.1 install from its backup, shapes the workspace settings file, runs the
# candidate update through the rc channel and reports what happened to the settings file.
# shapes: plain | narrowed | removed | badjson | symlink | private | readonly | ownhooktype
set -u
B="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="$1"; SHAPE="$2"; ANSWER="$3"; shift 3
CASE="$B/upg"; W="$CASE/ws"; SF="$W/.claude/settings.json"; LOG="$B/raw/rt4-$LABEL.raw.log"
case "$CASE" in */fable-rc2/redteam/upg) ;; *) echo "refusing: unexpected case dir"; exit 98 ;; esac
chmod -R u+w "$CASE" 2>/dev/null; rm -rf "$CASE"; cp -a "$B/upg-backup" "$CASE"
python3 - "$SF" "$SHAPE" "$CASE" <<'PY'
import json, os, sys
path, shape, case = sys.argv[1:4]
data = json.load(open(path, encoding="utf-8"))
def entries(event, script):
    return [e for e in data["hooks"][event] if any(script in h.get("command", "") for h in e["hooks"])]
write = True
if shape == "narrowed":
    # the user narrowed the matcher of a platform hook and gave it a timeout of their own
    e = entries("PreToolUse", "secret-file-read-block.sh")[0]
    e["matcher"] = "Read"
    e["hooks"][0]["timeout"] = 7
elif shape == "removed":
    # the user removed a platform hook on purpose
    data["hooks"]["PreToolUse"] = [e for e in data["hooks"]["PreToolUse"] if e not in entries("PreToolUse", "session-open-gate.sh")]
elif shape == "private":
    data.setdefault("env", {})["RT_FAKE_KEY"] = "RT-FAKE-VALUE"
elif shape == "ownhooktype":
    data["hooks"]["PermissionRequest"] = {"note": "user wrote an object where the platform expects a list"}
else:
    write = False
if write:
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
if shape == "badjson":
    text = open(path, encoding="utf-8").read().rstrip()
    open(path, "w", encoding="utf-8").write(text[:-1] + ',\n  // my comment\n}\n')
if shape == "symlink":
    target_dir = os.path.join(case, "dotfiles"); os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, "claude-settings.json")
    os.replace(path, target); os.symlink(target, path)
if shape == "private":
    os.chmod(path, 0o600)
if shape == "readonly":
    os.chmod(path, 0o444)
PY
state() { # one line describing the settings file
  local kind=file; [ -L "$SF" ] && kind="link->$(readlink "$SF" | sed "s#$B#<RT>#")"
  local parse=valid; jq -e . "$SF" >/dev/null 2>&1 || parse=INVALID-JSON
  echo "sha=$(shasum -a 256 "$SF" | cut -c1-12) kind=$kind mode=$(stat -L -f '%Sp' "$SF") json=$parse memory-hook=$(grep -c 'memory-write-permission.sh' "$SF") session-gate=$(grep -c 'session-open-gate.sh' "$SF") secret-read-matcher=$(jq -r '[.hooks.PreToolUse[]? | select(any(.hooks[]?; (.command // "") | test("secret-file-read-block"))) | .matcher] | join(",")' "$SF" 2>/dev/null) secret-read-timeout=$(jq -r '[.hooks.PreToolUse[]? | .hooks[]? | select((.command // "") | test("secret-file-read-block")) | (.timeout // "none")] | join(",")' "$SF" 2>/dev/null) own-key=$(grep -c RT_FAKE_KEY "$SF")"
}
before_sha=$(shasum -a 256 "$SF" | cut -c1-12)
cp "$SF" "$CASE/tmp-settings-before.json" 2>/dev/null
{
  echo "### variant=$LABEL shape=$SHAPE answer=$ANSWER command: IWE_UPDATE_CHANNEL=rc bash update.sh $*"
  echo "### before: $(state)"
} > "$LOG"
case "$ANSWER" in
  y|n) printf '%s\n' "$ANSWER" | "$B/tools/run.sh" "$CASE" "$W/FMT-exocortex-template" env IWE_UPDATE_CHANNEL=rc bash update.sh "$@" >> "$LOG" 2>&1 ;;
  *)   "$B/tools/run.sh" "$CASE" "$W/FMT-exocortex-template" env IWE_UPDATE_CHANNEL=rc bash update.sh "$@" >> "$LOG" 2>&1 </dev/null ;;
esac
rc=$?
after_sha=$(shasum -a 256 "$SF" | cut -c1-12)
same=CHANGED; [ "$before_sha" = "$after_sha" ] && same=unchanged
{
  echo "### exit=$rc"
  echo "### after:  $(state) ($same)"
  echo "### template now: $(git -C "$W/FMT-exocortex-template" describe --tags 2>/dev/null) ; preview file left: $(ls "$W/.claude/" | grep -c 'settings.merged.preview.json') ; stray temp files: $(ls -a "$W/.claude/" | grep -c '^\.settings-preview-')"
  echo "### backups: $(find "$W/.backups/settings-merge" -type f -exec stat -f '%Sp %N' {} \; 2>/dev/null | sed "s#$B#<RT>#" | tr '\n' ' ')"
  if [ "$same" = CHANGED ] && jq -e . "$SF" >/dev/null 2>&1 && jq -e . "$CASE/tmp-settings-before.json" >/dev/null 2>&1; then
    echo "### what changed (hooks summary diff, < before, > after):"
    bash "$B/tools/show-settings.sh" "$CASE/tmp-settings-before.json" "$SF" | sed 's/^/###   /'
  fi
} >> "$LOG"
grep -n '^###\|Канал поставки\|settings\|слияни\|Применить\|ОШИБКА\|Обновление завершено\|Отменено\|ВЕРДИКТ\|ОТКАТ\|подтвердили' "$LOG" | sed "s#$B#<RT>#g" | cut -c1-330
