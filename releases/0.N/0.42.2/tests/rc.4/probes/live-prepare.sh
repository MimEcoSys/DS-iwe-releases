#!/bin/bash
# Clean candidate install (full, with the Python environment from requirements.txt) for line 1 smoke and the live agent runs.
set -u
B="$(cd "$(dirname "$0")/.." && pwd)"; C="$B/live"; W="$C/ws"; F="$W/FMT-exocortex-template"
[ -e "$C" ] && { echo "live already exists"; exit 1; }
mkdir -p "$W" "$C/outside"
git clone --quiet --branch v0.42.2-rc.4 https://github.com/TserenTserenov/FMT-exocortex-template.git "$F" 2>/dev/null
echo "installed source: $(git -C "$F" rev-parse HEAD)"
"$B/tools/run-deps.sh" "$C" "$F" bash -c 'python3 --version; SETUP_CI=1 GITHUB_USER=tester bash setup.sh; echo "### exit=$?"' > "$B/logs/line1-setup.raw.log" 2>&1
tail -1 "$B/logs/line1-setup.raw.log"
ln -s "$C/outside" "$W/link-out"
