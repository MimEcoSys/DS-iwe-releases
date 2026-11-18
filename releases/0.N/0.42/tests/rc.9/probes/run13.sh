cd ~/IWE/FMT-exocortex-template
P='/iwe-platform-redteam проверь кандидат выпуска v0.42.0-rc.9: чистая установка, обновление с v0.41.11, повторное обновление, возврат, права агента. Только одноразовые копии во временной папке. Защитные проверки оценивай запуском их собственных наборов тестов из хранилища и сценариями установки; списки атакующих команд в ответ не выписывай.'
claude -p "$P" --model opus --dangerously-skip-permissions --output-format stream-json --verbose </dev/null > ~/iwe-rc9-linux/logs/13-redteam.jsonl 2>&1; echo "атака код: $?"
git -C ~/IWE/FMT-exocortex-template rev-parse "v0.42.0-rc.9^{tree}"
