> Собрано 2026-11-26 по шаблону a254425bbc.

# 2.3 Готово для передачи Выпускающему: 1

[← общее табло](README.md)

Число и коды согласованы с общим табло. Полные описания открываются по ссылкам на исходный документ. Ссылки закреплены за снимком источника; новые изменения появятся после пересборки.

Сделано целиком и влито в шаблон после выхода 0.42, готово для передачи Выпускающему. Расхождения в строках показывают, что нужно сверить. Полный журнал невыпущенных правок приведён отдельно под спойлером; его число не равно числу результатов.

| Код | Система | Состояние | Источник | Что получает |
|---|---|---|---|---|
| Ц96-11 | IWE по шаблону | готово для передачи | Ц96-11 | сессия, программа или агент в IWE отдаёт готовое отправление Почтальону и называет адресата по адресной книге (ящик РП, очередь агента); доставка ровно один… |

<details>
<summary>Справка: весь журнал невыпущенных правок</summary>

Записи этого журнала служат результатам разных этапов и новым предложениям. Это не число результатов этапа 2.3. Всего 12 записей: 4 из них служат 2 уже записанным результатам, 0 — 0 новым предложенным результатам ([список](proposed.md)), 8 — служебные правки без видимого результата.

## Записи раздела «Ещё не выпущено»: 12

| Ключ | Вид | Что | Код результата |
|---|---|---|---|
| U-99df23 | behavior | (#1678) Защитная проверка опасных команд (`destructive-guard`) перестала спрашивать пользователя в типичных безопасных случаях: запись во временный файл через переменную (`F=$(mktemp); git show X >… | служебное |
| U-802d20 | optional | Пояснение в начале `scripts/postman-address-book.py` снова совпадает с тем, что выдаёт доставка из авторской версии (путь по умолчанию записан как `{{WORKSPACE_DIR}}`): без этого следующая доставка… | Ц96-11 |
| U-ce1a61 | behavior | (#1684) The close-check fallback now tells the caller to state in the summary, as checkable facts, which checklist lines are not applicable without the close runner (runner not started, card age and… | служебное |
| U-b97273 | behavior | (#1683) Agents that cannot start a sub-agent (Codex, Kimi Code) now have a fallback for the close-protocol check by a helper with a clean context (R23): `scripts/close_verify_fallback.py` sends the… | служебное |
| U-22babf | behavior | (#1680) Codex now sees the template skills: install and update put one relative symlink per skill into `<workspace>/.agents/skills` (the only folder Codex reads), for every user skill that lists… | служебное |
| U-c319aa | behavior | (#1679) Every skill header now declares who the skill is for (`audience: user\|author`) and which agents run it correctly today (`runs_on: [claude, kimi, codex]`), per the skill inventory approved on… | служебное |
| U-a8d101 | optional | Почтальон: `scripts/postman.py deliver --to WP-N --from "..." --pointer "..." --summary "..."` кладёт заявку в ящик другого РП по адресной книге (`scripts/postman-address-book.yaml`, проверка и… | Ц96-11 |
| U-9d0abc | behavior | (#1633) Рабочий продукт (РП) нельзя перенести в архив, пока в его ящике входящих (`inbox/WP-N/INBOX.md`) есть записи «новое». Перед архивом владелец разбирает каждую запись: переносит её в «Осталось»… | Ц96-13 |
| U-96c6b9 | behavior | Проверка закрытия РП с ящиком входящих (`scripts/wp-inbox-close-gate.sh`, #1681) теперь есть в шаблоне. Хуки хранилища стратегии из #1633 зовут её при каждом коммите и отправке, но в шаблоне её не… | Ц96-13 |
| U-a11f3f | optional | Снимок терминов графа понятий для перевода шаблона на английский обновлён поставщиком терминов перевода (`translation/glossary-snapshot.csv`; WP-617, #1651). | служебное |
| U-cf2fe7 | optional | (#1682) Анонс нового выпуска для подписчиков в Telegram стал короче и понятнее, в стиле заметок о выпуске у вендоров: одна фраза о том, чему посвящён выпуск (например, исправлениям ошибок и… | служебное |
| U-310113 | behavior | (#1654) Мост навыков к DeepSeek Harness (`setup/install-dsh-skills.sh`) стал надёжнее (обращение #1623, находки аудита 0.42.1). Первое: навыки считаются подключёнными, только если после строки-метки… | служебное |

</details>
