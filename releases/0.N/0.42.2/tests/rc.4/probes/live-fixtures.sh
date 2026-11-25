#!/bin/bash
# Fixtures for lines 4 and 5 on the clean candidate install: a personal journal repository outside the IWE
# workspace (no remote), and links inside the memory folder.
set -u
B="$(cd "$(dirname "$0")/.." && pwd)"; C="$B/live"; W="$C/ws"; J="$C/home/journal"
g() { "$B/tools/run-deps.sh" "$C" "$C" git "$@"; }
mkdir -p "$J"; g -C "$J" init --quiet -b main; echo "личный журнал решений" > "$J/journal.md"
g -C "$J" add journal.md; g -C "$J" commit --quiet -m "journal: start"
echo "journal: $(g -C "$J" log --oneline | wc -l | tr -d ' ') commit(s), remotes: [$(g -C "$J" remote)]"
M="$(cd "$W/memory" && pwd -P)"
mkdir -p "$M/.git/hooks" "$M/.claude" "$M/plain/hooks" "$M/sub" "$C/outside-memory"
ln -s "$C/outside-memory" "$M/link-inside-out"      # link inside memory leading outside
ln -s "$M/plain" "$M/sub/.git"                       # link named .git pointing to an ordinary folder inside memory
ln -s "$M/plain" "$M/alias"                          # ordinary-named link to the same ordinary folder (contrast)
ls -la "$M" "$M/sub" | sed "s#$B#<TMP>#g"
