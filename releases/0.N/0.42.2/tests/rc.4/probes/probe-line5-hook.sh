#!/bin/bash
# Hook-level probe (no agent): feeds PermissionRequest JSON to a memory-write-permission.sh.
# usage: probe-line5-hook.sh <workspace> [hook-file]   (default: the hook installed in the workspace)
W="$1"; H="${2:-$W/.claude/hooks/memory-write-permission.sh}"
ask() { # label mode path
  out=$(jq -n --arg m "$2" --arg p "$3" '{hook_event_name:"PermissionRequest",permission_mode:$m,tool_name:"Write",tool_input:{file_path:$p,content:"x"}}' | CLAUDE_PROJECT_DIR="$W" bash "$H"); rc=$?
  if printf '%s' "$out" | grep -q '"allow"'; then d=allow; elif [ -z "$out" ]; then d="silent (prompt stays)"; else d="other: $out"; fi
  echo "$1 | mode=$2 | exit=$rc | $d"
}
ask "new file in memory/"              acceptEdits "$W/memory/tester-note.md"
ask "new file in memory/"              auto        "$W/memory/tester-note.md"
ask "new file in memory/"              default     "$W/memory/tester-note.md"
ask "via symlink to folder outside"    acceptEdits "$W/link-out/note.md"
ask "via symlink to folder outside"    auto        "$W/link-out/note.md"
ask "memory/../ escape"                acceptEdits "$W/memory/../CLAUDE.md"
ask "ordinary workspace file"          acceptEdits "$W/extensions/x.md"
IWE_MEMORY_WRITE_AUTO_APPROVE=0 ask "memory/ with opt-out"   acceptEdits "$W/memory/tester-note.md"
# sensitive and hidden paths inside memory keep the prompt
for p in .git/hooks/pre-commit .claude/x.md .github/x.yml .ssh/config .gnupg/x .hidden-note.md plain/.hidden.md; do
  mkdir -p "$(dirname "$W/memory/$p")"
  ask "memory/$p" acceptEdits "$W/memory/$p"
  ask "memory/$p" auto        "$W/memory/$p"
done
# links inside memory (fixtures from live-fixtures.sh)
for p in link-inside-out/x.md sub/.git/hooks/pre-commit alias/hooks/note.md; do
  ask "memory/$p" acceptEdits "$W/memory/$p"
  ask "memory/$p" auto        "$W/memory/$p"
done
