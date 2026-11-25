#!/bin/bash
# usage: run.sh <case-dir> <cwd> <cmd...>   — clean env, disposable HOME, stubs first in PATH
CASE="$1"; CWD="$2"; shift 2
B="$(cd "$(dirname "$0")/.." && pwd)"
P="$(cd "$B/.." && pwd)"   # earlier rc.2 harness: python venv and links to node/claude/python3 (read-only use)
case "$CASE" in "$B"/*) ;; *) echo "run.sh: case dir outside the red team folder" >&2; exit 98 ;; esac
mkdir -p "$CASE/home" "$CASE/tmp"
cd "$CWD" || exit 97
exec env -i HOME="$CASE/home" USER=tester LOGNAME=tester LANG=en_US.UTF-8 TERM=dumb \
  PATH="$B/tools/bin:$P/tools/venv/bin:$P/tools/brewbin:/usr/bin:/bin:/usr/sbin:/sbin" \
  STUB_LOG="$CASE/stub-calls.log" TMPDIR="$CASE/tmp" \
  GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 \
  GIT_AUTHOR_NAME=tester GIT_AUTHOR_EMAIL=tester@test.local GIT_COMMITTER_NAME=tester GIT_COMMITTER_EMAIL=tester@test.local \
  ${RUN_EXTRA_ENV:-} \
  "$@"
