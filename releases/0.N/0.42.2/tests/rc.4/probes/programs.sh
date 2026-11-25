#!/bin/bash
# Template test programs for the two hooks changed in rc.4 and direct hook probes, on the clean candidate install.
B="$(cd "$(dirname "$0")/.." && pwd)"; W="$B/live/ws"; L="$B/logs"
r() { "$B/tools/run-deps.sh" "$B/live" "$@"; }
{ r "$W" bash .claude/hooks/tests/test-session-open-gate.sh; echo "exit=$?"; } > "$B/raw/line4-session-open-gate-test.full.log" 2>&1
{ grep -n 'tilde\|outside commit\|add then commit' "$B/raw/line4-session-open-gate-test.full.log"; tail -3 "$B/raw/line4-session-open-gate-test.full.log"; } > "$L/line4-session-open-gate-test.raw.log"
{ r "$W" bash .claude/hooks/tests/test-memory-write-permission.sh; echo "exit=$?"; } > "$L/line5-hook-test-clean.raw.log" 2>&1
OLD="$B/tools/memory-write-permission.rc3.sh"; git -C "$B/src/FMT" show v0.42.2-rc.3:.claude/hooks/memory-write-permission.sh > "$OLD"
{
  echo "== candidate rc.4, hook installed in the workspace"
  r "$W" bash "$B/tools/probe-line5-hook.sh" "$W"
  echo "== rc.3 hook file, same workspace (for contrast: the last three paths)"
  r "$W" bash "$B/tools/probe-line5-hook.sh" "$W" "$OLD" | tail -6
} > "$L/line5-hook-probe-clean.raw.log" 2>&1
tail -4 "$L/line4-session-open-gate-test.raw.log"; tail -3 "$L/line5-hook-test-clean.raw.log"; cat "$L/line5-hook-probe-clean.raw.log"
