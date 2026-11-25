#!/bin/bash
# usage: publish.sh <release tests dir>   — cleaned logs and the probe scripts of the rc.3 red team run
set -u
RT="$(cd "$(dirname "$0")/.." && pwd)"; DST="$1"; U="$(id -un)"
L="$DST/logs/redteam-macos"; P="$DST/probes/redteam-macos"; mkdir -p "$L" "$P/prompts"
c() { python3 "$RT/tools/condense.py" "$RT" "$1" "$2" "$U" >/dev/null; }
for f in "$RT"/logs/rt*.txt; do c "$f" "$L/$(basename "$f")"; done
c "$RT/raw/rt0-calibration.log" "$L/rt0-calibration-home-in-temp.txt"
c "$RT/raw/rt0-calibration-home-var-empty.log" "$L/rt0-calibration.txt"
for f in "$RT"/raw/rt4-*.raw.log "$RT"/raw/rt5-rollback-*.raw.log "$RT"/raw/rt6-*.raw.log "$RT"/raw/quota/*.raw.log; do
  [ -f "$f" ] || continue
  n="$(basename "$f" .raw.log)"; c "$f" "$L/${n%.sh}.txt"
done
for f in "$RT"/tools/*.sh "$RT"/tools/*.py; do cp "$f" "$P/$(basename "$f")"; done
for f in "$RT"/prompts/*.txt; do c "$f" "$P/prompts/$(basename "$f")"; done
echo "logs: $(ls "$L" | wc -l | tr -d ' ') probes: $(ls "$P" | wc -l | tr -d ' ')"
