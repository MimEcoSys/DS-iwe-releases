> Собрано 2026-11-24 по шаблону 75cb2ff9e7.

# 2.3 Готово для передачи Выпускающему: 1

[← общее табло](README.md)

Число и коды согласованы с общим табло. Полные описания открываются по ссылкам на исходный документ. Ссылки закреплены за снимком источника; новые изменения появятся после пересборки.

Сделано целиком и влито в шаблон после выхода 0.42, готово для передачи Выпускающему. Расхождения в строках показывают, что нужно сверить. Полный журнал невыпущенных правок приведён отдельно под спойлером; его число не равно числу результатов.

| Код | Система | Состояние | Источник | Что получает |
|---|---|---|---|---|
| Ц96-11 | IWE по шаблону | готово для передачи | Ц96-11 | сессия, программа или агент в IWE отдаёт готовое отправление Почтальону и называет адресата по адресной книге (ящик РП, очередь агента); доставка ровно один… |

<details>
<summary>Справка: весь журнал невыпущенных правок</summary>

Записи этого журнала служат результатам разных этапов и новым предложениям. Это не число результатов этапа 2.3. Всего 31 записей: 10 из них служат 7 уже записанным результатам, 0 — 0 новым предложенным результатам ([список](proposed.md)), 21 — служебные правки без видимого результата.

## Записи раздела «Ещё не выпущено»: 31

| Ключ | Вид | Что | Код результата |
|---|---|---|---|
| U-802d20 | optional | Пояснение в начале `scripts/postman-address-book.py` снова совпадает с тем, что выдаёт доставка из авторской версии (путь по умолчанию записан как `{{WORKSPACE_DIR}}`): без этого следующая доставка… | Ц96-11 |
| U-f4ec1d | behavior | `scripts/wp-inbox.sh` и `scripts/test-wp-inbox.sh` снова совпадают с авторской версией (не считая подстановки имени хранилища по умолчанию). Шаблонная копия `wp-inbox.sh` разошлась отдельной правкой… | служебное |
| U-f3dd00 | behavior | `scripts/iwe-notify` is again a byte-for-byte copy of the author's canon: direct send (`--direct`) and the outcome line from iwe-local-config PR #257 are carried over. (#1660) | служебное |
| U-25803a | behavior | The glossary supplier now opens a GitHub issue on failure and comments on it when the same run fails again. The issue lookup passes its exact run key to standalone `jq`. (#1647) | Ц93-02 |
| U-2736b6 | behavior | Translation reports match local glossary entries as whole terms in Markdown. The glossary supplies *Ceiling* for «Тупик» when it names the second practitioner state (#1645). | Ц93-01, Ц93-05 |
| U-df4851 | behavior | (#1652) Хост API WakaTime (`api.wakatime.com` вместо `wakatime.com`) теперь во всех программах шаблона, которые обращаются к API, а не только в подсчёте часов закрытия дня (его поправил #1646… | служебное |
| U-9e9af6 | behavior | (#1646) Сводка WakaTime для закрытия дня (`scripts/wakatime-day-total.py`) использует адрес `api.wakatime.com`, как и официальный клиент: раньше в сетях без доступа к основному сайту сводка не… | служебное |
| U-2417cb | behavior | (#1653) Сверка главной копии с опубликованной (`scripts/canon-reconcile-published.sh`) больше не пишет «IWE_RUNTIME used as a directory (legacy caller)» при обычной установке (обращение #1625). Файл… | служебное |
| U-77d368 | behavior | (#1634) Проверка запуска Кими (`scripts/kimi-standalone-preflight.sh`) теперь выполняет то, чего от неё ждёт скилл `kimi-peer-writer` 1.4.2 (шаг 0а). Раньше она не разбирала аргументы: переданный… | Ц82-02 |
| U-e0430e | behavior | (#1627) Срочное уведомление подписчикам о защитных изменениях (`.github/workflows/notify-security.yml`) больше не пересылает записи журнала изменений как есть. При слиянии 0.42.1 ушли одиннадцать… | служебное |
| U-f7aadd | behavior | (#1629) Создание РП (`scripts/create-wp.sh`) снова держит замок, который обещает навык Артефактора (шаг 2.2): название нового РП сверяется с реестром понятий и родов установленного пака… | служебное |
| U-815c6b | behavior | (#1626) Запись в авто-память агента через ссылку `memory/` в рабочей папке больше не должна требовать ручного подтверждения в режимах `auto` и `acceptEdits` (обращение #1487): новый обработчик… | служебное |
| U-a8d101 | optional | Почтальон: `scripts/postman.py deliver --to WP-N --from "..." --pointer "..." --summary "..."` кладёт заявку в ящик другого РП по адресной книге (`scripts/postman-address-book.yaml`, проверка и… | Ц96-11 |
| U-99e11d | optional | The glossary supplier can explain the outcome for each requested concept code. Run `python3 scripts/glossary_supplier.py coverage` for the published snapshot. Use `--expected FILE` for selected… | Ц93-02 |
| U-9af040 | optional | `scripts/fetch-glossary-concepts.py`: the glossary exporter reaches the knowledge graph through the platform gateway as a registered machine client (token in `GLOSSARY_EXPORTER_MACHINE_TOKEN`), no… | служебное |
| U-c8c8fb | optional | `scripts/iwe-notify --direct`: one direct send to Telegram without looking up the notification gateway at all (row `direct-requested` in `direct-send-log.tsv`, outcome `direct-sent` / `direct-failed`… | служебное |
| U-ed137c | behavior | Day Open recognizes the plan table and attention section from the installed language catalogs. English and Russian headings route to the same plan prompt and priority check. The updater ships the… | Ц93-06 |
| U-9d0abc | behavior | (#1633) Рабочий продукт (РП) нельзя перенести в архив, пока в его ящике входящих (`inbox/WP-N/INBOX.md`) есть записи «новое». Перед архивом владелец разбирает каждую запись: переносит её в «Осталось»… | Ц96-13 |
| U-d4adfc | docs | Разметка изменений перед выпуском 0.42.2: записи «Ещё не выпущено» разнесены по разделам «Исправлено / Добавлено / Изменено» по решению Выпускающего 24.11.2026; тексты и коды записей не менялись… | служебное |
| U-653331 | optional | (#1664) В разделе «Переезд с Claude на другого агента» (`docs/AGENT-VENDOR-SETUP.md`) уточнены шаги Б, В и Г, а абзац «Что работает только в Claude Code» заменён блоком «Первый день с новым агентом»… | служебное |
| U-f6fa57 | optional | (#1663) Инструкция по подключению агента (`docs/AGENT-VENDOR-SETUP.md`) получила раздел «Переезд с Claude на другого агента»: выбор агента (Codex, Kimi Code, Hermes, другие файловые агенты, модели… | служебное |
| U-fa5819 | behavior | Автоматическая доставка из авторского источника (template-sync.sh): обновлены .claude/skills/mentor-participant-brief/SKILL.md (#1650). | служебное |
| U-4ddcaf | behavior | English installation scripts keep their executable bits when the translated tree is published. Full assembly preserves the Git metadata used to publish the draft. (#1649) | Ц93-06 |
| U-4aeab6 | behavior | Автоматическая доставка из авторского источника (template-sync.sh): обновлены scripts/lib/process-identity.sh (#1638). | служебное |
| U-5a95c2 | optional | `scripts/session-guard.sh`: при наличии `scripts/lib/process-identity.sh` (доставляется отдельно, #1638) каждая запись семафора сессии дополнительно получает строку `pid_start_id:` рядом с… | служебное |
| U-eeb1d6 | optional | Снимок терминов графа понятий для перевода шаблона на английский обновлён поставщиком терминов перевода (`translation/glossary-snapshot.csv`; WP-617, #1616). | служебное |
| U-56d7a2 | docs | (#1636) Каталог навыков (`.claude/skills-catalog.yaml`) пересобран программой `scripts/generate-skills-catalog.sh`: с 25.09 его не пересобирали, и в нём не было трёх уже выпущенных навыков - подбора… | служебное |
| U-dccdb3 | docs | (#1601) Описание процесса выпуска (`docs/RELEASE-PROCESS.md`) называет настоящие пути в репозитории выпусков: `releases/<X>.N/<N>/protocol.md`, папку кандидата `tests/rc.<K>/` и… | служебное |
| U-c7bbce | behavior | (#1628) Скиллы пир-сессий `peer-conversation` (1.5.7 → 1.8.0) и `kimi-peer-writer` (1.3.0 → 1.4.2) получили текущую версию автора: одна редакция для установки автора и установки из шаблона. Файлы… | Ц82-02 |
| U-5c024f | docs | (#1624) В журнал пострелизных аудитов (`docs/release-audit-log.md`) записан итог проверки выпуска 0.42.1: атака на проверку опасных команд — GO, проверка перед слиянием — CAUTION с оговорками… | служебное |
| U-ad2f4e | behavior | (#1622) В ручной словарь перевода записана роль «Верификатор» → Verifier (пилот утвердил 20.11, WP-620). Станция «Проверка» остаётся Verification: Проверка — это верификация (учёт требований… | служебное |

</details>
