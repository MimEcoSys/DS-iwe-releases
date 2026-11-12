# Background chain: row 3 (sys, brew), fresh row 2 (sys) + row 4, then suites. Output -> $W/logs/chain.out
. /private/tmp/iwe-rc13-probes/env.sh
P=/private/tmp/iwe-rc13-probes
step(){ echo; echo "######## $* ($(date +%T))"; }
step "строка 3, системная bash";   bash $P/park.sh finding-core-strategist; mv ~/Library/LaunchAgents/com.strategist.*.plist "$W/runs/finding-core-strategist/" 2>/dev/null
bash $P/upgrade.sh v0.36.3 sys line3-sysbash 2>&1 | grep -v "не исполняем" | grep -vE '^\s+\+ - \['; bash $P/mode-check.sh | tail -2; echo "агентов стратега: $(ls ~/Library/LaunchAgents | grep -c strategist)"
step "строка 3, bash из Homebrew"; bash $P/park.sh line3-sysbash; mv ~/Library/LaunchAgents/com.strategist.*.plist "$W/runs/line3-sysbash/" 2>/dev/null
bash $P/upgrade.sh v0.36.3 brew line3-brewbash 2>&1 | grep -v "не исполняем" | grep -vE '^\s+\+ - \['; bash $P/mode-check.sh | tail -2; echo "агентов стратега: $(ls ~/Library/LaunchAgents | grep -c strategist)"
step "строка 2 заново (системная bash) + строка 4"; bash $P/park.sh line3-brewbash; mv ~/Library/LaunchAgents/com.strategist.*.plist "$W/runs/line3-brewbash/" 2>/dev/null
bash $P/upgrade.sh v0.41.11 sys line4-base 2>&1 | grep -v "не исполняем" | grep -vE '^\s+\+ - \[' | head -8
PATH="$W/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin" bash $P/row4.sh line4
bash $P/mode-check.sh | tail -3
step "наборы тестов кандидата"; bash $P/suites.sh
step "готово"
