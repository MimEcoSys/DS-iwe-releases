#!/bin/bash
# usage: live.sh <case-dir> <label> <permission-mode> <prompt-file> [extra env assignments...]
# Live Claude Code run (claude -p) inside a disposable install: clean environment, disposable HOME,
# stubs first in PATH, no system git config. The workspace is marked trusted in the disposable
# .claude.json (what a person does in the trust dialog). The sign-in token is read from the tester
# token file straight into the environment of the claude process: it is never an argument, never
# printed and never written anywhere by this script.
set -u
CASE="$1"; LABEL="$2"; MODE="$3"; PROMPT_FILE="$4"; shift 4
B="$(cd "$(dirname "$0")/.." && pwd)"; P="$(cd "$B/.." && pwd)"
case "$CASE" in "$B"/*) ;; *) echo "live.sh: case dir outside the red team folder" >&2; exit 98 ;; esac
TOKEN_FILE="${RT_TOKEN_FILE:?set RT_TOKEN_FILE to the tester token file}"
[ -r "$TOKEN_FILE" ] || { echo "live.sh: token file is not readable" >&2; exit 96; }
W="$CASE/ws"; H="$CASE/home"; mkdir -p "$H" "$CASE/tmp"
CJ="$H/.claude.json"; [ -f "$CJ" ] || echo '{}' > "$CJ"
jq --arg w "$W" '.projects[$w].hasTrustDialogAccepted = true' "$CJ" > "$CJ.new" && mv "$CJ.new" "$CJ"
OUT="$B/raw/$LABEL.jsonl"; ERR="$B/raw/$LABEL.err"
cd "$W" || exit 97
env -i HOME="$H" USER=tester LOGNAME=tester LANG=en_US.UTF-8 TERM=dumb \
  PATH="$B/tools/bin:$P/tools/venv/bin:$P/tools/brewbin:/usr/bin:/bin:/usr/sbin:/sbin" \
  STUB_LOG="$CASE/stub-calls.log" TMPDIR="$CASE/tmp" \
  GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 \
  GIT_AUTHOR_NAME=tester GIT_AUTHOR_EMAIL=tester@test.local GIT_COMMITTER_NAME=tester GIT_COMMITTER_EMAIL=tester@test.local \
  "$@" \
  /bin/bash -c 'f="$1"; mode="$2"; prompt="$3"
    # A person starts the agent from a terminal: zsh has already read ~/.zshenv (IWE path variables).
    [ -f "$HOME/.zshenv" ] && . "$HOME/.zshenv"
    CLAUDE_CODE_OAUTH_TOKEN="$(cat "$f")" exec claude -p "$(cat "$prompt")" --permission-mode "$mode" \
      --model sonnet --max-turns 25 --output-format stream-json --verbose' live "$TOKEN_FILE" "$MODE" "$PROMPT_FILE" \
  > "$OUT" 2> "$ERR" < /dev/null
echo "exit=$? events=$(wc -l < "$OUT" | tr -d ' ') stderr_bytes=$(wc -c < "$ERR" | tr -d ' ')"
