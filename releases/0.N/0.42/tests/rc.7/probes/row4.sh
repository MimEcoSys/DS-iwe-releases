#!/run/current-system/sw/bin/bash
# Row 4 (rollback guard) on an install updated 0.41.11 -> candidate. Runs as the disposable test user.
# Usage: row4.sh <log-dir> <list-of-0.42-only-paths>
L=${1:?log dir}; ONLY=${2:?file with 0.42-only manifest paths}
T=~/IWE/FMT-exocortex-template
cd "$T" || exit 1
MOD=docs/onboarding/light-onboarding.md
key='ОТКАТ|ROLLBACK|Отменено|Остановлено|старше|заменён|deprecated|изменён|Обновление завершено|ОШИБКА'
snap(){ (cd ~ && find IWE .claude -path "*/.git" -prune -o -type f ! -name "*.lock" ! -path "*/.iwe-runtime/state/*" ! -path "*/.backups/*" ! -name .build-hash -print0 | sort -z | xargs -0 sha256sum); }
same(){ snap > ~/s-now; diff -q ~/s-before ~/s-now >/dev/null && echo "  файлы не изменены" || { echo "  ФАЙЛЫ ИЗМЕНЕНЫ:"; diff ~/s-before ~/s-now | head -5; }; }

echo "### подготовка: правлю один файл только из 0.42 ($MOD)"
echo "<!-- правка тестировщика до отката -->" >> "$MOD"
snap > ~/s-before

echo "### 4a обычный update.sh, ответ y"
printf "y\ny\ny\n" | bash update.sh > $L/04a-rollback-no-confirm.log 2>&1; echo "  код: $?"; grep -E "$key" $L/04a-rollback-no-confirm.log | head -5; same
echo "### 4m1 канал main --yes"
IWE_UPDATE_CHANNEL=main bash update.sh --yes > $L/04m1-main-yes.log 2>&1 </dev/null; echo "  код: $?"; grep -E "$key" $L/04m1-main-yes.log | head -3; same
echo "### 4m2 канал main без --yes, ответ y"
printf "y\ny\ny\n" | IWE_UPDATE_CHANNEL=main bash update.sh > $L/04m2-main-no-confirm.log 2>&1; echo "  код: $?"; grep -E "$key" $L/04m2-main-no-confirm.log | head -3; same

echo "### 4b ROLLBACK"
printf "ROLLBACK\ny\ny\ny\n" | bash update.sh > $L/04b-rollback-confirmed.log 2>&1; echo "  код: $?"
grep -nE "$key" $L/04b-rollback-confirmed.log | head -12
echo "  манифест: $(jq -r .version update-manifest.json)"
cat ~/IWE/extensions/test-marker.md; grep test_marker ~/IWE/params.yaml
[ "$(git hash-object update.sh)" = "$(git rev-parse v0.41.11:update.sh)" ] && echo "  update.sh = 0.41.11 по хешу (сразу после отката)" || echo "  update.sh НЕ совпадает с 0.41.11"
left=0; while read -r p; do [ -e "$p" ] && { left=$((left+1)); echo "  остался в папке шаблона: $p"; }; done < "$ONLY"; echo "  файлов только из 0.42 в папке шаблона: $left"
echo "  .backups/deprecated:"; find .backups/deprecated -type f 2>/dev/null | sed 's#^#    #' | head -40; echo "  всего в deprecated: $(find .backups/deprecated -type f 2>/dev/null | wc -l)"
echo "  изменённый файл: $( [ -e "$MOD" ] && { tail -1 "$MOD"; } || echo 'НЕТ на месте')"

echo "### 4c повтор после отката"
printf "y\ny\ny\n" | bash update.sh > $L/04c-after-rollback-rerun.log 2>&1; echo "  код: $?"; tail -2 $L/04c-after-rollback-rerun.log
