# Бэклог выпусков

Единый список того, что **обещано людям или отложено** и должно попасть в будущий выпуск шаблона. Здесь не состав выпуска и не решения о нём: состав — [форма решений](../method/pipeline.md) папки выпуска и [план выпуска](0.N/0.43/plan.md) (то, что выбрали голосованием). Здесь — то, что иначе потерялось бы между выпусками: исправления по обращениям пользователей, отложенные правки, просьбы проверить.

Пишет Разработчик, исход «берём в выпуск» решает Выпускающий. Разбирается на каждом выпуске — [действие 1г общего чек-листа](../method/release-checklist.md). Строка закрыта, когда у неё исход «вышло в 0.N.K» или «снято: причина»; пока исхода нет, она открыта.

Правило записи: **обещание автору обращения записывается сюда в тот же ход, в который оно написано на GitHub.** Комментарий «планируем в 0.N» без строки здесь не пишется.

## Открыто

| Что | Откуда | Куда | Что сделать | Исход |
|---|---|---|---|---|
| [#1659](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1659): недельная сессия стратегирования не может сохраниться без номера РП | комментарий автору (`boklashov`) 25.11.2026 «планируем в 0.43» | 0.43 | научить программу сессий открывать отдельную копию без номера РП (правка ядра программы сессий); простое добавление причины в список не решает | открыто |
| [#1670](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1670): поиск секретов молча пропускает файл не в UTF-8 на macOS | комментарий автору (`litvegpt`) 25.11.2026 «планируем в 0.43» | 0.43 | исправить защитную программу `pre-commit-secret-scan.sh`, проверить на macOS | открыто |
| [#1674](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1674): подготовка к сессии стратегирования не сохраняет удаление старых путей | комментарий автору (`277zdwvw9f-pixel`) 25.11.2026 «планируем в 0.43» | 0.43 | рассмотреть оба предложенных исправления: `git mv` в шаге 8 `session-prep.md` и предупреждение о строках ` D` после сценария в `strategist.sh` | открыто |
| #1633 (U-9d0abc), #1662 (U-a8d101), #1665 (U-802d20) | решение Выпускающего 24.11.2026, отложены из 0.42.2 | сразу после выхода 0.42.2 | вернуть в основную ветку: #1633 вместе с [FMT #1668](https://github.com/TserenTserenov/FMT-exocortex-template/pull/1668), затем #1662, #1665 (действие 17а); проверка `tools/check_decisions.py --after-release` | открыто |
| [#1657](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1657) | комментарий автору (`art-artemov`) 25.11.2026: просьба подтвердить | после выхода 0.42.2 | получить ответ автора, что в Kimi Code заработало (живой прогон мы не делали); закрыть обращение | открыто |
| [#1623](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1623), [#1586](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1586), [#1578](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1578), [#1577](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1577), [#1547](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1547), [#1478](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1478), [#1473](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1473), [#1468](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1468), [#1447](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1447), [#1359](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1359), [#1124](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1124), [#836](https://github.com/TserenTserenov/FMT-exocortex-template/issues/836) | сверка 24.11.2026: не берём в 0.42.2 (Windows не обещается, остальное — улучшения и документация); исходы оценены по тексту, не по коду | не назначен | решить по каждому: выпуск, «не берём» с причиной или закрыть; написать автору; сроков автору не обещали | автору ответ не написан |
| После выхода 0.42.2: [#1658](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1658), [#1656](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1656), [#1625](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1625), [#1606](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1606), [#1487](https://github.com/TserenTserenov/FMT-exocortex-template/issues/1487) | в составе 0.42.2; автору #1658 и #1656 написано «взято» 25.11.2026 | 0.42.2 | написать «вышло в 0.42.2» со ссылкой на описание выпуска и закрыть (действие 26) | открыто |

## Закрыто

Пока пусто. Закрытую строку переносят сюда с исходом и датой, не удаляют.
