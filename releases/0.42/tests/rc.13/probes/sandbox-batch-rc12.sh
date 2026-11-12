#!/run/current-system/sw/bin/bash
# Step 2 sandbox probes for rc.12, each in its own fresh sandbox; summaries to <log-dir>/sandbox-summary-<name>.txt
P=$(cd "$(dirname "$0")" && pwd); L=${1:?log dir}; mkdir -p "$L"
LS='$HOME/rt5-1/lsremote-upto-rc12.txt'; RC8=b871465497e0a2abfc2ab8f1c9a5b2ef86b90be5; RC5=48dd21520fb5321112bd4893faacca73beabb881
job(){ local n=$1; shift; "$P/sb-run.sh" "$n" "$*" > "$L/sandbox-summary-$n.txt" 2>&1; echo "rc=$?" >> "$L/sandbox-summary-$n.txt"; }
job rt8-1-a "bash rt8-1.sh a-core-0.41.11-to-rc12 v0.41.11 core no $LS ~/out" &
job rt8-1-b "bash rt8-1.sh b-core-presched-0.41.11-to-rc12 v0.41.11 core yes $LS ~/out" &
job rt8-1-c-full "bash rt8-1.sh c-full-rc12 v0.42.0-rc.12 full no $LS ~/out" &
job rt8-1-c-core "bash rt8-1.sh c-core-rc12 v0.42.0-rc.12 core no $LS ~/out" &
job rt5-2 "bash rt5-2-core.sh v0.42.0-rc.12 ~/out $LS" &
job rt5-1-rc8 "bash install-prev.sh ~/out && bash rt5-1/run-drift.sh rc12-fake-to-rc8 $LS v0.42.0-rc.13 $RC8 ~/out" &
job rt5-1-rc5 "bash install-prev.sh ~/out && bash rt5-1/run-drift.sh rc12-fake-to-rc5 $LS v0.42.0-rc.13 $RC5 ~/out" &
job f3 "bash install-prev.sh ~/out && bash f3-clone-memory.sh v0.42.0-rc.12 $LS ~/out" &
wait
