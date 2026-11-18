# Every manifest path that is 100755 in the tag must exist and be executable in the installed template folder.
# Usage (as iwe-test): mode-check.sh [template-dir]
. /private/tmp/iwe-rc13-probes/env.sh
TPL=${1:-$HOME/IWE/FMT-exocortex-template}; REPO="$W/src"
total=0; bad=0; miss=0
while IFS= read -r p; do
  [ "$(git -C "$REPO" ls-tree "$RC" -- "$p" | cut -c1-6)" = 100755 ] || continue
  total=$((total+1))
  if [ ! -e "$TPL/$p" ]; then miss=$((miss+1)); echo "  нет файла: $p"
  elif [ ! -x "$TPL/$p" ]; then bad=$((bad+1)); echo "  без права на запуск: $p ($(stat -f %Lp "$TPL/$p"))"; fi
done < <(jq -r '.files[].path' "$TPL/update-manifest.json")
echo "$RC в установке: программ (755 в git) из манифеста: $total, нет файла: $miss, без права на запуск: $bad"
echo "из 37 вне манифеста: $(git -C "$REPO" ls-tree -r "$RC" | awk '$1==100755{print $4}' | grep -vxFf <(jq -r '.files[].path' "$TPL/update-manifest.json") | wc -l | tr -d ' ') программ кандидата не входят в список доставки"
