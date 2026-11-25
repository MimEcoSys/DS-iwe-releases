#!/bin/bash
# usage: line1-checks.sh — update --check (default and rc channel) and setup --validate on the clean install
B="$(cd "$(dirname "$0")/.." && pwd)"; F="$B/clean/ws/FMT-exocortex-template"
r() { "$B/tools/run.sh" "$B/clean" "$F" bash -c "$1; echo \"### exit=\$?\""; }
r 'bash update.sh --check' > "$B/logs/line1-update-check.raw.log" 2>&1
r 'IWE_UPDATE_CHANNEL=rc bash update.sh --check' > "$B/logs/line1-update-check-rc.raw.log" 2>&1
r 'bash setup.sh --validate' > "$B/logs/line1-setup-validate.raw.log" 2>&1
