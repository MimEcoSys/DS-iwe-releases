#!/run/current-system/sw/bin/bash
# Protocol line 2: update the fresh $PREV install over the rc channel (answers "y"), then rerun.
# Usage (as iwe-test via probes/T): line2.sh <log-dir>
L=${1:?log dir}; T=~/IWE/FMT-exocortex-template; cd "$T" || exit 1
fp(){ (cd ~ && find IWE .claude -path "*/.git" -prune -o -type f ! -path "*/.backups/*" ! -path "*/.iwe-runtime/state/*" -print0 | sort -z | xargs -0 sha256sum); }
printf "y\ny\ny\ny\n" | IWE_UPDATE_CHANNEL=rc bash update.sh > "$L/02-update-to-rc.log" 2>&1; echo "обновление код $?"
grep -E "Канал поставки|Обновление завершено|ОШИБКА|прервался|конфликт" "$L/02-update-to-rc.log" | head -6
echo "манифест: $(jq -r .version update-manifest.json); метка: $(git describe --tags 2>/dev/null)"
echo "правки: $(cat ~/IWE/extensions/test-marker.md) / $(grep test_marker ~/IWE/params.yaml)"
fp > ~/fp-before-rerun
printf "y\ny\ny\ny\n" | IWE_UPDATE_CHANNEL=rc bash update.sh > "$L/03-update-to-rc-rerun.log" 2>&1; echo "повтор код $?"
tail -3 "$L/03-update-to-rc-rerun.log"
fp > ~/fp-after-rerun; diff -q ~/fp-before-rerun ~/fp-after-rerun >/dev/null && echo "содержимое после повтора не изменилось" || { echo "ИЗМЕНЕНО после повтора:"; diff ~/fp-before-rerun ~/fp-after-rerun | grep '^[<>]' | awk '{print $1, $3}' | head -10; }
n=0; x=0; while IFS=$'\t' read -r meta path; do set -- $meta; [ "$1" = 100755 ] || continue; n=$((n+1)); [ -x "$path" ] || { x=$((x+1)); echo "  не исполняем: $path"; }; done < <(git ls-tree -r "$RC"); echo "программ (100755): $n, без права на запуск: $x"
