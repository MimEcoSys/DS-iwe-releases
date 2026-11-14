# Row 4 continuation after the anonymous GitHub API limit reset: ROLLBACK, rerun, back to rc.
. /private/tmp/iwe-rc13-probes/env.sh
L="$W/logs/line4"; ONLY=/private/tmp/iwe-rc13-probes/only-0.42-paths.txt; T=~/IWE/FMT-exocortex-template; cd "$T" || exit 1
MOD=docs/onboarding/light-onboarding.md
key='ОТКАТ|ROLLBACK|Отменено|Остановлено|старше|заменён|deprecated|изменён|Обновление завершено|ОШИБКА|прервался'
echo "лимит GitHub без входа: $(curl -s https://api.github.com/rate_limit | jq .resources.core.remaining)"
echo "### 4b ROLLBACK"; printf "ROLLBACK\ny\ny\ny\n" | bash update.sh > "$L/04b-rollback-confirmed.log" 2>&1; echo "  код: $?"
grep -nE "$key" "$L/04b-rollback-confirmed.log" | grep -vE '^[0-9]+:\s*\+' | sed "s#$HOME#~#g" | head -14
echo "  манифест: $(jq -r .version update-manifest.json)"
echo "  правки: $(cat ~/IWE/extensions/test-marker.md) / $(grep test_marker ~/IWE/params.yaml)"
[ "$(git hash-object update.sh)" = "$(git rev-parse v0.41.11:update.sh)" ] && echo "  update.sh = 0.41.11 по хешу" || echo "  update.sh НЕ совпадает с 0.41.11"
left=0; while read -r p; do [ -e "$p" ] && { left=$((left+1)); echo "  остался в папке шаблона: $p"; }; done < "$ONLY"; echo "  файлов только из 0.42 в папке шаблона: $left"
echo "  в .backups/deprecated: $(find ~/IWE/.backups/deprecated -type f 2>/dev/null | wc -l | tr -d ' ') (из папки шаблона $(find ~/IWE/.backups/deprecated -type f -path '*FMT-exocortex-template*' 2>/dev/null | wc -l | tr -d ' '))"
echo "  изменённый файл: $( [ -e "$MOD" ] && tail -1 "$MOD" || echo 'НЕТ на месте')"
find ~/IWE/.backups -name "light-onboarding.md*" 2>/dev/null | sed "s#$HOME#~#" | head -2
bash /private/tmp/iwe-rc13-probes/mode-check.sh | tail -3
echo "### 4c повтор после отката"; printf "y\ny\ny\n" | bash update.sh > "$L/04c-after-rollback-rerun.log" 2>&1; echo "  код: $?"; tail -2 "$L/04c-after-rollback-rerun.log"
echo "### 4r снова на кандидата"; printf "y\ny\ny\ny\n" | IWE_UPDATE_CHANNEL=rc bash update.sh > "$L/04r-back-to-rc.log" 2>&1; echo "  код: $?"
grep -E "Канал поставки|Обновление завершено|ОШИБКА" "$L/04r-back-to-rc.log" | grep -vE '^\s*\+' | head -3
echo "  манифест: $(jq -r .version update-manifest.json); правки: $(grep -c . ~/IWE/extensions/test-marker.md)/$(grep -c test_marker ~/IWE/params.yaml)"
echo "  агентов стратега: $(ls ~/Library/LaunchAgents | grep -c strategist)"
echo "лимит GitHub после: $(curl -s https://api.github.com/rate_limit | jq .resources.core.remaining)"
