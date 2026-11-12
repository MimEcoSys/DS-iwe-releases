#!/usr/bin/env bash
# F1 check: every manifest path that is 100755 in the tag must be executable in the installed template folder.
set -u
TAG="${1:?tag}"; REPO="${2:?git repo with the tag}"; TPL="${3:?installed FMT-exocortex-template}"
total=0; bad=0
while IFS= read -r p; do
  [ "$(git -C "$REPO" ls-tree "$TAG" -- "$p" | cut -c1-6)" = 100755 ] || continue
  total=$((total+1))
  if [ ! -x "$TPL/$p" ]; then bad=$((bad+1)); echo "  без права на запуск: $p ($(stat -c %a "$TPL/$p" 2>/dev/null || echo нет_файла))"; fi
done < <(jq -r '.files[].path' "$TPL/update-manifest.json")
echo "$TAG в $TPL: программ (755 в git) из манифеста: $total, без права на запуск: $bad"
for p in scripts/iwe-notify scripts/check-changelog-fields.py scripts/pack-duplicate-check.py .claude/hooks/dry-run-cmd-parse.pl; do printf '  %-40s %s\n' "$p" "$(stat -c %a "$TPL/$p")"; done
