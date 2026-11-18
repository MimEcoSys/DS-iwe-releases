cd ~/IWE
run(){ claude -p "/find-method $2" --model opus --dangerously-skip-permissions --output-format stream-json --verbose </dev/null > ~/iwe-rc7-linux/logs/18-$1.jsonl 2>&1; echo "$1 код: $?"; }
run N1 "как вывести закваску для хлеба"
run N3 "нужно ли мне исследование, чтобы ответить на мой вопрос, или хватит того, что уже известно"
run L4 "подскажи метод, у меня проблема с проектом"
