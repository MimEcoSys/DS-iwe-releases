#!/run/current-system/sw/bin/bash
# RT5-1 replay inside a bwrap sandbox: a fresh 0.41.11 install updates over the rc channel while the
# API mock alternates the newest candidate tag between a real tag and a fake one pointing at an older commit.
# Usage: run-drift.sh <label> <lsremote-file> <fake-tag> <fake-commit> <log-dir>
set -u
label=$1 ls=$2 tag=$3 sha=$4 L=$5
mkdir -p ~/shim ~/api "$L"
cp ~/rt5-1/curl ~/rt5-1/apimock.py ~/shim/ && cp "$ls" ~/api/lsremote.txt && rm -f ~/api/drift.count ~/shim/calls.log
cd ~/IWE/FMT-exocortex-template || exit 1
start=$(date +%s)
PATH=~/shim:$PATH RT_SHIM_DIR=~/shim RT_DRIFT="$sha" RT_DRIFT_TAG="$tag" IWE_UPDATE_CHANNEL=rc \
  timeout 240 bash update.sh --yes > "$L/rt5-1-$label.log" 2>&1 </dev/null
rc=$?
echo "$label: код $rc (124 = остановлено по таймеру 240 с), $(( $(date +%s) - start )) с"
echo "  запросов списка меток: $(cat ~/api/drift.count 2>/dev/null || echo 0)"
echo "  строк «Канал поставки»: $(grep -c 'Канал поставки' "$L/rt5-1-$label.log")"
grep 'Канал поставки' "$L/rt5-1-$label.log" | sort | uniq -c | sed 's/^/  /'
grep -n 'снова изменился\|Перезапуск\|перезапуск' "$L/rt5-1-$label.log" | head -4 | cut -c1-220 | sed 's/^/  /'
cp ~/shim/calls.log "$L/rt5-1-$label-calls.log" 2>/dev/null
