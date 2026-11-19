# Функционально-модульное описание

Две стороны одного конвейера. **Функции** — что делается и какой ролью ([схема](pipeline.md)). **Модули** — какая программа или какой файл это исполняет и хранит. Таблицы ниже связывают их, чтобы по функции найти файл и по файлу — функцию.

## Функции → модули

| Шаг | Функция | Роль | Вход | Выход | Модуль |
|---|---|---|---|---|---|
| 1 | Снимок | Выпускающий называет, Разработчик запускает | вершина основной ветки шаблона | ветка `release/v<N>` | шаблон: `Release Candidate`, режим `cut` |
| 1–2 | Кандидаты выпуска | Разработчик | `releases/developer-handoff.yaml`, список изменений шаблона | `candidates.md` папки выпуска | [tools/build_board.py](../tools/build_board.py) |
| 2 | Поля и коды | Разработчик, Разметчик кодов | раздел версии в `CHANGELOG.md` шаблона | каждая запись с полями и кодом результата | шаблон: `check-changelog-fields.py`; связи — `board/developer-links.yaml` |
| 3 | Отбор состава | Выпускающий | `candidates.md` | взято / отложено | `decisions.md` папки выпуска; проверка — [tools/check_decisions.py](../tools/check_decisions.py) |
| 4 | Сборка-кандидат | Разработчик | ветка выпуска | метка `v<N>-rc.<K>` и дерево | шаблон: `Release Candidate`, режим `next-rc` |
| 5 | Проверки на кандидате | программы, Рецензент, Аудитор кода, тестировщики, проверяющий red team | дерево кандидата, `protocol.md` | отметки и вердикт | `tests/rc.<K>/` папки выпуска; отчёт — [tools/release-checklist.py](../tools/release-checklist.py) |
| 5 | Стенд для прогонов (проект) | программа | метка и дерево кандидата, разметка строк протокола «машина» | `tests/rc.<K>/stand.yaml` | описание — [run-stand.md](run-stand.md); программы пока нет |
| 6 | Сверка доказательств | Рецензент доказательств | отметки, вердикт, дерево | «сходится» или расхождение | `check_decisions.py --require-final --rc-tree` |
| 7 | Согласование и выпуск | Выпускающий, затем `release.yml` | итог проверки | метка `v<N>` | `decisions.md`, строка «Итог»; шаблон: `release.yml` |
| 8 | После выхода | Выпускающий, Разработчик | вышедший выпуск | «держим» или откат; `shipped.md`; пересобранное табло | `build_board.py`, `index.yaml` |
| — | Табло результатов IWE | Разработчик запускает программу | закреплённые входы (`board/developer-sources.yaml`), связи (`board/developer-links.yaml`) | `board/README.md`, страницы стадий, сверка полноты, `board/snapshot.yaml` | [tools/build_board.py](../tools/build_board.py) |
| — | Результаты и статистика IWE | программа | табло, метки и история основной ветки шаблона (`fmt-tags.txt`, `fmt-history.txt` среди входов) | `board/stats.md` | [tools/iwe_stats.py](../tools/iwe_stats.py) |
| — | Что сейчас, история, планы | программа | `releases/index.yaml`, табло, папки выпусков | `NOW.md`, `releases/HISTORY.md`, `releases/NEXT.md`, `releases/INDEX.md`, `releases/catalog.json` | `build_board.py` вместе с [tools/release_catalog.py](../tools/release_catalog.py) |
| — | Проверка перед слиянием | автоматика GitHub | запрос на слияние | пропуск или отказ | [.github/workflows/publication-gate.yml](../.github/workflows/publication-gate.yml), [.github/scripts/pii_scan.py](../.github/scripts/pii_scan.py) |

## Что роли передают друг другу

| От кого → кому | Что передаётся | В каком виде |
|---|---|---|
| Разработчик → Выпускающему | правки, готовые к выпуску: что получает пользователь, как проверить, как откатить, риск, рекомендация | запись в `releases/developer-handoff.yaml` → программа собирает `candidates.md` |
| Разработчик → табло | какая запись списка изменений служит какому результату; из каких версий входов собрано табло | `board/developer-links.yaml`, `board/developer-sources.yaml` |
| Выпускающий → Разработчику | состав, блокирующие строки, принятые оговорки, «выпускаем» | `decisions.md` папки выпуска |
| Тестировщик, проверяющий red team → Выпускающему | отметки по строкам протокола, вердикт атаки, журналы | файлы в `tests/rc.<K>/` папки выпуска |
| Программа → всем | что сейчас, что сделано, что будет, табло | `NOW.md`, `releases/HISTORY.md`, `releases/NEXT.md`, `board/README.md` |

## Где что лежит

```
README.md               что это и зачем, карта вопросов                       человек
CLAUDE.md               правила для ИИ-агентов                                 человек
NOW.md                  что сейчас                                             программа
method/                 как должно работать (эта папка)                        Разработчик с Выпускающим
team/                   роли, как присоединиться, инструкции людям            Разработчик с Выпускающим
  developer/ release-lead/ tester/ code-marker/ red-team/
  release-reviewer/ code-auditor/ evidence-reviewer/ owner/   по папке на роль, в каждой README.md
releases/               выпуски
  index.yaml            список версий                                          Разработчик
  developer-handoff.yaml  передача Выпускающему                                Разработчик
  INDEX.md HISTORY.md NEXT.md catalog.json   списки выпусков                   программа
  <X>.N/<N>/            папка выпуска (схема — releases/README.md)
board/                  табло результатов IWE
  README.md             общее табло                                            программа
  stats.md              результаты и статистика крупными цифрами               программа
  plan.md … deferred.md страницы стадий; completeness.md — сверка полноты     программа
  snapshot.yaml         снимок источников                                      программа
  developer-links.yaml  связи записей с результатами                           Разработчик
  developer-sources.yaml  закреплённые входы последней сборки                  Разработчик
tools/                  программы: сборщик табло, статистика, каталог выпусков,
                        проверка решений, чек-лист, раскладка путей и их тесты  Разработчик
.github/                проверка перед слиянием, владельцы файлов, поиск личных данных
```

Все пути, которые читают и пишут программы, собраны в одном месте — [tools/layout.py](../tools/layout.py) (оглавление папки — [tools/README.md](../tools/README.md)). Раскладка следует принципам [DP.METHOD.265](https://github.com/MimEcoSys/PACK-digital-platform/blob/main/pack/digital-platform/03-methods/DP.METHOD.265-repository-structure-principles.md): у каждой папки одно назначение, программы с их тестами собраны в одной папке `tools/`, потому что табло и каталог выпусков собираются одним конвейером и используют общую раскладку путей.

## Команды

| Что | Команда (из папки репозитория) |
|---|---|
| Полная пересборка табло | `python3 tools/build_board.py --src <папка входов> --source-date <дата входов> --repo .` — порядок сбора входов в `board/developer-sources.yaml` |
| Только «что сейчас» и каталог | `python3 tools/build_board.py --repo . --user-board-only` |
| Проверить, что собранное не устарело | `python3 tools/build_board.py --repo . --check-user-board` |
| Проверить ссылки всех страниц | `python3 tools/build_board.py --repo . --check-links` |
| Проверить решения выпуска | `python3 tools/check_decisions.py` |
| Тесты программ | `python -m pytest -q tools` |
