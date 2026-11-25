#!/bin/bash
# Installs v0.42.1 into the disposable upg/ case, adds user edits, records governance hooks, makes the backup copy.
set -u
B="$(cd "$(dirname "$0")/.." && pwd)"; C="$B/upg"; W="$C/ws"; F="$W/FMT-exocortex-template"
[ -e "$C" ] && { echo "upg already exists"; exit 1; }
mkdir -p "$W" "$C/outside"
git clone --quiet --branch v0.42.1 https://github.com/TserenTserenov/FMT-exocortex-template.git "$F" 2>/dev/null
echo "installed source: $(git -C "$F" rev-parse HEAD)"
"$B/tools/run.sh" "$C" "$F" bash -c 'SETUP_CI=1 GITHUB_USER=tester bash setup.sh; echo "### exit=$?"' > "$B/logs/line2-setup-0.42.1.raw.log" 2>&1
tail -1 "$B/logs/line2-setup-0.42.1.raw.log"
mkdir -p "$W/extensions" "$F/extensions"
echo "моя правка (рабочая папка)" > "$W/extensions/test-marker.md"
echo "моя правка (шаблон)" > "$F/extensions/test-marker.md"
echo "test_marker: keep-me" >> "$W/params.yaml"
echo "tester marker line: keep-me" >> "$W/memory/MEMORY.md"
ln -s "$C/outside" "$W/link-out"
{
  echo "core.hooksPath=$(git -C "$W/DS-strategy" config core.hooksPath)"
  for h in pre-commit pre-push pre-commit-deny-legacy-sessions.sh; do
    echo "$h: installed(0.42.1)=$(shasum -a 256 "$W/DS-strategy/.githooks/$h" | cut -c1-16)"
  done
} > "$B/logs/line2-hooks-before.txt"
mkdir -p "$B/upg-backup"; cp -a "$W" "$C/home" "$B/upg-backup/"
cat "$B/logs/line2-hooks-before.txt"; grep -c memory-write-permission.sh "$W/.claude/settings.json"
