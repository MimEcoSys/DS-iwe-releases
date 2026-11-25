#!/bin/bash
# Copies sanitized logs, probe scripts and prompts into tests/rc.4/ of the releases repository clone.
set -eu
B="$(cd "$(dirname "$0")/.." && pwd)"; D="$B/releases-repo/releases/0.N/0.42.2/tests/rc.4"; U="$(id -un)"
rm -rf "$D/logs" "$D/probes"; mkdir -p "$D/logs/macos" "$D/probes/prompts"
python3 "$B/tools/sanitize.py" "$B" "$B/logs" "$B/raw" "$D/logs/macos" "$U" > /dev/null
scrub() { sed -e "s#$B#<TMP>#g" -e "s#$U#<user>#g" "$1" > "$2"; }
for f in run.sh run-deps.sh live.sh live-run.sh live-prepare.sh live-fixtures.sh line1-checks.sh programs.sh \
         line5-batch.sh line4-after.sh probe-line5-hook.sh probe-line4-memory-snapshot.sh sanitize.py publish.sh; do
  scrub "$B/tools/$f" "$D/probes/$f"
done
for s in gh launchctl crontab; do scrub "$B/tools/bin/$s" "$D/probes/stub-$s.sh"; done
for p in "$B"/prompts/*.txt; do scrub "$p" "$D/probes/prompts/${p##*/}"; done
echo "logs: $(ls "$D/logs/macos" | wc -l | tr -d ' ') probes: $(ls "$D/probes" | wc -l | tr -d ' ') prompts: $(ls "$D/probes/prompts" | wc -l | tr -d ' ')"
echo "leftovers (user name, local paths, token prefix): $(grep -rlE "$U|/private/tmp/claude|sk-ant""-" "$D" | wc -l | tr -d ' ')"
