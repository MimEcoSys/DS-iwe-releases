#!/run/current-system/sw/bin/bash
# RT5-2 check inside a bwrap sandbox: setup.sh --core, then update.sh --yes over the rc channel.
# Expect on a fixed candidate: no extractor-git-diff-feed unit files and a "core mode" line.
# Usage: rt5-2-core.sh <tag> <log-dir> [lsremote-file: pin the rc channel through the API mock]
set -u
tag=$1 L=$2 ls=${3:-}
mkdir -p "$L" ~/IWE ~/iwe-rc6-linux/logs
git clone -q --branch "$tag" https://github.com/TserenTserenov/FMT-exocortex-template.git ~/IWE/FMT-exocortex-template 2>/dev/null
cd ~/IWE/FMT-exocortex-template || exit 1
printf "\n\nyy\nn\nn\nn\n" | bash setup.sh --core > "$L/rt5-2-$tag-setup.log" 2>&1
echo "$tag setup --core: код $?; файл режима: $(cat ~/IWE/.iwe-install-mode 2>/dev/null || echo нет)"
units() { find ~/.config/systemd/user -name 'extractor-git-diff-feed*' 2>/dev/null | wc -l; }
echo "  файлов службы экстрактора после установки: $(units)"
envx=(IWE_UPDATE_CHANNEL=rc)
if [ -n "$ls" ]; then
  mkdir -p ~/shim ~/api && cp ~/rt5-1/curl ~/rt5-1/apimock.py ~/shim/ && cp "$ls" ~/api/lsremote.txt
  envx+=(PATH=~/shim:$PATH RT_SHIM_DIR=$HOME/shim)
fi
env "${envx[@]}" bash update.sh --yes > "$L/rt5-2-$tag-update.log" 2>&1 </dev/null
echo "  update.sh --yes: код $?; $(grep -m1 'Канал поставки' "$L/rt5-2-$tag-update.log" | sed 's/^ *//')"
echo "  файлов службы экстрактора после обновления: $(units)"
find ~/.config/systemd/user -name 'extractor-git-diff-feed*' 2>/dev/null | sed 's#^#    #'
grep -n 'урезанн\|--core\|core mode\|extractor-git-diff-feed\|systemctl' "$L/rt5-2-$tag-update.log" | head -6 | cut -c1-200 | sed 's/^/  /'
