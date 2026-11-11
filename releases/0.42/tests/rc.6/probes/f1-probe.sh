#!/usr/bin/env bash
# F2 re-check: feed synthetic Bash PreToolUse payloads through every Bash PreToolUse hook registered in
# an INSTALLED workspace's .claude/settings.json (a disposable copy). Prints the strictest exit code
# and which hooks blocked; the first probe is a harmless control that must give 0.
set -u
WS="${1:?installed IWE workspace copy}"; FAKE_HOME="${2:?home of that copy}"
mapfile -t HOOKS < <(jq -r '.hooks.PreToolUse[] | select((.matcher // "") | test("Bash")) | .hooks[].command' "$WS/.claude/settings.json")
echo "== $(jq -r .version "$WS/FMT-exocortex-template/update-manifest.json") ($WS): Bash-хуков ${#HOOKS[@]}; заранее разрешено: $(jq -r '.permissions.allow[]?' "$WS/.claude/settings.json" | grep -E '^Bash\((find|rg)' | tr '\n' ' ')"
probe() {
  local cmd="$1" payload worst=0 rc h who=""
  payload=$(python3 -c 'import json,sys;print(json.dumps({"hook_event_name":"PreToolUse","session_id":"probe-0000","tool_name":"Bash","tool_input":{"command":sys.argv[1]},"cwd":sys.argv[2]}))' "$cmd" "$WS")
  for h in "${HOOKS[@]}"; do
    h=${h//\$CLAUDE_PROJECT_DIR/$WS}; h=${h//\"/}
    printf '%s' "$payload" | (cd "$WS" && env -i PATH="/run/wrappers/bin:/run/current-system/sw/bin" HOME="$FAKE_HOME" CLAUDE_PROJECT_DIR="$WS" bash -c "$h") >/dev/null 2>&1; rc=$?
    if [ "$rc" -eq 2 ]; then worst=2; who="$who $(basename "${h%% *}" .sh)"; fi
  done
  printf '%-3s %-70s %s\n' "$worst" "$cmd" "${who:+[блок:$who]}"
}
echo "-- атака rc.6 F1 (чтение, затем действие; должны давать 2):"
for c in "find . -name v -exec grep -l foo {} \; -delete" "find . -name v -exec cat {} \; -delete" "find . -name v -execdir cat {} \; -exec rm {} \;" \
         "find . -name v -exec cat {} \; -exec rm -f {} \;" "find . -name v -exec wc -l {} \; -exec sh -c 'rm \"\$0\"' {} \;" \
         "find . -name v -exec head -1 {} \; -execdir rm {} +" "find . -name v -exec cat {} \; -fprint out.txt" \
         "find .claude/hooks -name destructive-guard.sh -exec cat {} \; -fprint .claude/hooks/destructive-guard.sh"; do probe "$c"; done
echo "-- контроль (должны давать 2 / 0):"
probe "find . -name v -delete"; probe "find . -name v -exec cat {} + -delete"; probe "find . -name v -exec cat {} \;"
