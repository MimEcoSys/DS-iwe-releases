#!/run/current-system/sw/bin/bash
# Build a fresh bwrap sandbox home (probes, API mock, gh shim, Claude CLI of the test user) and run one command in it via probes/B.
# Usage: sb-run.sh <sandbox-name> <command...>   (sandbox root: /tmp/rc13-work/sb/<name>; logs inside: ~/out)
set -u
P=$(cd "$(dirname "$0")" && pwd); name=$1; shift
export SB=/tmp/rc13-work/sb/$name CLAUDE_TOKEN_FILE=${CLAUDE_TOKEN_FILE:?set CLAUDE_TOKEN_FILE to the Claude token file}
if [ ! -d "$SB/home" ]; then
  mkdir -p "$SB/home/.local/bin" "$SB/tmp" "$SB/home/out" "$SB/home/iwe-rc13-linux/logs"
  cp -a "$P/rt5-1" "$SB/home/rt5-1"; cp "$P"/*.sh "$P/B" "$P/T" "$SB/home/" ; cp "$P/gh-shim" "$SB/home/.local/bin/gh"; chmod +x "$SB/home/.local/bin/gh"
  cp -a /tmp/rc13-work/npm-global "$SB/home/.npm-global"; cp /tmp/rc13-work/gitconfig "$SB/home/.gitconfig"; cp -a /tmp/rc13-work/git-templates "$SB/home/.git-templates"
  printf 'export PATH=$HOME/.npm-global/bin:$HOME/.local/bin:$PATH\n' > "$SB/home/.bashrc"
fi
exec "$P/B" "$*"
