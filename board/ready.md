> Собрано 2026-11-28 по шаблону ca0d6af7f6.

# 2.3 Готово для передачи Выпускающему: 5

[← общее табло](README.md)

Число и коды согласованы с общим табло. Полные описания открываются по ссылкам на исходный документ. Ссылки закреплены за снимком источника; новые изменения появятся после пересборки.

Сделано целиком и влито в шаблон после выхода 0.42, готово для передачи Выпускающему. Расхождения в строках показывают, что нужно сверить. Полный журнал невыпущенных правок приведён отдельно под спойлером; его число не равно числу результатов.

| Код | Система | Состояние | Источник | Что получает |
|---|---|---|---|---|
| Ц34-02 | IWE по шаблону | готово для передачи | Ц34-02 | DayPlan наполняется ночным конвейером; таблицу дня собирает программа, а не модель |
| Ц37-02 | IWE по шаблону | готово для передачи | Ц37-02 | Таблица из 10 этапов, вход и остановка на каждом, пул недели из карточек |
| Ц78-01 | IWE по шаблону | готово для передачи | Ц78-01 | check-dirty-repos.sh доставлен в корень и шаблон, дедупликация по toplevel |
| Ц82-07 | IWE по шаблону | готово для передачи | Ц82-07 | четыре новых паттерна: раздача параллельно, конвейер, супервизор, рой, плюс спор |
| Ц96-11 | IWE по шаблону | готово для передачи | Ц96-11 | сессия, программа или агент в IWE отдаёт готовое отправление Почтальону и называет адресата по адресной книге (ящик РП, очередь агента); доставка ровно один… |

<details>
<summary>Справка: весь журнал невыпущенных правок</summary>

Записи этого журнала служат результатам разных этапов и новым предложениям. Это не число результатов этапа 2.3. Всего 32 записей: 11 из них служат 11 уже записанным результатам, 0 — 0 новым предложенным результатам ([список](proposed.md)), 21 — служебные правки без видимого результата.

## Записи раздела «Ещё не выпущено»: 32

| Ключ | Вид | Что | Код результата |
|---|---|---|---|
| U-ddb0ee | behavior | (#1699) Обновление больше не теряет молча правки платформенного скилла вне блока USER-SPACE (обращение #1689). Раньше рабочая копия `.claude/skills/<имя>/SKILL.md` заменялась версией шаблона… | служебное |
| U-9de32d | behavior | (#1698) Подготовка к сессии стратегирования (`session-prep`) переносит план и отчёт прошлой недели, план дня и карточки в `archive/` целиком: шаг 8 запроса… | служебное |
| U-ae980d | behavior | (#1696) Проверка секретов при сохранении (`scripts/pre-commit-secret-scan.sh`) больше не пропускает сохранение целиком, если в нём есть файл не в UTF-8: раньше на macOS один такой файл (например… | служебное |
| U-2c074e | behavior | (#1697) Обновление больше не заменяет свой `core.hooksPath` пользователя (например `.husky` или общую папку хуков) на `.githooks` (обращение #1688): раньше свои хуки пользователя — линтеры, проверки… | Ц77-07 |
| U-85fcab | behavior | (#1700) Недельная и месячная сессия стратегирования снова сохраняется без номера рабочего продукта (обращение #1659). После 0.42.0 шаг 0 навыка `/strategy-session` требовал открыть отдельную копию… | служебное |
| U-13a28a | optional | (#1685) Сообщение `scripts/fmt-critical-alert.sh` о проблемах шаблона теперь второй строкой называет действие («Что делать: открыть новую беседу с Claude и сказать «разбери проблемы шаблона IWE»»)… | служебное |
| U-99df23 | behavior | (#1678) Защитная проверка опасных команд (`destructive-guard`) перестала спрашивать пользователя в типичных безопасных случаях: запись во временный файл через переменную (`F=$(mktemp); git show X >… | служебное |
| U-802d20 | optional | Пояснение в начале `scripts/postman-address-book.py` снова совпадает с тем, что выдаёт доставка из авторской версии (путь по умолчанию записан как `{{WORKSPACE_DIR}}`): без этого следующая доставка… | Ц96-11 |
| U-d63b07 | behavior | (#1644) Раздача независимых подзадач нескольким ИИ-агентам одновременно: навык `/peer-fanout` (пробная версия 0.1.0) и программа `scripts/peer-fanout.sh`. Подзадачи пишутся строками… | Ц82-07 |
| U-a38050 | optional | Экспериментальный скилл `/pack-subscribe` (0.3.0): по команде пользователя подключает базу знаний другого автора (пак) только для чтения и включает её в поиск по пакам; витрина берётся из… | Ц72-01, Ц72-04 |
| U-a1970e | behavior | (#1643) Забытые наработки находятся сами: на закрытии недели программа проверки остатка (`scripts/check-repo-residue.sh`, новый шаг 7c-bis навыка `week-close` 1.3.0) ищет то, что пропадёт вместе с… | Ц78-01 |
| U-61ed7a | behavior | (#1641) План дня строится из плана недели (выпуск 0.43, вариант 1 голосования). После того как модель составила утренний план, программа (`scripts/day-open-week-sync-patch.py`: шаг 4.45 открытия дня… | Ц34-02 |
| U-4f22b0 | optional | (#1635) Навык разбора проекта (`/project-analysis`, «проверь мой проект»): агент проходит проект по признакам этапа S0–S3 программы «Личное развитие» (дела и проекты, своя ИИ-среда), ставит уровень… | Ц54-01 |
| U-96a651 | security | (#1703) Live readiness check of the destructive-command guard for any agent (`bash .claude/scripts/guard-readiness.sh begin`, then the two printed commands, then `verify`): the agent itself runs a… | служебное |
| U-a573de | behavior | (#1695) Method skill `find-method` now tells the agent to show its steps 0-8 under separate headings in their order, to name the steps skipped by a branch (reflex, miss) in one line instead of empty… | служебное |
| U-c15639 | behavior | (#1694) Method skills `vdv` and `integration-gate` now tell the agent to show the steps of the method under separate headings in their order and to stop at a step that waits for the user instead of… | служебное |
| U-bec175 | behavior | (#1687) Step-by-step instruction (version 1) for moving IWE skills to Codex in `docs/AGENT-VENDOR-SETUP.md` (links, check, a task by a skill, closing without Claude through the close-check fallback… | служебное |
| U-0ca04b | behavior | (#1686) Method skills `think`, `archgate` and `decompose` now tell the agent to show the stages of the method under separate headings in their order (the "show the stages" line, decision "in the… | служебное |
| U-ce1a61 | behavior | (#1684) The close-check fallback now tells the caller to state in the summary, as checkable facts, which checklist lines are not applicable without the close runner (runner not started, card age and… | служебное |
| U-b97273 | behavior | (#1683) Agents that cannot start a sub-agent (Codex, Kimi Code) now have a fallback for the close-protocol check by a helper with a clean context (R23): `scripts/close_verify_fallback.py` sends the… | служебное |
| U-22babf | behavior | (#1680) Codex now sees the template skills: install and update put one relative symlink per skill into `<workspace>/.agents/skills` (the only folder Codex reads), for every user skill that lists… | служебное |
| U-c319aa | behavior | (#1679) Every skill header now declares who the skill is for (`audience: user\|author`) and which agents run it correctly today (`runs_on: [claude, kimi, codex]`), per the skill inventory approved on… | служебное |
| U-a8d101 | optional | Почтальон: `scripts/postman.py deliver --to WP-N --from "..." --pointer "..." --summary "..."` кладёт заявку в ящик другого РП по адресной книге (`scripts/postman-address-book.yaml`, проверка и… | Ц96-11 |
| U-9d0abc | behavior | (#1633) Рабочий продукт (РП) нельзя перенести в архив, пока в его ящике входящих (`inbox/WP-N/INBOX.md`) есть записи «новое». Перед архивом владелец разбирает каждую запись: переносит её в «Осталось»… | Ц96-13 |
| U-96c6b9 | behavior | Проверка закрытия РП с ящиком входящих (`scripts/wp-inbox-close-gate.sh`, #1681) теперь есть в шаблоне. Хуки хранилища стратегии из #1633 зовут её при каждом коммите и отправке, но в шаблоне её не… | Ц96-13 |
| U-a00bce | optional | (#1704) (WP-526) Описание стартового набора хранилищ в карте домов (`docs/adr/ADR-004-data-domain-map.md`, пункт 3 поправки 27.11) приведено к решению пилота: хранилища событий и личных фактов… | служебное |
| U-2fc387 | optional | (#1701) (WP-526) Карта домов данных (`docs/adr/ADR-004-data-domain-map.md`, `docs/DATA-DOMAINS-REGISTRY.yaml`) приведена к пересмотру решения о структуре 27.11: коды 2.5/2.6 у диалогов сняты (дом… | служебное |
| U-eac956 | behavior | (#1693) Сессия стратегирования начинается с разметки нового: вторым этапом, сразу после открытия, агент по роли Разметчика размечает всё, что появилось в хранилище с прошлой сессии (в первой — всё… | Ц37-02, Ц37-03 |
| U-559801 | docs | (#1690) В журнал пострелизных аудитов (`docs/release-audit-log.md`) записан итог атаки на вышедшую версию 0.42.2: CAUTION, блокирующих находок нет; две существенные находки пути обновления вынесены в… | служебное |
| U-a11f3f | optional | Снимок терминов графа понятий для перевода шаблона на английский обновлён поставщиком терминов перевода (`translation/glossary-snapshot.csv`; WP-617, #1651). | служебное |
| U-cf2fe7 | optional | (#1682) Анонс нового выпуска для подписчиков в Telegram стал короче и понятнее, в стиле заметок о выпуске у вендоров: одна фраза о том, чему посвящён выпуск (например, исправлениям ошибок и… | служебное |
| U-310113 | behavior | (#1654) Мост навыков к DeepSeek Harness (`setup/install-dsh-skills.sh`) стал надёжнее (обращение #1623, находки аудита 0.42.1). Первое: навыки считаются подключёнными, только если после строки-метки… | служебное |

</details>
