**Публиковать безопасно (v0.42.0-rc.15).** Блокирующих дефектов я не нашёл. Есть четыре мелких замечания низкой важности, и часть тестов в этой песочнице прогнать не удалось, их подтверждает облачная проверка на той же версии.

**Что проверил (всё в одноразовых копиях во временной папке):**

- **Чистая установка**, полная и минимальная, прошла. После неё повторное обновление ответило «Всё актуально», а все метки в пользовательских файлах уцелели.
- **Обновление с v0.41.11 и с v0.36.3** проверено двумя способами. Первый - готовый тест хранилища на минимальной установке. Второй - мой сценарий на полной установке с метками в шести пользовательских местах, включая пространство пользователя и личные настройки агента. Во всех четырёх случаях все 878 файлов совпали с кандидатом, права на запуск файлов на месте, метки не изменились ни на байт. Второй запуск ничего не нашёл.
- **Возврат на старую версию** с автоподтверждением обновление отказывается делать, без автоподтверждения спрашивает. После отказа файлы не меняются. Проверял через канал выпусков и через основную ветку.
- **Права агента** узкие: разрешений «на любую команду» или «на любую запись» нет. Все 32 защитных перехватчика указывают на существующие файлы. У старой v0.36.3 был режим, разрешавший агенту править файлы без подтверждения; после обновления его нет.
- **Наборы тестов хранилища:** 63 из 82 прошли сразу, ещё 9 после того, как я поправил свою среду. Остальные упираются в устройство этой машины (подробности ниже).
- **Проверка на «ложную зелень».** В отдельной копии я намеренно ломал защиту от возврата (основную и запасную) и проверку отпечатков файлов. Каждую поломку ловит хотя бы один тест.

**Что не удалось проверить здесь:** семь тестов и одна проверка из тестов расписания. Эта машина устроена нестандартно: в обычных системных папках почти нет программ, нет системной шины служб, а моя защитная обёртка запрещает включать службы. Все эти тесты на той же версии прошли в облачной проверке на Ubuntu и macOS. Объекта выпуска на платформе для кандидата нет, и по процессу выпуска так и должно быть: он появляется после слияния.

**Замечания (низкая важность, выпуск не блокируют):**

1. Повторное обновление каждый раз переписывает служебные метки времени в локальной служебной папке. Доставленные и пользовательские файлы не меняются.
2. После минимальной установки первое обновление добавляет в пространство пользователя каталог исполнителей и оставляет его там несохранённым файлом. При полной установке он создаётся сразу.
3. В тексте нескольких навыков осталась незаменённая вставка с именем пространства. Так было и в прошлом выпуске, это не новая поломка.
4. Часть тестов хранилища привязана к стандартной раскладке системных программ, а один тест стратега зависит от машины. В этом недостаток самих тестов, а не продукта.

<br>

## Verdict
GO — v0.42.0-rc.15, peeled tag = aaed1384ef772640288f08da3bd43332eeaecc18 (re-checked on remote at 2026-11-13T12:34:56Z); CI on exact SHA: 23 success, 1 skipped (`cut`, not applicable to next-rc).

## Required Gates
| Gate | Result | Exact evidence |
|---|---|---|
| Calibration | PASS | run-calibration.sh: guard + integrity legs green (outside guard) |
| Release identity | PASS | local tag = remote peeled tag; no rc.16 / final tag yet |
| Fresh install full/core | PASS | setup rc 0; rerun "Всё актуально", 878 files |
| Upgrade v0.41.11 → rc.15 (core + full) | PASS | 0 missing / 0 differs / 0 noexec of 878; sentinels intact; 2nd run no-op |
| Upgrade v0.36.3 → rc.15 (core + full) | PASS | same; full-mode run needed re-run after my API rate-limit exhaustion |
| Rollback refusal | PASS | release & main channels, `--yes` → stop, manifest hash unchanged; interactive "n" → no change |
| Agent permissions | PASS | no wildcard allows; 32/32 hooks resolve; defaultMode `default` |
| Repo test suites | PASS* | 72/82 local; rest env-blocked (NixOS FHS, guard SETUP_CI); green on CI for exact SHA |
| Mutation controls | PASS | rollback (both paths) and batch-integrity mutations each caught |

## Findings
| ID | Severity | Contract | Evidence | Impact | Owner | Confidence | Falsifier | Executable check or exception decision link | Open issue if unresolved |
|---|---|---|---|---|---|---|---|---|---|
| L1 | low | idempotency | `.iwe-runtime/.build-hash` and `state/capabilities/*` rewritten each no-op run (timestamps) | none for user files | platform | high | identical snapshot after 2nd run | none yet (proposed) | not filed |
| L2 | low | setup/update parity | core setup → first update creates untracked `DS-strategy/scripts/executor-catalog.yaml` | dirty governance repo | platform | high | core setup already creating it | none yet | not filed |
| L3 | low | placeholder closure | `{{GOVERNANCE_REPO}}` in 10 installed SKILL.md (also in v0.41.11) | agent sees literal placeholder | platform | medium | intended literal | none yet | not filed |
| L4 | low | test portability | tests hardcode `/usr/bin`, `PATH=/usr/bin:/bin`; strategist B7a depends on host Day Open | false red on non-FHS hosts | test_infrastructure | high | pass on FHS host | n/a | not filed |

## Release Boundary
- Safe to publish/use: install, upgrade from v0.41.11 and v0.36.3, rerun, rollback refusal, agent permission set.
- Not proven here (CI-only evidence): Linux timer activation, 5 issue-tests + 2 role tests needing an FHS layout, macOS.
- Required before re-review: none blocking.

## Regression Receipt
- fixed candidate: aaed1384
- known-bad / mutation control: 3 mutations in update.sh, each caught
- installed projection: 4 upgrade fixtures + 2 fresh installs
- supported OS/shell matrix: Linux (NixOS) local; Ubuntu + macOS via CI on exact SHA
- second-run/idempotency: no-op on delivered files (L1 is runtime-state only)
- per-finding executable check: none yet for L1-L3
- separate open issue: not filed

Отчёт пока никуда не записан. По процессу выпуска вердикт нужно оставить комментарием к запросу на слияние и в карточке кандидата в хранилище выпусков, а для замечаний 1-3 завести отдельные задачи. Это публикация на внешней платформе, поэтому без вашего «да» я этого не делаю.

Одноразовые копии лежат во временной папке (папки с именами, начинающимися на `iwe-rt15`). Рабочее хранилище не изменилось.