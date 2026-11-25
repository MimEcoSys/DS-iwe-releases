#!/bin/bash
# Program checks that accompany line 4 (same set as on rc.2), run on the live candidate install.
B="$(cd "$(dirname "$0")/.." && pwd)"; W="$B/live/ws"; F="$W/FMT-exocortex-template"; L="$B/logs"
r() { "$B/tools/run-deps.sh" "$B/live" "$@"; }
{ r "$F" python3 -m pytest -q scripts/tests/test_issue_1451_wakatime_403.py; echo "exit=$?"; } > "$L/line4-1646-wakatime-tests.raw.log" 2>&1
{ r "$F" bash scripts/tests/day-open-llm-fill-today-plan-detect-smoke.sh; echo "exit=$?"; } > "$L/line4-1648-plan-detect.raw.log" 2>&1
{ r "$F" bash scripts/tests/test_issue_1625_runtime_warning.sh; echo "exit=$?"; } > "$L/line4-1653-runtime-warning.raw.log" 2>&1
OLD="$B/tools/canon-reconcile-published-0.42.1.sh"
git -C "$B/src/FMT" show v0.42.1:scripts/canon-reconcile-published.sh > "$OLD"
{
  echo "== candidate rc.3 (live install, after day close)"
  r "$W" bash "$B/tools/probe-line4-runtime-warning.sh" "$W" "$F/scripts/canon-reconcile-published.sh"
  echo "== 0.42.1 script, same environment (for contrast)"
  r "$W" bash "$B/tools/probe-line4-runtime-warning.sh" "$W" "$OLD"
} > "$L/line4-1653-runtime-warning-direct.raw.log" 2>&1
{ r "$W" bash .claude/hooks/tests/test-session-open-gate.sh; echo "exit=$?"; } 2>&1 | tail -3 > "$L/line4-session-open-gate-test.raw.log"
{ r "$W" bash .claude/hooks/tests/test-issue-1657-secret-file-read-block-kimi-envelope.sh; echo "exit=$?"; } 2>&1 | tail -3 > "$L/line4-secret-file-read-block-test.raw.log"
for f in line4-1646-wakatime-tests line4-1648-plan-detect line4-1653-runtime-warning line4-1653-runtime-warning-direct line4-session-open-gate-test line4-secret-file-read-block-test; do
  echo "== $f"; tail -4 "$L/$f.raw.log" | cut -c1-220
done
