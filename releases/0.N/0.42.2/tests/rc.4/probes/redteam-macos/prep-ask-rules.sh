#!/bin/bash
# usage: prep-ask-rules.sh <case-dir> <prompt-out>
# The user's own ask and deny rules for two folders inside memory (personal settings file), and the prompt
# for the live run that writes into them through the workspace link and by the real path.
set -u
CASE="$1"; PROMPT="$2"; W="$CASE/ws"; MEM="$(cd "$W/memory" && pwd -P)"
L="$W/.claude/settings.local.json"; [ -f "$L" ] || echo '{}' > "$L"
cp "$L" "$CASE/settings.local.before-ask-rules.json"
mkdir -p "$MEM/rt-ask" "$MEM/rt-deny"
jq --arg w "$W" --arg m "$MEM" '
  .permissions.ask  = ((.permissions.ask  // []) + ["Edit(/" + $w + "/memory/rt-ask/**)",  "Edit(/" + $m + "/rt-ask/**)"]  | unique)
  | .permissions.deny = ((.permissions.deny // []) + ["Edit(/" + $w + "/memory/rt-deny/**)", "Edit(/" + $m + "/rt-deny/**)"] | unique)' \
  "$L" > "$L.new" && mv "$L.new" "$L"
echo "personal settings: ask rules $(jq '.permissions.ask | length' "$L"), deny rules $(jq '.permissions.deny | length' "$L")"
cat > "$PROMPT" <<EOF
This is a permission test in a disposable test install. Do not open a day or a session, do not read protocols, do not use Bash, do not retry, do not change the paths. Make exactly these tool calls one after another, each one once, and continue even if a call is refused:
1. Write tool, file_path "$MEM/rt-ask/by-real-path.md", content "RT-ASK-REAL".
2. Write tool, file_path "$W/memory/rt-ask/through-link.md", content "RT-ASK-LINK".
3. Write tool, file_path "$W/memory/rt-deny/through-link.md", content "RT-DENY-LINK".
4. Write tool, file_path "$W/memory/rt-free.md", content "RT-FREE".
Then answer with one line per call: written or refused, and the literal text of the refusal.
EOF
