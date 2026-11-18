# Lines 2/3 (macOS): fresh install of <prev> (core), own edits, IWE_UPDATE_CHANNEL=rc update.sh, rerun, compare.
# Usage (as iwe-test): upgrade.sh <prev-tag> <sys|brew> <log-subdir> [core|full]
. /private/tmp/iwe-rc13-probes/env.sh
P=${1:?prev}; B=${2:?bash}; L="$W/logs/${3:?subdir}"; MODE=${4:-core}; mkdir -p "$L"
[ "$B" = sys ] && export PATH="$W/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin"
echo "bash в пути: $(command -v bash) — $(bash -c 'echo $BASH_VERSION')"
[ -e ~/IWE ] && { echo "~/IWE уже есть"; exit 3; }
mkdir -p ~/IWE
git clone -q --branch "$P" https://github.com/TserenTserenov/FMT-exocortex-template.git ~/IWE/FMT-exocortex-template 2>/dev/null || exit 1
cd ~/IWE/FMT-exocortex-template || exit 1
if [ "$MODE" = core ]; then ARGS=--core; IN='\n\nyy\n'; else ARGS=; IN='\n\n\n\n\nyy\nn\nn\nn\nn\n'; fi
printf "$IN" | bash setup.sh $ARGS > "$L/01-setup-$P.log" 2>&1; echo "установка $P ($MODE) код $?"
grep -E "Setup Complete|ERROR|ОШИБКА" "$L/01-setup-$P.log" | head -3
mkdir -p ~/IWE/extensions && echo "<!-- маркер тестировщика: своё расширение -->" > ~/IWE/extensions/test-marker.md
echo "test_marker: keep-me" >> ~/IWE/params.yaml
echo "манифест до: $(jq -r .version update-manifest.json); режим: $(cat ~/IWE/.iwe-install-mode 2>/dev/null || echo нет)"
fp(){ (cd ~ && find IWE .claude -path "*/.git" -prune -o -type f ! -path "*/.backups/*" ! -path "*/.iwe-runtime/state/*" -print0 | sort -z | xargs -0 shasum -a 256); }
s=$(date +%s); printf "y\ny\ny\ny\n" | IWE_UPDATE_CHANNEL=rc bash update.sh > "$L/02-update-to-rc.log" 2>&1; echo "обновление код $? за $(( $(date +%s)-s )) с"
grep -E "Канал поставки|Обновление завершено|ОШИБКА|прервался|конфликт" "$L/02-update-to-rc.log" | head -6
echo "манифест после: $(jq -r .version update-manifest.json); HEAD: $(git rev-parse --short HEAD) дерево $(git rev-parse HEAD^{tree})"
echo "правки: $(cat ~/IWE/extensions/test-marker.md) / $(grep test_marker ~/IWE/params.yaml)"
fp > "$L/fp-before-rerun"
printf "y\ny\ny\ny\n" | IWE_UPDATE_CHANNEL=rc bash update.sh > "$L/03-update-to-rc-rerun.log" 2>&1; echo "повтор код $?"
tail -2 "$L/03-update-to-rc-rerun.log"
fp > "$L/fp-after-rerun"; diff -q "$L/fp-before-rerun" "$L/fp-after-rerun" >/dev/null && echo "содержимое после повтора не изменилось" || { echo "ИЗМЕНЕНО после повтора:"; diff "$L/fp-before-rerun" "$L/fp-after-rerun" | grep '^[<>]' | awk '{print $1, $3}' | sort -u -k2 | head -10; }
n=0; x=0; while IFS=$'\t' read -r meta path; do set -- $meta; [ "$1" = 100755 ] || continue; n=$((n+1)); [ -x "$path" ] || { x=$((x+1)); echo "  не исполняем: $path"; }; done < <(git ls-tree -r "$RC"); echo "программ (100755): $n, без права на запуск: $x"
grep -cE "MISSING|DIFFERS|NOEXEC" "$L/02-update-to-rc.log" | sed 's/^/строк MISSING|DIFFERS|NOEXEC в журнале обновления: /'
