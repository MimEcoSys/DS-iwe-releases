# Инструкция тестировщику на Linux

До сих пор строки протокола на Linux проверял не человек, а ИИ-агент на сервере Цех (`tsekh-1`) — записано так же в `decisions.md`, строка «Тестировщики». Эта инструкция написана для агента, который делает ту же работу: она даёт готовые команды вместо того, чтобы каждый раз собирать их заново по старым сессиям (так появился пробел на rc.15 15.11.2026 — шесть строк перенесли со старых сборок, потому что готового сценария не было). Человек-тестировщик может пользоваться той же инструкцией — язык ниже этого не требует, но скриншотов и разжёвывания, как в [инструкции для Mac](tester-macos.md), здесь нет.

**Где это выполняется.** Одноразовая учётная запись `iwe-test` на отдельной Linux-машине, в стороне от рабочих файлов. Каждый тест начинает с чистой установки — старую `~/IWE` удаляет перед началом, не после.

**Как запускать от имени `iwe-test`.** Готовая обёртка `probes/T` в прошлых папках кандидата задаёт окружение правильно; ниже — тот же набор переменных развёрнуто, без обёртки (она не всегда переживает чистку между кандидатами):

```bash
sudo -u iwe-test -H env -i HOME=/home/iwe-test USER=iwe-test LOGNAME=iwe-test LANG=ru_RU.UTF-8 \
  XDG_RUNTIME_DIR=/run/user/1001 PATH=/home/iwe-test/.npm-global/bin:/home/iwe-test/.local/bin:/run/wrappers/bin:/run/current-system/sw/bin \
  RC=v0.42.0-rc.<K> PREV=v0.41.11 TERM=dumb /run/current-system/sw/bin/bash -lc '<команда>'
```

Если учётной записи нет или `sudo useradd` отказал — её пересоздаёт `probes/ensure-user.sh` (нужна переменная `GUARD_LOG`).

Перед каждой строкой, которая ставит *новую* установку: `sudo -u iwe-test -H rm -rf /home/iwe-test/IWE` — иначе `git clone` в несуществующую, казалось бы, папку откажет, потому что прошлый прогон там уже что-то оставил.

## Строка 1 — чистая установка + строка 9 — фоновые роли

```bash
sudo -u iwe-test -H rm -rf /home/iwe-test/IWE
sudo -u iwe-test -H env -i HOME=/home/iwe-test USER=iwe-test LOGNAME=iwe-test LANG=ru_RU.UTF-8 \
  XDG_RUNTIME_DIR=/run/user/1001 PATH=/home/iwe-test/.npm-global/bin:/home/iwe-test/.local/bin:/run/wrappers/bin:/run/current-system/sw/bin \
  RC=v0.42.0-rc.<K> PREV=v0.41.11 TERM=dumb /run/current-system/sw/bin/bash -lc '
mkdir -p ~/IWE
git clone -q --branch "$RC" https://github.com/TserenTserenov/FMT-exocortex-template.git ~/IWE/FMT-exocortex-template
cd ~/IWE/FMT-exocortex-template
printf "\n\n\n\n\nyy\nn\nn\nn\nn\n" | bash setup.sh
echo "режим: $(cat ~/IWE/.iwe-install-mode 2>/dev/null); манифест: $(jq -r .version update-manifest.json)"
IWE_UPDATE_CHANNEL=rc bash update.sh --check
systemctl --user list-timers --all --no-pager | grep -E "iwe-|extractor"
'
```

**Строка 1 пройдена, если:** установка закончилась без `ERROR`/`ОШИБКА` (кроме ожидаемого `gh repo create failed` — в песочнице нет сети к хранилищу, это не находка), а `update.sh --check` напечатал `Канал поставки: кандидат v0.42.0-rc.<K>` и `ВЕРДИКТ: можно ставить`.
**Строка 9 пройдена, если:** в списке таймеров есть хотя бы одна строка `iwe-*.timer`/`extractor*.timer` и в выводе установки нет слов «вручную»/«manually».

## Строка 2 — обновление со старой версии, строка 4 — откат

Сначала поставить именно `$PREV` (не `$RC`), иначе «обновление» ничего не обновляет:

```bash
sudo -u iwe-test -H rm -rf /home/iwe-test/IWE
sudo -u iwe-test -H env -i HOME=/home/iwe-test USER=iwe-test LOGNAME=iwe-test LANG=ru_RU.UTF-8 \
  XDG_RUNTIME_DIR=/run/user/1001 PATH=/home/iwe-test/.npm-global/bin:/home/iwe-test/.local/bin:/run/wrappers/bin:/run/current-system/sw/bin \
  RC=v0.42.0-rc.<K> PREV=v0.41.11 TERM=dumb /run/current-system/sw/bin/bash -lc '
mkdir -p ~/IWE
git clone -q --branch "$PREV" https://github.com/TserenTserenov/FMT-exocortex-template.git ~/IWE/FMT-exocortex-template
cd ~/IWE/FMT-exocortex-template
printf "\n\n\n\n\nyy\nn\nn\nn\nn\n" | bash setup.sh
echo "своя правка для проверки" > ~/IWE/extensions/test-marker.md
echo "test_marker: ok" >> ~/IWE/params.yaml
printf "y\ny\ny\ny\n" | IWE_UPDATE_CHANNEL=rc bash update.sh
printf "y\ny\ny\ny\n" | IWE_UPDATE_CHANNEL=rc bash update.sh   # повтор — должен сказать «Всё актуально»
echo "правка на месте: $(cat ~/IWE/extensions/test-marker.md)"
# Строка 4 — на том же кандидате, обычный канал (где последний выпуск ещё 0.41.11):
printf "n\n" | bash update.sh   # без подтверждения — должен отказать и назвать это откатом
printf "ROLLBACK\n" | bash update.sh   # с подтверждением — должен откатить до 0.41.11
echo "манифест после отката: $(jq -r .version update-manifest.json); правка на месте: $(cat ~/IWE/extensions/test-marker.md 2>/dev/null)"
'
```

**Строка 2 пройдена, если:** обновление дошло до конца, повтор сказал «Всё актуально», правка в `extensions/` и `params.yaml` цела.
**Строка 4 пройдена, если:** без подтверждения манифест не поменялся и в выводе явно сказано слово «откат»/«ROLLBACK»; после ввода `ROLLBACK` манифест стал `0.41.11`, а правка осталась.

## Строка 10 — навык объяснения изменений, строка 18 — навык поиска метода

Эти два — через `claude -p`, не через `iwe-test` (у него нет своего входа в сервис; используй свою уже открытую сессию, скопировав установку в читаемое для себя место):

```bash
sudo cp -a /home/iwe-test/IWE /tmp/line10-copy && sudo chown -R "$(whoami)":users /tmp/line10-copy
cd /tmp/line10-copy
claude -p "/iwe-update что изменилось в установленном выпуске по сравнению с 0.41.11?" \
  --model opus --dangerously-skip-permissions --output-format stream-json --verbose </dev/null
claude -p "/find-method как вывести закваску для хлеба" --model opus --dangerously-skip-permissions --output-format stream-json --verbose </dev/null
claude -p "/find-method нужно ли мне исследование, чтобы ответить на мой вопрос, или хватит того, что уже известно" --model opus --dangerously-skip-permissions --output-format stream-json --verbose </dev/null
claude -p "/find-method подскажи метод, у меня проблема с проектом" --model opus --dangerously-skip-permissions --output-format stream-json --verbose </dev/null
sudo rm -rf /tmp/line10-copy
```

**Строка 10 пройдена, если:** ответ ссылается на доставленные `CHANGELOG.md` и `docs/releases/<версия>/README.md`, не на основную ветку; нет полей «Цель»/«Как проверить»/«Как откатить»; версия не названа уже вышедшей, если это ещё кандидат.
**Строка 18 пройдена, если:** на «закваску» ответ — «метода нет», без выдумывания; на вопрос про исследование — среди кандидатов есть `RMP.1`, и навык спрашивает, какой взять, а не выбирает сам; на «проблема с проектом» — ровно один уточняющий вопрос до начала поиска.

## Запись результата

Файл отметок — `releases/0.42/tests/rc.<K>/linux-<имя>.yaml` по формату [tests/README.md](../releases/0.42/tests/README.md#формат-файла-отметок) (пример готового файла — `tests/rc.15/linux-claude-code.yaml`). Один `result`/`note` на строку, даже если несколько строк проверялись одной командой. Журналы (вывод команд) — рядом, в `tests/rc.<K>/logs/linux-<имя>/`, без личных данных и секретов — перед запросом на слияние прогнать `python3 ops/pii_scan.py`.

**Перенос отметки со старой сборки запрещён без явной записи** (протокол, раздел после первого абзаца): если код по строке не менялся между сборками, это предложение Выпускающему, не умолчание — без его подтверждения в файле отметок строка считается непройденной на новой сборке.

## Чего эта инструкция не покрывает

Строки 3 (обновление с версии 0.36 — у Разработчика своя копия 0.36, здесь её нет), 5 (открытие/закрытие дня — через `/audit-installation`, нужен более долгий агентский сеанс), 6-8 и 16-17 (Windows и три режима доступа — не Linux), 11-12, 14-15 (решения и живая проверка потребностей — не механическая проверка одной командой). Эти строки либо не относятся к Linux, либо их по-прежнему проверяет Разработчик/Выпускающий отдельно.
