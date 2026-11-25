#!/bin/bash
# usage: live-run.sh <case-name> <label> <permission-mode> <prompt-name> [extra env assignments...]
# One live run plus its condensed transcript in logs/. RT_TOKEN_FILE must name the tester token file.
set -u
RT="$(cd "$(dirname "$0")/.." && pwd)"; CASE="$RT/$1"; LABEL="$2"; MODE="$3"; PROMPT="$RT/prompts/$4"; shift 4
bash "$RT/tools/live.sh" "$CASE" "$LABEL" "$MODE" "$PROMPT" "$@"
python3 "$RT/tools/condense.py" "$RT" "$RT/raw/$LABEL.jsonl" "$RT/logs/$LABEL.txt" "$(id -un)" >/dev/null
[ $# -gt 0 ] && printf '# extra environment of this run: %s\n' "$*" | sed "s#$RT#<RT>#g" >> "$RT/logs/$LABEL.txt"
cut -c1-460 "$RT/logs/$LABEL.txt"
