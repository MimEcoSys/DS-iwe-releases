#!/bin/bash
# After the main update: governance hooks vs candidate, then a second update run with a before/after hash snapshot.
B="$(cd "$(dirname "$0")/.." && pwd)"; C="$B/upg"; W="$C/ws"; F="$W/FMT-exocortex-template"
{
  echo "core.hooksPath=$(git -C "$W/DS-strategy" config core.hooksPath)"
  for h in pre-commit pre-push pre-commit-deny-legacy-sessions.sh; do
    echo "$h: installed=$(shasum -a 256 "$W/DS-strategy/.githooks/$h" | cut -c1-16) candidate(seed/strategy/.githooks/$h)=$(shasum -a 256 "$F/seed/strategy/.githooks/$h" | cut -c1-16)"
  done
} > "$B/logs/line2-hooks-after.txt"
snap() { (cd "$C" && find ws -type f -not -path '*/.git/*' -print0 | sort -z | xargs -0 shasum -a 256) > "$1"; }
snap "$C/snap-before-2nd.txt"
printf 'y\n' | "$B/tools/run.sh" "$C" "$F" bash -c 'IWE_UPDATE_CHANNEL=rc bash update.sh; echo "### exit=$?"' > "$B/logs/line2-update-second.raw.log" 2>&1
snap "$C/snap-after-2nd.txt"
{
  echo "### files hashed before: $(wc -l < "$C/snap-before-2nd.txt" | tr -d ' ') after: $(wc -l < "$C/snap-after-2nd.txt" | tr -d ' ')"
  echo "### changed or new/removed files between the two snapshots:"
  diff "$C/snap-before-2nd.txt" "$C/snap-after-2nd.txt" | grep '^[<>]' | awk '{print $1, $3}' | sort -u -k2 | sed 's/^/###   /'
} >> "$B/logs/line2-update-second.raw.log"
cat "$B/logs/line2-hooks-after.txt"; grep -n 'Канал поставки\|актуально\|^###' "$B/logs/line2-update-second.raw.log"
