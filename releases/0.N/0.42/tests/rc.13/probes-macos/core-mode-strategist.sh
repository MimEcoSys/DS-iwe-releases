# Does update.sh on macOS create strategist launchd jobs on an install whose mode is recorded as core?
. /private/tmp/iwe-rc13-probes/env.sh
L="$W/logs/finding-core-strategist"; mkdir -p "$L"
echo "загружено в launchctl до: $(launchctl list 2>/dev/null | grep -c strategist)"
mkdir -p "$W/runs/plists-after-line2"; mv ~/Library/LaunchAgents/com.strategist.*.plist "$W/runs/plists-after-line2/" 2>/dev/null
launchctl list 2>/dev/null | grep strategist | awk '{print $3}' | while read -r lb; do launchctl remove "$lb" && echo "снято из launchctl: $lb"; done
echo "агентов в LaunchAgents: $(ls ~/Library/LaunchAgents | wc -l | tr -d ' ')"
[ -e ~/IWE ] && { echo "~/IWE есть"; exit 3; }
mkdir -p ~/IWE; git clone -q --branch "$PREV" https://github.com/TserenTserenov/FMT-exocortex-template.git ~/IWE/FMT-exocortex-template 2>/dev/null; cd ~/IWE/FMT-exocortex-template
printf '\n\nyy\n' | bash setup.sh --core > "$L/01-setup-prev-core.log" 2>&1; echo "установка $PREV --core код $?; агентов после установки: $(ls ~/Library/LaunchAgents | grep -c strategist)"
printf 'core\n' > ~/IWE/.iwe-install-mode; echo "режим записан вручную: $(cat ~/IWE/.iwe-install-mode)"
printf "y\ny\ny\ny\n" | IWE_UPDATE_CHANNEL=rc bash update.sh > "$L/02-update.log" 2>&1; echo "обновление код $?"
grep -E "урезанном режиме|режим установки|Strategist|strategist переустановлен|Agents loaded" "$L/02-update.log" | grep -v '^\s*+' | sed "s#$HOME#~#g"
echo "агентов стратега после обновления: $(ls ~/Library/LaunchAgents | grep -c strategist); в launchctl: $(launchctl list 2>/dev/null | grep -c strategist)"
