#!/bin/bash
# Facts after the four line 4 live runs: legacy-caller warning, hours summary reason, commits, stub calls.
B="$(cd "$(dirname "$0")/.." && pwd)"; W="$B/live/ws"
echo "== 'IWE_RUNTIME used as a directory' in the four line 4 transcripts (count per run)"
for f in "$B"/raw/line4-live-*.jsonl; do echo "${f##*/}: $(grep -c 'used as a directory' "$f")"; done
echo "== hours summary reason in the day close run"
grep -o 'WAKATIME_API_KEY not found[^"]*' "$B/raw/line4-live-4-day-close.jsonl" | cut -c1-80 | sort | uniq -c
echo "== strategy repository commits"
git -C "$W/DS-strategy" log --oneline -6
echo "== personal journal commits (outside the IWE workspace, no remote)"
git -C "$B/live/home/journal" log --oneline -6
echo "== stub calls during the live runs (new compared to the install)"
sort -u "$B/live/stub-calls.log" > "$B/live/tmp/stub-now.txt"; sort -u "$B/live/stub-calls.log.pre-live" > "$B/live/tmp/stub-pre.txt"
comm -23 "$B/live/tmp/stub-now.txt" "$B/live/tmp/stub-pre.txt" | cut -c1-200
