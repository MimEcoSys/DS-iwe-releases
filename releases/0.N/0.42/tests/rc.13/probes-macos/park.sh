# Move the current disposable install aside (no deletion): ~/IWE and ~/.claude -> $W/runs/<label>/
. /private/tmp/iwe-rc13-probes/env.sh
D="$W/runs/${1:?label}"; mkdir -p "$D"
for p in IWE .claude; do [ -e ~/$p ] && mv ~/$p "$D/$p"; done
ls ~/Library/LaunchAgents 2>/dev/null | grep -iE 'iwe|exocortex|strategist|extractor' && echo "ВНИМАНИЕ: остались агенты launchd"
echo "убрано в $D"
