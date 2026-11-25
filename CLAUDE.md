# DS-iwe-releases — правила для ИИ-агентов

Открытый репозиторий команды выпуска шаблона IWE. Что здесь и где что лежит — в [README.md](README.md); раскладка следует принципам [DP.METHOD.265](https://github.com/MimEcoSys/PACK-digital-platform/blob/main/pack/digital-platform/03-methods/DP.METHOD.265-repository-structure-principles.md).

## Обязательно загружай

Перед работой в роли выпуска — прочитай [method/pipeline.md](method/pipeline.md), [method/functional-modular.md](method/functional-modular.md) и инструкцию своей роли: Выпускающему — [team/release-lead/start.md](team/release-lead/start.md) и [team/release-lead/instruction.md](team/release-lead/instruction.md), затем `README.md` в папке текущего выпуска (номер — на странице [NOW.md](NOW.md)); тестировщику — [team/tester/README.md](team/tester/README.md). Роль и метод — в Паке (DP.ROLE.120); расходится — прав Пак.

## Обязательно

- **Без личных данных.** Людей указывать только логином GitHub; почту, телефоны, обращения пользователей с их данными не писать. Обращение пользователя — пересказом без имени. Секретов и ключей здесь нет и не будет.
- **Только свой файл роли.** Агент Разработчика правит `board/developer-links.yaml`, `board/developer-sources.yaml`, `releases/developer-handoff.yaml`, `releases/backlog.md`, `releases/index.yaml`, `README.md` и `checklist.md` папки выпуска, программы в `tools/`, Выпускающего — `decisions.md` папки выпуска, тестировщика — своя папка кандидата `tests/rc.<K>/` (файл отметок, отчёт атаки, журналы). Чужой файл не трогать. Папка выпуска — `releases/<X>.N/<N>/`, где `<X>` — первое число версии (`releases/0.N/0.42/`).
- **Собранное программой руками не править:** `NOW.md`, `board/` (кроме двух файлов Разработчика), `releases/INDEX.md`, `releases/HISTORY.md`, `releases/NEXT.md`, `releases/catalog.json`, `shipped.md` и `candidates.md` в папках выпусков. Собирает [tools/build_board.py](tools/build_board.py) вместе с [tools/release_catalog.py](tools/release_catalog.py). `NOW.md` и `board/` — оперативное, переписываются целиком; папка выпуска — накопительное, после выхода выпуска не меняется.
- **Статус — только из закрытого списка** в [method/board-rules.md](method/board-rules.md), раздел «Стадии и статусы». Новый статус — сначала правка этой страницы через запрос на слияние.
- **Все правки — через запрос на слияние**, не прямой отправкой в main.
- **Новый файл или папка** — сначала назначение и писатель по [DP.METHOD.265](https://github.com/MimEcoSys/PACK-digital-platform/blob/main/pack/digital-platform/03-methods/DP.METHOD.265-repository-structure-principles.md), запись в [method/functional-modular.md](method/functional-modular.md) и оглавление папки.
- Номера целей и коды результатов не придумывать: цели — из «Целей и сценариев» (DP.MAP.005), коды — из «Состояния по целям».
