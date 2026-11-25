#!/bin/bash
# usage: publish.sh <release tests dir>   — cleaned logs and the probe scripts of the red team run
set -u
RT="$(cd "$(dirname "$0")/.." && pwd)"; DST="$1"; U="$(id -un)"
L="$DST/logs/macos"; P="$DST/probes/redteam"; mkdir -p "$L" "$P"
c() { python3 "$RT/tools/condense.py" "$RT" "$1" "$2" "$U" >/dev/null; }
for f in "$RT"/logs/rt*.txt; do c "$f" "$L/$(basename "$f")"; done
c "$RT/raw/rt0-calibration.log" "$L/rt0-calibration-home-in-temp.txt"
c "$RT/raw/rt0-calibration-home-var-empty.log" "$L/rt0-calibration.txt"
for f in "$RT"/raw/rt4-*.raw.log "$RT"/raw/rt5-rollback-*.raw.log "$RT"/raw/rt6-*.raw.log; do
  n="$(basename "$f" .raw.log)"; c "$f" "$L/${n%.sh}.txt"
done
for f in "$RT"/raw/net-timeouts/*.raw.log; do c "$f" "$L/$(basename "$f" .raw.log).txt"; done
for f in run.sh install.sh live.sh condense.py upg-variant.sh upg-batch.sh variant-digest.sh rollback.sh show-settings.sh \
         probe-memory-hook.sh probe-secret-hook.sh probe-session-gate.sh probe-permissions.sh prep-ask-rules.sh publish.sh; do
  cp "$RT/tools/$f" "$P/$f"
done
mkdir -p "$P/prompts"
for f in "$RT"/prompts/*.txt; do c "$f" "$P/prompts/$(basename "$f")"; done
echo "logs: $(ls "$L" | grep -c '^rt') probes: $(ls "$P" | wc -l | tr -d ' ')"
