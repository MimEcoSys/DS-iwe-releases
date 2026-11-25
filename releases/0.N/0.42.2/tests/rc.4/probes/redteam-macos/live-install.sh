#!/bin/bash
# usage: live-install.sh <case-name> <tag>
# Install <tag> with the FMT root AT <case>/ws (so <case>/ws is the live workspace),
# the shape the live run harness expects. Same update channel as a real install.
set -u
B="$(cd "$(dirname "$0")/.." && pwd)"; CASE="$B/$1"; TAG="$2"
mkdir -p "$CASE/home" "$CASE/tmp"
[ -e "$CASE/ws" ] && { echo "ws exists"; exit 98; }
/usr/bin/git clone -q --branch "$TAG" "$B/../src/FMT" "$CASE/ws" 2>/dev/null || { echo "clone fail"; exit 96; }
/usr/bin/git -C "$CASE/ws" remote set-url origin https://github.com/TserenTserenov/FMT-exocortex-template.git
RUN_EXTRA_ENV="SETUP_CI=1" "$B/tools/run.sh" "$CASE" "$CASE/ws" bash setup.sh > "$B/raw/live-setup-$1.log" 2>&1
echo "setup exit=$?"
