# Protocol line 1 (macOS): clean install of $RC per README, then update.sh --check verdict.
# Usage (as iwe-test): line1.sh <core|full> <log-subdir>
. /private/tmp/iwe-rc13-probes/env.sh
MODE=${1:?mode}; L="$W/logs/${2:?subdir}"; mkdir -p "$L"
[ -e ~/IWE ] && { echo "~/IWE уже есть — сначала уборка"; exit 3; }
mkdir -p ~/IWE
git clone -q --branch "$RC" https://github.com/TserenTserenov/FMT-exocortex-template.git ~/IWE/FMT-exocortex-template 2>/dev/null || exit 1
cd ~/IWE/FMT-exocortex-template || exit 1
echo "дерево: $(git rev-parse HEAD^{tree})"
if [ "$MODE" = core ]; then ARGS=--core; IN='\n\nyy\n'; else ARGS=; IN='\n\n\n\n\nyy\nn\nn\nn\nn\n'; fi
s=$(date +%s); printf "$IN" | bash setup.sh $ARGS > "$L/01-setup.log" 2>&1; echo "установка ($MODE) код $? за $(( $(date +%s)-s )) с"
grep -E "Setup Complete|ERROR|ОШИБКА|cancelled" "$L/01-setup.log" | head -6
echo "режим: $(cat ~/IWE/.iwe-install-mode 2>/dev/null || echo нет); манифест: $(jq -r .version update-manifest.json)"
IWE_UPDATE_CHANNEL=rc bash update.sh --check > "$L/02-check-rc.log" 2>&1 </dev/null; echo "update.sh --check (канал rc) код $?"
grep -E "ВЕРДИКТ|Канал поставки|Всё актуально" "$L/02-check-rc.log"
bash update.sh --check > "$L/03-check-default.log" 2>&1 </dev/null; echo "update.sh --check (обычный канал) код $?"
grep -E "ВЕРДИКТ|Канал поставки|Всё актуально|откат|ROLLBACK" "$L/03-check-default.log" | head -4
echo "launchd-агентов iwe в ~/Library/LaunchAgents: $(ls ~/Library/LaunchAgents 2>/dev/null | grep -ciE 'iwe|exocortex|strategist|extractor')"
echo "слов «вручную/manually» в выводе установки: $(grep -ciE 'вручную|manually' "$L/01-setup.log")"
grep -iE 'вручную|manually|launchctl|launchd' "$L/01-setup.log" | head -5
