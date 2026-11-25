#!/bin/bash
# Clean candidate install with the Python environment from requirements.txt, for the live agent runs.
set -u
B="$(cd "$(dirname "$0")/.." && pwd)"; C="$B/live"; W="$C/ws"; F="$W/FMT-exocortex-template"
[ -e "$C" ] && { echo "live already exists"; exit 1; }
mkdir -p "$W" "$C/outside"
git clone --quiet --branch v0.42.2-rc.3 https://github.com/TserenTserenov/FMT-exocortex-template.git "$F" 2>/dev/null
echo "installed source: $(git -C "$F" rev-parse HEAD)"
"$B/tools/run-deps.sh" "$C" "$F" bash -c 'python3 --version; SETUP_CI=1 GITHUB_USER=tester bash setup.sh; echo "### exit=$?"' > "$B/logs/line4-setup-with-deps.raw.log" 2>&1
tail -1 "$B/logs/line4-setup-with-deps.raw.log"
ln -s "$C/outside" "$W/link-out"
