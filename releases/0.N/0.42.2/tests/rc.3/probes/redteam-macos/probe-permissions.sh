#!/bin/bash
# usage: probe-permissions.sh <case-dir>   — file modes of a disposable install (read-only)
set -u
CASE="$1"; RT="$(cd "$(dirname "$0")/.." && pwd)"; W="$CASE/ws"; H="$CASE/home"
mask() { sed "s#$RT#<RT>#g"; }
echo "## group- or world-writable files and folders (outside .git):"
find "$W" "$H" -not -path '*/.git/*' \( -perm -002 -o -perm -020 \) -not -type l 2>/dev/null | mask | head -20
echo "count: $(find "$W" "$H" -not -path '*/.git/*' \( -perm -002 -o -perm -020 \) -not -type l 2>/dev/null | wc -l | tr -d ' ')"
echo "## modes of sensitive files:"
for f in "$W/.exocortex.env" "$W/.mcp.json" "$W/.claude/settings.json" "$W/.claude/settings.local.json" \
         "$W/params.yaml" "$W/.iwe-paths" "$H/.zshenv" "$H/.claude.json" "$H/.claude/settings.json"; do
  [ -e "$f" ] && stat -f '%Sp %N' "$f" | mask
done
echo "## modes of folders:"
stat -f '%Sp %N' "$W/.claude" "$W/.iwe-runtime" "$W/.claude/hooks" "$H/.claude" "$H/.claude/projects" "$(readlink "$W/memory")" 2>&1 | mask
echo "## hook scripts without the execute bit: $(find "$W/.claude/hooks" -maxdepth 1 -name '*.sh' ! -perm -100 | wc -l | tr -d ' ')"
echo "## setuid/setgid files: $(find "$W" "$H" -perm +6000 -type f 2>/dev/null | wc -l | tr -d ' ')"
echo "## absolute symlinks that leave the disposable install:"
find "$W" "$H" -type l -not -path '*/.git/*' 2>/dev/null | while read -r l; do
  t=$(readlink "$l")
  case "$t" in "$CASE"/*) ;; /*) echo "$l -> $t" | mask ;; esac
done | head
echo "## plist files written into the disposable HOME: $(find "$H" -name '*.plist' | wc -l | tr -d ' ')"
find "$H" -name '*.plist' -exec stat -f '%Sp %N' {} \; | mask | head -20
echo "## backups folder modes:"
[ -d "$W/.backups" ] && find "$W/.backups" -maxdepth 3 -exec stat -f '%Sp %N' {} \; | mask | head -20
echo "## service manager calls recorded by the stubs:"
grep -v '^gh ' "$CASE/stub-calls.log" 2>/dev/null | mask | cut -c1-160 | head -30
