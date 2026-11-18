#!/run/current-system/sw/bin/bash
# RT8-1 check inside a bwrap sandbox (no SETUP_CI): install <start-tag> in <mode>, optionally create the extractor
# schedule by hand, then update twice over the rc channel pinned to one candidate through the API mock.
# systemctl and crontab are replaced by shims that only record their calls.
# Usage: rt8-1.sh <label> <start-tag> <core|full> <presched yes|no> <lsremote-file> <log-dir>
set -u
label=$1 tag=$2 mode=$3 pre=$4 ls=$5 L=$6
mkdir -p "$L" ~/IWE ~/svc ~/shim ~/api
for c in systemctl crontab; do
  printf '#!/run/current-system/sw/bin/bash\necho "%s $*" >> "$HOME/svc-calls.log"\nexit 0\n' "$c" > ~/svc/$c; chmod +x ~/svc/$c
done
cp ~/rt5-1/curl ~/rt5-1/apimock.py ~/shim/ && cp "$ls" ~/api/lsremote.txt
export PATH=~/svc:$PATH
units() { find ~/.config/systemd/user -maxdepth 1 -name 'extractor-git-diff-feed*' -type f 2>/dev/null | wc -l; }
unitsum() { cat ~/.config/systemd/user/extractor-git-diff-feed* 2>/dev/null | sha256sum | cut -c1-12; }
calls() { grep -c . ~/svc-calls.log 2>/dev/null || echo 0; }
git clone -q --branch "$tag" https://github.com/TserenTserenov/FMT-exocortex-template.git ~/IWE/FMT-exocortex-template 2>/dev/null
cd ~/IWE/FMT-exocortex-template || exit 1
if [ "$mode" = core ]; then printf "\n\nyy\nn\nn\nn\n" | bash setup.sh --core > "$L/rt8-1-$label-setup.log" 2>&1
else printf "\n\n\n\n\nyy\nn\nn\nn\nn\n" | bash setup.sh > "$L/rt8-1-$label-setup.log" 2>&1; fi
echo "$label: установка $tag ($mode) код $?; файл режима: $(cat ~/IWE/.iwe-install-mode 2>/dev/null || echo нет)"
if [ "$pre" = yes ]; then
  bash scripts/setup-extractor-feeders.sh > "$L/rt8-1-$label-presched.log" 2>&1 </dev/null
  echo "  расписание заведено вручную: код $?"
fi
echo "  файлов службы до обновления: $(units) (отпечаток $(unitsum)); вызовов systemctl/crontab за установку: $(calls)"
for run in 1 2; do
  : > ~/svc-calls.log
  PATH=~/shim:$PATH RT_SHIM_DIR=$HOME/shim IWE_UPDATE_CHANNEL=rc bash update.sh --yes > "$L/rt8-1-$label-update$run.log" 2>&1 </dev/null
  rc=$?
  echo "  обновление $run: код $rc; $(grep -m1 'Канал поставки' "$L/rt8-1-$label-update$run.log" | sed 's/^ *//')"
  echo "    файлов службы: $(units) (отпечаток $(unitsum)); вызовов systemctl: $(grep -c '^systemctl' ~/svc-calls.log), crontab: $(grep -c '^crontab' ~/svc-calls.log)"
  echo "    строк «расписания … нет … не заводим»: $(grep -c 'расписания на этой установке нет' "$L/rt8-1-$label-update$run.log"); «урезанном режиме»: $(grep -c 'урезанном режиме' "$L/rt8-1-$label-update$run.log"); строк про экстрактор: $(grep -c 'Экстрактор' "$L/rt8-1-$label-update$run.log")"
  cp ~/svc-calls.log "$L/rt8-1-$label-update$run-svc-calls.log"
done
