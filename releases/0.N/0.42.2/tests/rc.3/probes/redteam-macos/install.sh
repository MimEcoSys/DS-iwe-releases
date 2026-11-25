#!/bin/bash
# usage: install.sh <case-name> <tag>   — full non-interactive install of <tag> into redteam/<case>/ws
set -u
B="$(cd "$(dirname "$0")/.." && pwd)"; CASE="$B/$1"; TAG="$2"
[ -e "$CASE" ] && { echo "case exists"; exit 98; }
mkdir -p "$CASE/ws" "$CASE/home" "$CASE/tmp"
/usr/bin/git clone -q --branch "$TAG" "$B/../src/FMT" "$CASE/ws/FMT-exocortex-template" 2>/dev/null || exit 96
# the update channel must reach the real public template, as in a normal install
/usr/bin/git -C "$CASE/ws/FMT-exocortex-template" remote set-url origin https://github.com/TserenTserenov/FMT-exocortex-template.git
RUN_EXTRA_ENV="SETUP_CI=1" "$B/tools/run.sh" "$CASE" "$CASE/ws/FMT-exocortex-template" bash setup.sh > "$B/raw/install-$1.log" 2>&1
echo "exit=$?"
