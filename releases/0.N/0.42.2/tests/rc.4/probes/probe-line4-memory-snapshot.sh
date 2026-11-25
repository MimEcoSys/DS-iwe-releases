#!/bin/bash
# The day close run reported "memory snapshot not saved": the memory folder held the tester's symlink
# fixtures for line 5. This probe repeats the snapshot step with the fixtures in place and with them moved away.
# usage (through run-deps.sh, cwd = workspace): probe-line4-memory-snapshot.sh <workspace> <parking-dir>
W="$1"; PARK="$2"; . "$W/.iwe-paths"
M="$(cd "$W/memory" && pwd -P)"
LINKS="alias link-inside-out sub"
move() { for l in $LINKS; do [ -e "$1/$l" ] || [ -L "$1/$l" ] && mv "$1/$l" "$2/"; done; }
snap() {
  local dst; dst=$(mktemp -d)
  out=$(bash "$IWE_TEMPLATE/scripts/day-close.sh" --exocortex-snapshot "$dst" 2>&1); echo "exit=$?"
  printf '%s\n' "$out" | tail -3 | cut -c1-300
  echo "files in the snapshot: $(find "$dst" -type f | wc -l | tr -d ' ')"
}
mkdir -p "$PARK"
move "$PARK" "$M"
echo "== with the tester's links inside memory (alias, link-inside-out, sub/.git)"
snap
move "$M" "$PARK"
echo "== links moved out of memory"
snap
