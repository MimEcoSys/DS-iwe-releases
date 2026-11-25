#!/bin/bash
# usage: probe-memory-hook.sh <case-dir>
# Direct attack on the installed PermissionRequest hook memory-write-permission.sh (#1626).
# No agent: the hook receives the request JSON on stdin. Every fixture lives in the case dir.
set -u
CASE="$1"; RT="$(cd "$(dirname "$0")/.." && pwd)"; W="$CASE/ws"; H="$CASE/home"
case "$CASE" in "$RT"/*) ;; *) echo "refusing: case outside red team folder"; exit 98 ;; esac
HOOK="$W/.claude/hooks/memory-write-permission.sh"
MEM="$(cd "$W/memory" && pwd -P)"
OUT="$CASE/outside"; mkdir -p "$OUT/dir"
mask() { sed "s#$RT#<RT>#g"; }
n=0; unexpected=0

# ask <expect: allow|silent> <label> <mode> <tool> <field> <path> [env assignments...]
ask() {
  local expect="$1" label="$2" mode="$3" tool="$4" field="$5" path="$6"; shift 6
  local out rc d
  out=$(jq -n --arg m "$mode" --arg t "$tool" --arg f "$field" --arg p "$path" \
        '{hook_event_name:"PermissionRequest",permission_mode:$m,tool_name:$t,tool_input:{($f):$p,content:"x"}}' \
        | env -i HOME="$H" PATH="/usr/bin:/bin:$RT/../tools/brewbin" CLAUDE_PROJECT_DIR="$W" "$@" bash "$HOOK" 2>/dev/null); rc=$?
  if printf '%s' "$out" | grep -q '"behavior": *"allow"'; then d=allow; elif [ -z "$out" ]; then d=silent; else d="other"; fi
  n=$((n + 1))
  local flag=ok; [ "$d" = "$expect" ] || { flag="UNEXPECTED"; unexpected=$((unexpected + 1)); }
  printf '%-10s | expect=%-6s got=%-6s exit=%s | %s | mode=%s tool=%s | %s\n' "$flag" "$expect" "$d" "$rc" "$label" "$mode" "$tool" "$(printf '%s' "$path" | mask)"
}
raw() { # raw <expect> <label> <json>
  local expect="$1" label="$2" json="$3" out d
  out=$(printf '%s' "$json" | env -i HOME="$H" PATH="/usr/bin:/bin:$RT/../tools/brewbin" CLAUDE_PROJECT_DIR="$W" bash "$HOOK" 2>/dev/null)
  if printf '%s' "$out" | grep -q '"behavior": *"allow"'; then d=allow; elif [ -z "$out" ]; then d=silent; else d=other; fi
  n=$((n + 1))
  local flag=ok; [ "$d" = "$expect" ] || { flag="UNEXPECTED"; unexpected=$((unexpected + 1)); }
  printf '%-10s | expect=%-6s got=%-6s | %s\n' "$flag" "$expect" "$d" "$label"
}

echo "# fixtures (all inside the disposable case)"
mkdir -p "$MEM/sub/deep"
ln -sfn "$OUT/dir" "$MEM/link-out-dir"                 # folder link leaving memory
ln -sfn "$OUT/dir/existing.txt" "$MEM/link-out-file.md" ; : > "$OUT/dir/existing.txt"
ln -sfn "$OUT/dir/not-yet.txt" "$MEM/dangling.md"      # dangling link leaving memory
ln -sfn "$MEM/sub/deep" "$MEM/link-in"                 # folder link staying inside memory
rm -f "$MEM/sub/x.md"; ln -sfn "$OUT/dir/existing.txt" "$MEM/mis.md"  # lexical target of the dot-dot mismatch case; memory/sub/mis.md does not exist
ln -sfn loopb "$MEM/loopa"; ln -sfn loopa "$MEM/loopb" # link loop
ln "$OUT/dir/existing.txt" "$MEM/hardlink.md" 2>/dev/null || true

echo "# 1. baseline"
ask allow  "new file in memory"               acceptEdits Write file_path "$W/memory/rt-note.md"
ask allow  "new file in memory"               auto        Write file_path "$W/memory/rt-note.md"
ask allow  "nested existing folder"           acceptEdits Edit  file_path "$W/memory/sub/deep/a.md"
ask allow  "MultiEdit"                        acceptEdits MultiEdit file_path "$W/memory/rt-note.md"
ask allow  "NotebookEdit"                     acceptEdits NotebookEdit notebook_path "$W/memory/rt.ipynb"
echo "# 2. permission modes"
for m in default plan bypassPermissions dontAsk "" AUTO Auto "acceptEdits " "auto,default"; do
  ask silent "mode not in the approve list"   "$m" Write file_path "$W/memory/rt-note.md"
done
echo "# 3. dot-dot and normalisation"
ask silent "memory/../ escape"                acceptEdits Write file_path "$W/memory/../CLAUDE.md"
ask silent "memory/sub/../../ escape"         acceptEdits Write file_path "$W/memory/sub/../../.claude/settings.json"
ask silent "memory itself"                    acceptEdits Write file_path "$W/memory"
ask silent "memory with trailing slash"       acceptEdits Write file_path "$W/memory/"
ask silent "prefix sibling memory-evil"       acceptEdits Write file_path "$W/memory-evil/x.md"
ask silent "double leading slash"             acceptEdits Write file_path "/$W/memory/x.md"
ask silent "relative path"                    acceptEdits Write file_path "memory/x.md"
ask silent "upper-case MEMORY (same folder on this volume)" acceptEdits Write file_path "$W/MEMORY/x.md"
ask silent "missing parent folder"            acceptEdits Write file_path "$W/memory/no-such-dir/x.md"
ask allow  "dot segment inside"               acceptEdits Write file_path "$W/memory/./sub/../rt-note.md"
echo "# 4. links"
ask silent "folder link leaving memory"       acceptEdits Write file_path "$W/memory/link-out-dir/x.md"
ask silent "file link leaving memory"         acceptEdits Write file_path "$W/memory/link-out-file.md"
ask silent "dangling link leaving memory"     acceptEdits Write file_path "$W/memory/dangling.md"
ask silent "link loop"                        acceptEdits Write file_path "$W/memory/loopa"
ask allow  "folder link staying inside"       acceptEdits Write file_path "$W/memory/link-in/a.md"
ask silent "out-link then dot-dot (physical parent is outside)" acceptEdits Write file_path "$W/memory/link-out-dir/../x.md"
echo "# 4a. check/use mismatch: the hook resolves dot-dot after the link (physical), an editor that"
echo "#     collapses dot-dot as text writes to memory/mis.md, which is a link leaving memory"
ask silent "in-link + dot-dot, lexical target is an out-link" acceptEdits Write file_path "$W/memory/link-in/../mis.md"
echo "#     hard link: same inode as a file outside memory (the hook cannot see it)"
ask allow  "hard link to an outside file"     acceptEdits Write file_path "$W/memory/hardlink.md"
echo "# 5. other tools and malformed requests"
ask silent "Bash is not a file tool"          acceptEdits Bash  command  "echo x > $W/memory/x.md"
ask silent "Read"                             acceptEdits Read  file_path "$W/memory/x.md"
ask silent "lower-case tool name"             acceptEdits write file_path "$W/memory/x.md"
ask silent "Write with the path in the wrong field" acceptEdits Write path "$W/memory/x.md"
raw silent "path is a list"        "{\"permission_mode\":\"auto\",\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":[\"$W/memory/x.md\"]}}"
raw silent "tool_input is a string" "{\"permission_mode\":\"auto\",\"tool_name\":\"Write\",\"tool_input\":\"$W/memory/x.md\"}"
raw silent "top level is a list"   "[{\"permission_mode\":\"auto\",\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$W/memory/x.md\"}}]"
raw silent "not JSON"              "permission_mode=auto"
raw silent "empty input"           ""
raw silent "NUL inside the path"   "{\"permission_mode\":\"auto\",\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$W/memory/x\\u0000/../../../CLAUDE.md\"}}"
raw allow  "duplicate mode key, last one wins (auto)" "{\"permission_mode\":\"default\",\"permission_mode\":\"auto\",\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$W/memory/x.md\"}}"
echo "# 6. switches and environment"
ask silent "opt-out variable = 0"             acceptEdits Write file_path "$W/memory/rt-note.md" IWE_MEMORY_WRITE_AUTO_APPROVE=0
ask allow  "opt-out variable = false (only the literal 0 switches it off)" acceptEdits Write file_path "$W/memory/rt-note.md" IWE_MEMORY_WRITE_AUTO_APPROVE=false
ask allow  "opt-out variable empty"           acceptEdits Write file_path "$W/memory/rt-note.md" IWE_MEMORY_WRITE_AUTO_APPROVE=
ask silent "no project folder in the environment" acceptEdits Write file_path "$W/memory/rt-note.md" CLAUDE_PROJECT_DIR= IWE_WORKSPACE=
echo "# 7. foreign project: a cloned folder ships its own memory link and its own copy of the hook"
F="$CASE/foreign"; rm -rf "$F"; mkdir -p "$F/.claude/hooks" "$OUT/ssh"
cp "$HOOK" "$F/.claude/hooks/"
fask() { # fask <expect> <label> <link target> <written path> [env...]
  local expect="$1" label="$2" target="$3" path="$4"; shift 4
  rm -f "$F/memory"; ln -s "$target" "$F/memory"
  local out d
  out=$(jq -n --arg p "$path" '{permission_mode:"acceptEdits",tool_name:"Write",tool_input:{file_path:$p,content:"x"}}' \
        | env -i HOME="$H" PATH="/usr/bin:/bin:$RT/../tools/brewbin" CLAUDE_PROJECT_DIR="$F" "$@" bash "$F/.claude/hooks/memory-write-permission.sh" 2>/dev/null)
  if printf '%s' "$out" | grep -q '"behavior": *"allow"'; then d=allow; elif [ -z "$out" ]; then d=silent; else d=other; fi
  n=$((n + 1))
  local flag=ok; [ "$d" = "$expect" ] || { flag="UNEXPECTED"; unexpected=$((unexpected + 1)); }
  printf '%-10s | expect=%-6s got=%-6s | %s\n' "$flag" "$expect" "$d" "$label"
}
fask silent "memory -> a folder outside (stand-in for ~/.ssh)"      "$OUT/ssh" "$F/memory/authorized_keys"
fask silent "memory -> the memory of ANOTHER project (the install)"  "$MEM"     "$F/memory/MEMORY.md"
fask silent "memory -> the whole projects folder"                    "$H/.claude/projects" "$F/memory/x/memory/MEMORY.md"
FSLUG=$(printf '%s' "$(cd "$F" && pwd -P)" | sed 's/[^A-Za-z0-9]/-/g')
mkdir -p "$H/.claude/projects/$FSLUG/memory"
fask allow  "memory -> its own auto-memory folder (legitimate)"      "$H/.claude/projects/$FSLUG/memory" "$F/memory/x.md"
echo "#     environment the session could inherit: the folder name and the config folder are taken from variables"
fask allow  "CLAUDE_CODE_PROJECT_DIR_NAME points the check at another project's memory" "$MEM" "$F/memory/MEMORY.md" "CLAUDE_CODE_PROJECT_DIR_NAME=$(basename "$(dirname "$MEM")")"
mkdir -p "$OUT/cfg/projects/$FSLUG"; ln -sfn "$OUT/ssh" "$OUT/cfg/projects/$FSLUG/memory"
fask allow  "CLAUDE_CONFIG_DIR points at a folder where projects/<name>/memory is a link outside" "$OUT/ssh" "$F/memory/authorized_keys" "CLAUDE_CONFIG_DIR=$OUT/cfg"
echo "#     same folder name for two different project paths (every non-alphanumeric character becomes -)"
G1="$CASE/slug/a-b"; G2="$CASE/slug/a/b"; mkdir -p "$G1" "$G2"
s1=$(printf '%s' "$(cd "$G1" && pwd -P)" | sed 's/[^A-Za-z0-9]/-/g'); s2=$(printf '%s' "$(cd "$G2" && pwd -P)" | sed 's/[^A-Za-z0-9]/-/g')
[ "$s1" = "$s2" ] && echo "note       | project paths .../slug/a-b and .../slug/a/b share one auto-memory folder name (same rule as Claude Code itself)"
echo "# 8. swap between check and write (documented limit): the hook answers allow, then memory is repointed"
cp -R "$F" "$CASE/race"; R="$CASE/race"; RSLUG=$(printf '%s' "$(cd "$R" && pwd -P)" | sed 's/[^A-Za-z0-9]/-/g')
mkdir -p "$H/.claude/projects/$RSLUG/memory"; rm -f "$R/memory"; ln -s "$H/.claude/projects/$RSLUG/memory" "$R/memory"
out=$(jq -n --arg p "$R/memory/x.md" '{permission_mode:"auto",tool_name:"Write",tool_input:{file_path:$p}}' | env -i HOME="$H" PATH="/usr/bin:/bin:$RT/../tools/brewbin" CLAUDE_PROJECT_DIR="$R" bash "$R/.claude/hooks/memory-write-permission.sh" 2>/dev/null)
rm -f "$R/memory"; ln -s "$OUT/ssh" "$R/memory"
printf 'note       | answer before the swap: %s; after the swap the same written path resolves to %s\n' "$(printf '%s' "$out" | grep -q allow && echo allow || echo silent)" "$(cd "$R/memory" && pwd -P | mask)"
echo "# total requests: $n, answers different from the expected one: $unexpected"
