#!/bin/bash
# usage: live.sh <case-dir> <cwd> <token-file> <claude args...>
# Live Claude Code run inside a disposable install: clean env, disposable HOME, stubs first in PATH,
# no system git config (no keychain credential helper). The sign-in token is read from the file
# straight into the environment of the claude process: it never becomes an argument, is never
# printed and is never written anywhere by this script.
CASE="$1"; CWD="$2"; TOKEN_FILE="$3"; shift 3
B="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$CASE/home" "$CASE/tmp"
cd "$CWD" || exit 97
[ -r "$TOKEN_FILE" ] || { echo "live.sh: token file is not readable" >&2; exit 96; }
exec env -i HOME="$CASE/home" USER=tester LOGNAME=tester LANG=en_US.UTF-8 TERM=dumb \
  PATH="$B/tools/bin:$B/tools/venv/bin:$B/tools/brewbin:/usr/bin:/bin:/usr/sbin:/sbin" \
  STUB_LOG="$CASE/stub-calls.log" TMPDIR="$CASE/tmp" \
  GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 \
  GIT_AUTHOR_NAME=tester GIT_AUTHOR_EMAIL=tester@test.local GIT_COMMITTER_NAME=tester GIT_COMMITTER_EMAIL=tester@test.local \
  ${LIVE_EXTRA_ENV:-} \
  /bin/bash -c 'f="$1"; shift
    # A person starts the agent from a terminal: zsh has already read ~/.zshenv (IWE path variables).
    [ "${LIVE_NO_SHELL_ENV:-0}" = 1 ] || { [ -f "$HOME/.zshenv" ] && . "$HOME/.zshenv"; }
    CLAUDE_CODE_OAUTH_TOKEN="$(cat "$f")" exec claude "$@"' live "$TOKEN_FILE" "$@"
