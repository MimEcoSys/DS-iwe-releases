#!/usr/bin/env bash
# Independent re-check of the subagent's P1 findings. Runs only inside a fresh
# mktemp fixture; feeds synthetic PreToolUse JSON to the candidate's real hook.
set -u
SRC=/home/iwe-test/IWE/FMT-exocortex-template
TAG="${1:-v0.42.0-rc.2}"
FIX=$(mktemp -d /tmp/rt-verify.XXXXXX)
mkdir -p "$FIX/ws"
git -C "$SRC" archive "$TAG" | tar -x -C "$FIX/ws"
HOOK="$FIX/ws/.claude/hooks/destructive-guard.sh"
probe() {
  local cmd="$1" payload rc
  payload=$(python3 -c 'import json,sys;print(json.dumps({"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":sys.argv[1]},"cwd":sys.argv[2]}))' "$cmd" "$FIX/ws")
  printf '%s' "$payload" | env -i PATH="$PATH" HOME="$FIX" CLAUDE_PROJECT_DIR="$FIX/ws" bash "$HOOK" >/dev/null 2>&1
  rc=$?
  printf '%-4s %s\n' "$rc" "$cmd"
}
echo "== $TAG destructive-guard (2 = blocked, 0 = allowed)"
probe "rm -rf $FIX/victim"
probe "find $FIX/victim -exec rm -f {} +"
probe "find $FIX/victim -type f -exec env rm {} +"
probe "find $FIX/victim -type f -print0 | xargs -0 rm"
probe "TMPDIR=$FIX/home $FIX/ws/.claude/bin/guarded-rm -rf $FIX/home/IWE"
probe "git diff --output=.claude/hooks/destructive-guard.sh"
probe "find .claude/hooks -maxdepth 0 -fprint .claude/hooks/secret-leak-block.sh"
probe "git add --al"
probe "git add :/"

echo "== guarded-rm path validation with a hostile TMPDIR (dry: target is a fixture dir)"
mkdir -p "$FIX/home/IWE/sub"; echo keep > "$FIX/home/IWE/sub/f"
# Work around NixOS lacking /usr/bin/rm only in a private copy (finding F9).
sed "s#/usr/bin/rm#$(command -v rm)#g; s#/bin/rm#$(command -v rm)#g" "$FIX/ws/.claude/bin/guarded-rm" > "$FIX/guarded-rm-nix"
chmod +x "$FIX/guarded-rm-nix"; mkdir -p "$FIX/ws/.claude/bin2"; cp "$FIX/guarded-rm-nix" "$FIX/ws/.claude/bin2/guarded-rm"
( cd "$FIX/ws" && env -i PATH="$PATH" HOME="$FIX" bash .claude/bin2/guarded-rm -rf "$FIX/home/IWE" ) >/dev/null 2>&1
echo "baseline (no TMPDIR)  rc=$? exists=$([ -d "$FIX/home/IWE" ] && echo yes || echo no)"
( cd "$FIX/ws" && env -i PATH="$PATH" HOME="$FIX" TMPDIR="$FIX/home" bash .claude/bin2/guarded-rm -rf "$FIX/home/IWE" ) >/dev/null 2>&1
echo "hostile TMPDIR=home   rc=$? exists=$([ -d "$FIX/home/IWE" ] && echo yes || echo no)"
echo "fixture: $FIX"
