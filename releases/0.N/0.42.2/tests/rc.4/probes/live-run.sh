#!/bin/bash
# usage: live-run.sh <case: live|upg> <label> <permission-mode> <prompt-file> [extra claude args...]
# One non-interactive live Claude Code run in the disposable install; raw stream-json goes to raw/<label>.jsonl.
# The workspace is marked trusted in the disposable ~/.claude.json (as after a person accepts the trust dialog).
set -u
B="$(cd "$(dirname "$0")/.." && pwd)"; CASE="$B/$1"; LABEL="$2"; MODE="$3"; PROMPT="$4"; shift 4
W="$CASE/ws"; CFG="$CASE/home/.claude.json"
[ -f "$CFG" ] || echo '{}' > "$CFG"
tmp=$(mktemp); jq --arg w "$W" '.projects[$w].hasTrustDialogAccepted = true' "$CFG" > "$tmp" && mv "$tmp" "$CFG"
"$B/tools/live.sh" "$CASE" "$W" "$HOME/.config/iwe/fable-tester-token" \
  -p "$(cat "$PROMPT")" --model sonnet --permission-mode "$MODE" --output-format stream-json --verbose "$@" \
  > "$B/raw/$LABEL.jsonl" 2> "$B/raw/$LABEL.err" </dev/null
echo "exit=$? label=$LABEL"
jq -r 'select(.type=="system" and .subtype=="init") | "init: \(.claude_code_version) \(.model) mode=\(.permissionMode)"' "$B/raw/$LABEL.jsonl"
jq -r 'select(.type=="result") | "result: \(.subtype) turns=\(.num_turns) denials=\(.permission_denials|length) \([.permission_denials[]? | .tool_name + " " + ((.tool_input.file_path // .tool_input.command // "")|tostring|.[0:160])] | join(" ;; "))"' "$B/raw/$LABEL.jsonl"
echo "token-prefix-hits=$(grep -c "sk-ant""-" "$B/raw/$LABEL.jsonl" "$B/raw/$LABEL.err" | paste -sd' ' -)"
