> Собрано 2026-11-26 по шаблону a254425bbc.

# Выпуск 0.42.2: что добавилось к 0.42.1

Короткая выжимка записей списка изменений шаблона; полный текст — в CHANGELOG.md шаблона.

## 0.42.2 — записей: 32

- [behavior] (#1672) Пункт закрытия дня «Rule-engine FP-stats» (навык `day-close`) при отсутствии `fp-stats.py` больше не пишет «skip: fp-stats.py требует rule-classifier.py»: это неверно, `fp-stats.py` не… — **служебное**
- [behavior] (#1673) Защита от чтения секретных файлов (`.claude/hooks/secret-file-read-block.sh`) снова работает в сессиях Kimi Code: раньше она отказывала на любой вызов чтения и правки файла, и агент оставался… — **служебное**
- [behavior] (#1671) Проверка сессии перед сохранением (`.claude/hooks/session-open-gate.sh`) больше не требует номер РП для личного локального git-репозитория вне рабочей папки IWE (обращение #1658): так… — **служебное**
- [behavior] `scripts/wp-inbox.sh` и `scripts/test-wp-inbox.sh` снова совпадают с авторской версией (не считая подстановки имени хранилища по умолчанию). Шаблонная копия `wp-inbox.sh` разошлась отдельной правкой… — **служебное**
- [behavior] `scripts/iwe-notify` is again a byte-for-byte copy of the author's canon: direct send (`--direct`) and the outcome line from iwe-local-config PR #257 are carried over. (#1660) — **служебное**
- [behavior] The glossary supplier now opens a GitHub issue on failure and comments on it when the same run fails again. The issue lookup passes its exact run key to standalone `jq`. (#1647) — **Ц93-02**
- [behavior] Translation reports match local glossary entries as whole terms in Markdown. The glossary supplies *Ceiling* for «Тупик» when it names the second practitioner state (#1645). — **Ц93-01, Ц93-05**
- [behavior] (#1652) Хост API WakaTime (`api.wakatime.com` вместо `wakatime.com`) теперь во всех программах шаблона, которые обращаются к API, а не только в подсчёте часов закрытия дня (его поправил #1646… — **служебное**
- [behavior] (#1646) Сводка WakaTime для закрытия дня (`scripts/wakatime-day-total.py`) использует адрес `api.wakatime.com`, как и официальный клиент: раньше в сетях без доступа к основному сайту сводка не… — **служебное**
- [behavior] (#1653) Сверка главной копии с опубликованной (`scripts/canon-reconcile-published.sh`) больше не пишет «IWE_RUNTIME used as a directory (legacy caller)» при обычной установке (обращение #1625). Файл… — **служебное**
- [behavior] (#1634) Проверка запуска Кими (`scripts/kimi-standalone-preflight.sh`) теперь выполняет то, чего от неё ждёт скилл `kimi-peer-writer` 1.4.2 (шаг 0а). Раньше она не разбирала аргументы: переданный… — **Ц82-02**
- [behavior] (#1627) Срочное уведомление подписчикам о защитных изменениях (`.github/workflows/notify-security.yml`) больше не пересылает записи журнала изменений как есть. При слиянии 0.42.1 ушли одиннадцать… — **служебное**
- [behavior] (#1629) Создание РП (`scripts/create-wp.sh`) снова держит замок, который обещает навык Артефактора (шаг 2.2): название нового РП сверяется с реестром понятий и родов установленного пака… — **служебное**
- [behavior] (#1626) Запись в авто-память агента через ссылку `memory/` в рабочей папке больше не должна требовать ручного подтверждения в режимах `auto` и `acceptEdits` (обращение #1487): новый обработчик… — **служебное**
- [behavior] Обновление шаблона после вашего ответа «y» теперь само подключает в `.claude/settings.json` новые хуки и разрешения платформы, если слияние не заменяет ваши значения и не снимает отозванные… — **служебное**
- [optional] The glossary supplier can explain the outcome for each requested concept code. Run `python3 scripts/glossary_supplier.py coverage` for the published snapshot. Use `--expected FILE` for selected… — **Ц93-02**
- [optional] `scripts/fetch-glossary-concepts.py`: the glossary exporter reaches the knowledge graph through the platform gateway as a registered machine client (token in `GLOSSARY_EXPORTER_MACHINE_TOKEN`), no… — **служебное**
- [optional] `scripts/iwe-notify --direct`: one direct send to Telegram without looking up the notification gateway at all (row `direct-requested` in `direct-send-log.tsv`, outcome `direct-sent` / `direct-failed`… — **служебное**
- [behavior] Day Open recognizes the plan table and attention section from the installed language catalogs. English and Russian headings route to the same plan prompt and priority check. The updater ships the… — **Ц93-06**
- [docs] Разметка изменений перед выпуском 0.42.2: записи «Ещё не выпущено» разнесены по разделам «Исправлено / Добавлено / Изменено» по решению Выпускающего 24.11.2026; тексты и коды записей не менялись… — **служебное**
- [optional] (#1664) В разделе «Переезд с Claude на другого агента» (`docs/AGENT-VENDOR-SETUP.md`) уточнены шаги Б, В и Г, а абзац «Что работает только в Claude Code» заменён блоком «Первый день с новым агентом»… — **служебное**
- [optional] (#1663) Инструкция по подключению агента (`docs/AGENT-VENDOR-SETUP.md`) получила раздел «Переезд с Claude на другого агента»: выбор агента (Codex, Kimi Code, Hermes, другие файловые агенты, модели… — **служебное**
- [behavior] Автоматическая доставка из авторского источника (template-sync.sh): обновлены .claude/skills/mentor-participant-brief/SKILL.md (#1650). — **служебное**
- [behavior] English installation scripts keep their executable bits when the translated tree is published. Full assembly preserves the Git metadata used to publish the draft. (#1649) — **Ц93-06**
- [behavior] Автоматическая доставка из авторского источника (template-sync.sh): обновлены scripts/lib/process-identity.sh (#1638). — **служебное**
- [optional] `scripts/session-guard.sh`: при наличии `scripts/lib/process-identity.sh` (доставляется отдельно, #1638) каждая запись семафора сессии дополнительно получает строку `pid_start_id:` рядом с… — **служебное**
- [optional] Снимок терминов графа понятий для перевода шаблона на английский обновлён поставщиком терминов перевода (`translation/glossary-snapshot.csv`; WP-617, #1616). — **служебное**
- [docs] (#1636) Каталог навыков (`.claude/skills-catalog.yaml`) пересобран программой `scripts/generate-skills-catalog.sh`: с 25.09 его не пересобирали, и в нём не было трёх уже выпущенных навыков - подбора… — **служебное**
- [docs] (#1601) Описание процесса выпуска (`docs/RELEASE-PROCESS.md`) называет настоящие пути в репозитории выпусков: `releases/<X>.N/<N>/protocol.md`, папку кандидата `tests/rc.<K>/` и… — **служебное**
- [behavior] (#1628) Скиллы пир-сессий `peer-conversation` (1.5.7 → 1.8.0) и `kimi-peer-writer` (1.3.0 → 1.4.2) получили текущую версию автора: одна редакция для установки автора и установки из шаблона. Файлы… — **Ц82-02**
- [docs] (#1624) В журнал пострелизных аудитов (`docs/release-audit-log.md`) записан итог проверки выпуска 0.42.1: атака на проверку опасных команд — GO, проверка перед слиянием — CAUTION с оговорками… — **служебное**
- [behavior] (#1622) В ручной словарь перевода записана роль «Верификатор» → Verifier (пилот утвердил 20.11, WP-620). Станция «Проверка» остаётся Verification: Проверка — это верификация (учёт требований… — **служебное**
