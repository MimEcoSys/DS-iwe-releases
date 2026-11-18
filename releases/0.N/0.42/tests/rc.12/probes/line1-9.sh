#!/run/current-system/sw/bin/bash
# Protocol lines 1 and 9: clean full install of $RC, then update.sh --check verdict and the systemd --user timers.
# Usage (as iwe-test via probes/T): line1-9.sh <log-dir>
L=${1:?log dir}; mkdir -p "$L" ~/IWE
git clone -q --branch "$RC" https://github.com/TserenTserenov/FMT-exocortex-template.git ~/IWE/FMT-exocortex-template 2>/dev/null || exit 1
cd ~/IWE/FMT-exocortex-template || exit 1
echo "дерево: $(git rev-parse HEAD^{tree})"
printf "\n\n\n\n\nyy\nn\nn\nn\nn\n" | bash setup.sh > "$L/05-setup-rc-clean.log" 2>&1; echo "установка $RC код $?"
grep -E "Setup Complete|ERROR|ОШИБКА" "$L/05-setup-rc-clean.log" | head -5
echo "режим: $(cat ~/IWE/.iwe-install-mode 2>/dev/null || echo нет); манифест: $(jq -r .version update-manifest.json)"
IWE_UPDATE_CHANNEL=rc bash update.sh --check > "$L/06-check-rc-clean.log" 2>&1 </dev/null; echo "update.sh --check код $?"
grep -E "ВЕРДИКТ|Канал поставки" "$L/06-check-rc-clean.log"; grep -iE -- "--yes" "$L/06-check-rc-clean.log" | head -2
systemctl --user list-timers --all --no-pager > "$L/systemd-after-rc-clean.txt" 2>&1
grep -oE 'iwe-[a-z-]+\.timer|extractor[a-z-]*\.timer' "$L/systemd-after-rc-clean.txt" | sort -u
echo "слов «вручную/manually» в выводе установки: $(grep -ciE 'вручную|manually' "$L/05-setup-rc-clean.log")"
grep -iE 'вручную|manually' "$L/05-setup-rc-clean.log" | head -3
