# Row 4 (rollback guard, macOS) on an install updated 0.41.11 -> candidate.
# Usage (as iwe-test): row4.sh <log-subdir>
. /private/tmp/iwe-rc13-probes/env.sh
L="$W/logs/${1:?subdir}"; mkdir -p "$L"; ONLY=/private/tmp/iwe-rc13-probes/only-0.42-paths.txt
T=~/IWE/FMT-exocortex-template; cd "$T" || exit 1
MOD=docs/onboarding/light-onboarding.md
key='ОТКАТ|ROLLBACK|Отменено|Остановлено|старше|заменён|deprecated|изменён|Обновление завершено|ОШИБКА|прервался'
snap(){ (cd ~ && find IWE .claude -path "*/.git" -prune -o -type f ! -name "*.lock" ! -path "*/.iwe-runtime/state/*" ! -path "*/.backups/*" ! -name .build-hash -print0 | sort -z | xargs -0 shasum -a 256); }
same(){ snap > "$L/s-now"; diff -q "$L/s-before" "$L/s-now" >/dev/null && echo "  файлы не изменены" || { echo "  ФАЙЛЫ ИЗМЕНЕНЫ:"; diff "$L/s-before" "$L/s-now" | grep '^[<>]' | awk '{print $1,$3}' | head -5; }; }
q(){ grep -E "$key" "$1" | grep -vE '^\s*\+' | head -${2:-5}; }
echo "### подготовка: правлю один файл только из 0.42 ($MOD)"
echo "<!-- правка тестировщика до отката -->" >> "$MOD"; snap > "$L/s-before"
echo "### 4a обычный update.sh, ответ y"; printf "y\ny\ny\n" | bash update.sh > "$L/04a-rollback-no-confirm.log" 2>&1; echo "  код: $?"; q "$L/04a-rollback-no-confirm.log"; same
echo "### 4n обычный update.sh, ответ n"; printf "n\nn\nn\n" | bash update.sh > "$L/04n-rollback-answer-no.log" 2>&1; echo "  код: $?"; q "$L/04n-rollback-answer-no.log" 3; same
echo "### 4m1 канал main --yes"; IWE_UPDATE_CHANNEL=main bash update.sh --yes > "$L/04m1-main-yes.log" 2>&1 </dev/null; echo "  код: $?"; q "$L/04m1-main-yes.log" 3; same
echo "### 4m2 канал main без --yes, ответ y"; printf "y\ny\ny\n" | IWE_UPDATE_CHANNEL=main bash update.sh > "$L/04m2-main-no-confirm.log" 2>&1; echo "  код: $?"; q "$L/04m2-main-no-confirm.log" 3; same
echo "### 4b ROLLBACK"; printf "ROLLBACK\ny\ny\ny\n" | bash update.sh > "$L/04b-rollback-confirmed.log" 2>&1; echo "  код: $?"
grep -nE "$key" "$L/04b-rollback-confirmed.log" | grep -vE '^[0-9]+:\s*\+' | head -12
echo "  манифест: $(jq -r .version update-manifest.json)"
echo "  правки: $(cat ~/IWE/extensions/test-marker.md) / $(grep test_marker ~/IWE/params.yaml)"
[ "$(git hash-object update.sh)" = "$(git rev-parse v0.41.11:update.sh)" ] && echo "  update.sh = 0.41.11 по хешу" || echo "  update.sh НЕ совпадает с 0.41.11"
left=0; while read -r p; do [ -e "$p" ] && { left=$((left+1)); echo "  остался в папке шаблона: $p"; }; done < "$ONLY"; echo "  файлов только из 0.42 в папке шаблона: $left"
echo "  всего в .backups/deprecated: $(find ~/IWE/.backups/deprecated .backups/deprecated -type f 2>/dev/null | wc -l | tr -d ' ')"
echo "  изменённый файл: $( [ -e "$MOD" ] && tail -1 "$MOD" || echo 'НЕТ на месте'; find ~/IWE/.backups .backups -name "$(basename $MOD)*" 2>/dev/null | sed "s#$HOME#~#" | head -2)"
echo "### 4c повтор после отката"; printf "y\ny\ny\n" | bash update.sh > "$L/04c-after-rollback-rerun.log" 2>&1; echo "  код: $?"; tail -2 "$L/04c-after-rollback-rerun.log"
echo "### 4r снова на кандидата"; printf "y\ny\ny\ny\n" | IWE_UPDATE_CHANNEL=rc bash update.sh > "$L/04r-back-to-rc.log" 2>&1; echo "  код: $?"; echo "  манифест: $(jq -r .version update-manifest.json); правки: $(grep -c . ~/IWE/extensions/test-marker.md)/$(grep -c test_marker ~/IWE/params.yaml)"
