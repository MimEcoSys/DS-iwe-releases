#!/run/current-system/sw/bin/bash
# Line 2 preparation: fresh full install of $PREV for the disposable user, plus the user's own edits.
# Usage (as iwe-test via probes/T): install-prev.sh <log-dir>
L=${1:?log dir}; mkdir -p "$L" ~/IWE
git clone -q --branch "$PREV" https://github.com/TserenTserenov/FMT-exocortex-template.git ~/IWE/FMT-exocortex-template || exit 1
cd ~/IWE/FMT-exocortex-template || exit 1
printf "\n\n\n\n\nyy\nn\nn\nn\nn\n" | bash setup.sh > "$L/01-setup-prev.log" 2>&1; echo "установка $PREV код $?"
mkdir -p ~/IWE/extensions && echo "<!-- маркер тестировщика: своё расширение -->" > ~/IWE/extensions/test-marker.md
echo "test_marker: true" >> ~/IWE/params.yaml
echo "манифест: $(jq -r .version update-manifest.json); режим: $(cat ~/IWE/.iwe-install-mode 2>/dev/null || echo нет)"
