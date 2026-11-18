cd ~/IWE/FMT-exocortex-template
P='/iwe-platform-redteam проверь кандидат выпуска v0.42.0-rc.6: чистая установка, обновление с v0.41.11, возврат, права агента, защитные проверки. Только одноразовые копии во временной папке.'
claude -p "$P" --model opus --dangerously-skip-permissions --output-format stream-json --verbose </dev/null > ~/iwe-rc6-linux/logs/13-redteam.jsonl 2>&1; echo "атака код: $?"
git -C ~/IWE/FMT-exocortex-template rev-parse "v0.42.0-rc.6^{tree}"
