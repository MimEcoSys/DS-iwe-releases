> Собрано 2026-11-06 по шаблону 1a4b9afc47.

# Выпуски до 0.36 включительно

Короткая выжимка записей списка изменений шаблона; полный текст — в CHANGELOG.md шаблона.

## 0.36.3 — записей: 30

- [—] `8ab5386` feat(wp499): Ф16 — доставка iwe-local-gateway в шаблон: setup/optional/setup-local-gateway.sh (клон на пин v0.1.0, сборка, запуск демона, блок для .mcp.json), правка…
- [—] `813dbbf` fix(wp499): Ф16 фиксы по независимому ревью — liveness-проба демона (сокет-файл переживает ребут), lock против гонки двух запусков, скрипт добавлен в update-manifest.json (доставка…
- [—] `3cd8d01` feat(wp-429-f6.5): пре-фильтры фабрикации ID и cross-report дублей в extractor.sh
- [—] `9fcc6d9` feat(apply-captures): Ф6.4 фасетный классификатор (шаг 4в-0) + routing.yaml как SoT для 4в
- [—] `35944f3` feat(wp505): create-wp.sh --state (обязателен при реестре осей) + --hypothesis, ячейка «Ставка»; /wp-new и protocol-open — ставка и гипотеза в ритуале создания РП
- [—] `c34f8ab` chore(release): weekly auto-bump to v0.36.2
- [—] `da9faad` sync: iwe-agent-dispatcher.py from DS-my-strategy (WP-503 Ф5.1/5.2)
- [—] `c516145` security: WP-500 Ф1 — синхронизировать фикс утечки трейсов в облако
- [—] `5e13c05` docs(changelog): thank vakungur (#312/#311/#310) and VxxxlBxxxxv (#308)
- [—] `cd92300` fix(wp499): Ф16 хвост — bump iwe-local-gateway пин к v0.1.1 (демон писал pid всегда в ~/.iwe/gateway.pid независимо от кастомного сокета, issue TserenTserenov/iwe-local-gateway#1; фикс…
- [—] `7717c76` fix(mcp): утечка личного пути автора в .mcp.json (→ {{HOME_DIR}}) + скилл personal-guide-render указывал на несуществующий инструмент локального шлюза
- [—] `0873dde` fix: promote day-open-pipeline.sh — facts_digest guard fix (WP-484)
- [—] `cef6352` fix(hooks): revert WeekPlan section-list gate — broke 23/24 real WeekPlans (issue #318 hotfix)
- [—] `fe0b908` fix(setup): githooks provisioning for DS-strategy + WeekPlan validator drift (#317, #318)
- [—] `022d290` fix(apply-captures): привести гейт 4а.1 к дословному эталону из bug-файла
- [—] `c0113ce` fix(apply-captures): гейт Forces/Bias-Annotation для новых карточек методов
- [—] `afdce30` fix(create-wp): три дефекта в WeekPlan-writer и slug-обрезке
- [—] `16edace` fix(setup): понятная подсказка вместо traceback при отсутствии PyYAML (шаг 4e)
- [—] `a73e9e8` fix(cloud-scheduler): явный skip backup-memory job, если exocortex/ в .gitignore
- [—] `d3f63d2` fix(seed-drift): синхронизировать seed-копию day-open-scaffold.sh
- [—] `877c587` fix(ci): устранить 2 красных джоба на main — hardcode-паттерн + badge-дрейф
- [—] `4303c8e` fix(template): genericize username in examples + narrow author-check exemption
- [—] `c7a0494` fix(#315,#316): регрессии из ee0795c — независимый код-ревью субагентом
- [—] `be48c84` fix(template): de-link private-repo references + close case-sensitivity gap in validator
- [—] `ffed001` fix(template): remove author-specific DS-my-strategy leak (validate-template FAIL)
- [—] `ee0795c` fix(#316,#315,#314): issue funnel — 3 бага свежих установок
- [—] `9324f54` fix(review): 2 regressions in e190ba2 found by independent code review
- [—] `c4e4152` fix: добавить поддержку колонки «Ставка» в create-wp.sh (WP-505)
- [—] `e190ba2` fix(#312,#311,#308): issue funnel — устаревшая инструкция, ложный блок гейта, author-leak на ADR + exec-bit
- [—] `c02f663` fix(strategist): table_to_list() column mapping — DayPlan/WeekPlan diverged formats

## 0.36.2 — записей: 0


## 0.36.1 — записей: 10

- [—] feat(wp483): sync guide-kit v0.1.2 into template (снимок Ф9 система №16 + слияние приоритета Портного + degree-контекст)
- [—] `4484b4c` feat(skill-promote): защита L3-констант через inline-маркер (WP-5)
- [—] `5aabac2` feat(wp483): sync guide-kit v0.1.1 into template
- [—] `c40b041` docs(changelog): thank SDaiBots (#217/#221/#224/#228), AONarchuk (#215), trover97 (#218) — пропущены в прошлых раундах благодарностей
- [—] `b08403d` chore: release 0.36.0
- [—] `fb9afa6` docs(changelog): regenerate [Unreleased] after guide-kit v0.1.1 sync
- [—] `3f91860` fix(release): sync README version badge to 0.36.0
- [—] `b0f675b` fix(scripts): env-fallback для GOVERNANCE_REPO в generate-hot-files-list.sh
- [—] `1b29b19` fix(strategist): убрать хардкод DS-strategy в DAY_OPEN_PIPELINE (регрессия 238a5c1)
- [—] `5cd5695` fix(roles): runtime-резолв путей в extractor/synchronizer вместо build-time плейсхолдеров

## 0.36.0 — записей: 169

- [—] `5aabac2` feat(wp483): sync guide-kit v0.1.1 into template
- [—] `ae900f3` feat(wp485): доставить 4 скрипта Kimi Standalone из root в шаблон
- [—] `262c313` feat(l1-skills): добавить USER-SPACE маркеры в agent-fault и audit-installation
- [—] `017235c` feat(wp483-f4): deliver guide-kit v0.1.0 to the template (demo catalog + work_section)
- [—] `fee0f85` feat(template-sync): промоция слим-ядра CLAUDE.md + hot-каркаса из авторского IWE
- [—] `8c9c305` feat(wp415): provenance-free iwesys publication
- [—] `63c2ec5` feat(wp415): Cyrillic gate — publish-to-iwesys rejects any Cyrillic
- [—] `58b8602` feat(residency-gate): mandatory schema_version + pilot-approved pre-grant.yaml (WP-476 F1 cond. 2/6, pilot decisions 2026-07-16)
- [—] `078f66c` feat(wp483-f4): guide-kit → template sync tooling (vendored-by-tag model)
- [—] `d450902` feat(day-close): token-discipline execution model — digest + subagent phases (#234)
- [—] `f4ca48e` feat(manifest): update-manifest.local.json — fork-local exclusions survive update.sh (#247)
- [—] `c65f9d0` feat(WP-450 S-50): promote hot-files.list auto-discovery to FMT
- [—] `33ebbf9` feat(WP-450): promote verify-context-budget.sh to FMT (S-50)
- [—] `4bebc58` feat: complete gate-metrics.sh promotion — manifest coverage + changelog
- [—] `39421f0` feat(strategist): вызвать week-open-day-section-patch после session-prep (WP-484 Ф3)
- [—] `dd011fa` feat(hindsight): deliver hindsight_trigger.py + hindsight_adapter.py, closing L2 integration gap (#252)
- [—] `046aec3` feat(wp-450-ф5): промоция hooks-bypass-gate.md + integration-gate.md
- [—] `a7f5f9d` feat: promote 8 personal utility scripts to platform
- [—] `50eeef1` feat(wp-450-ф5): промоция 3 rules-lazy файлов (drift-guard, new-files-guard, wp-stop-list)
- [—] `695033d` feat(residency-gate): ResidencyGate full implementation
- [—] `c286e98` feat: promote day-open-pipeline.sh to platform
- [—] `1d66115` feat(docs): принцип резидентности персональных данных (WP-475 Ф4)
- [—] `e919c04` feat(update.sh): add --fast check mode, version-only comparison (#230)
- [—] `34bcc57` feat(en-projection): community channels live on iwesys/IWE itself (pilot decision)
- [—] `7eeee9e` feat(en-projection): EN distribution is self-contained — no RU-source references (pilot decision)
- [—] `c8fcea1` feat(wp474/f5-f6): dry-run фиксы + assembly через доменные источники
- [—] `dfb4a48` feat(wp401): визуальный слой README + доставка CHANGELOG + EN-редирект контрибуций (Ф5.4/Ф5.6)
- [—] `fed2e79` feat(wp401): governance-файлы публичной витрины + доставка в iwesys (Ф5.1-Ф5.2)
- [—] `3c4d202` feat(wp474/f4): реализовать verify-pack-adequacy-subsection + подключить к /verify и pack-creator
- [—] `0a1de9a` feat(pack-creator,pack-new): seed/mature maturity marker + move .spf-state.yaml out of Pack tree
- [—] `0fbfbba` feat(pack-new): provisional-имя Pack + PFAD-lite decision record (WP-474 Ф2)
- [—] `2befada` feat(pack-new): собирать источники домена до имени, не после (SoTA-Sheet-lite)
- [—] `2381d7f` feat(wp-7): promote 6 day-open scripts + fix scaffold drift + seed new-user scripts
- [—] `927808b` feat(wp-7): promote 6 day-open scripts + fix scaffold drift + seed new-user scripts
- [—] `1c71664` feat: promote day-open-pipeline.sh entry point (WP-7 FMT-PROMOTE-DAYOPEN1)
- [—] `c428393` feat(canon-sync): add iwesys/MimEcoSys publish jobs to translate-sync workflow
- [—] `a100fa6` feat: promote iwe-bug-report.sh to platform (WP-5 sub-#3)
- [—] `529e165` feat(wp-448-ф7): промоция TPF-рамки — 7 артефактов процессного слоя IWE
- [—] `77e856c` feat(wp-415): sync glossary from iwe-translation-engine (18/78/30 tiers)
- [—] `acf10e4` feat(wp-415): automate RU→EN translation sync with tier-based delivery tests
- [—] `d049e6c` feat(dev-guide): тестирование как спецификация (WP-452 Ф1)
- [—] `1d1d4fa` feat(wp-149): promote skill personal-guide-render v2.0.0 to platform (L1)
- [—] `e9cf822` refactor(scripts): удалить избыточный незащищённый template-sync.sh
- [—] `917d950` docs: regenerate [Unreleased] CHANGELOG after guide-kit v0.1.0 delivery (017235c)
- [—] `3b1941a` revert(claude-md): вернуть шаблонный distinctions.md — не мирроить авторский
- [—] `dd273fd` docs(changelog): thank July issue reporters — maxborovik, art-artemov, 277zdwvw9f-pixel, alexfirstoff, alexmetasky, AVNechaev, VxxxlBxxxxv
- [—] `d68413b` docs: regenerate [Unreleased] CHANGELOG after #234 promotion
- [—] `a5697c3` docs: regenerate [Unreleased] CHANGELOG after #247 local-manifest feature
- [—] `387dd77` docs: regenerate [Unreleased] CHANGELOG after issue sweep (#264/#240/#222/#223/#254/#234)
- [—] `750eaf6` chore: remove __pycache__ .pyc from tree + gitignore (sync 238a5c1 garbage)
- [—] `8e69322` docs: regenerate [Unreleased] CHANGELOG after #263 fix
- [—] `806ba4c` docs(changelog): add cec81a3 (DayPlan follow-up to #248)
- [—] `82b1cc8` docs(changelog): sync Unreleased section — #248/#251/#252 fixes, thank VxxxlBxxxxv
- [—] `67571f3` docs(changelog): thank den317 for #247/#249/#250 reports
- [—] `3c62228` docs(changelog): sync Unreleased section — #247/#249/#250 fixes
- [—] `9f0f31c` docs(changelog): sync Unreleased section — scripts/ delivery fix (#247)
- [—] `e1c1924` refine(note-review-d6): уточнить текст правила (не существует вместо пуст, дальние сроки → WeekPlan)
- [—] `0fafee4` docs(changelog): sync Unreleased section — FMT issues #230-246 batch
- [—] `831a992` docs(pack-creation): синхронизация с WP-474 Ф1-Ф6 — SoTA на Шаге 1.5, Kind/термины, /verify pack [wp474]
- [—] `1ef78f4` docs(changelog): sync Unreleased section (governance-файлы, jq-фикс, rename iwe-template->IWE)
- [—] `65e5534` rename(canon-sync): target repo iwesys/iwe-template -> iwesys/IWE
- [—] `eba00c7` docs: онбординг-страница про три слоя IWE (L1/L2/L3)
- [—] `039ccf8` chore(hygiene): untrack .DS_Store, добавить в .gitignore
- [—] `bdb2c9b` docs(changelog): thank users for #229/#228 reports, sync Unreleased section
- [—] `5b72787` rename(canon-sync): target repo iwesys/FMT-exocortex-template-en -> iwesys/iwe-template
- [—] `5bce5e3` revert(canon-sync): drop MimEcoSys mirror job — wrong repo scope
- [—] `b3ba993` refactor(translate): drop openai SDK dependency, call OpenRouter directly
- [—] `901103d` docs: python3 in maintaining-skills snippets
- [—] `c25790a` refactor(translate): switch provider to OpenRouter (reuse existing key, mirror enrich-glossary client)
- [—] `ffcea49` docs(contributing): раздел Promoting a Practice — синхронизация guide при промоции (WP-453 Ф1 §6)
- [—] `b0f675b` fix(scripts): env-fallback для GOVERNANCE_REPO в generate-hot-files-list.sh (CI-блокер, найден при релизе)
- [—] `1b29b19` fix(strategist): убрать хардкод DS-strategy в DAY_OPEN_PIPELINE (регрессия 238a5c1, блокировала CI)
- [—] `5cd5695` fix(roles): runtime-резолв путей в extractor/synchronizer вместо build-time плейсхолдеров (issue #271)
- [—] `5dcff24` fix(wp485): доставить 4 скрипта, обещанных уже промотированными SKILL.md (Ф4)
- [—] `0b20534` fix(templ): issue funnel 266 — доставка session-guard.sh + SessionEnd fail-safe
- [—] `eb612ec` fix(day-open/day-close): дедупликация repo-symlink алиасов в циклах по репозиториям
- [—] `8d4217b` fix(templ): issue funnel 266 — .gitignore для audit-логов + опечатка в CLAUDE.md
- [—] `662188d` fix(claude-md): добавить недостающий .claude/rules-lazy/blocking-rules-full.md
- [—] `188653a` fix(wp415): 3 gaps found by review — CHANGELOG heading drop, broken in-page anchors, incomplete author-attribution regex
- [—] `d69d6f6` fix(wp485): Ф3 ч.2 — синхронизация 5 скриптов root↔шаблон
- [—] `af12f9c` fix(residency-gate): mark_pre_granted becomes a warning no-op (verifier finding, WP-476)
- [—] `b1679da` fix(wp-485): подключить check-wp-transfer-completeness.sh к Week Close шаблона
- [—] `c5488d4` fix(wp-485): 4 живых бага в скриптах шаблона — восстановление регрессии
- [—] `1c62621` fix(day-close): language-tolerant postcondition patterns 9a/9b (#234)
- [—] `5ab284f` fix(executor-catalog): VALID_EXECUTORS += agent, script+judgment (#222)
- [—] `655d385` fix(setup,update): quote env values (#223) + merge-managed base↔remote detector (#254)
- [—] `6ffb54a` fix(pre-commit): manifest-coverage — block только staged, whole-repo WARN (#240)
- [—] `e67ca20` fix(dry-run-gate): restore #237 v2 matcher + whitelist read-only bash helpers (#264)
- [—] `8a611bf` fix(validate-template): restore staged mode + dynamic TEMPLATE_DIR (sync 238a5c1 regression)
- [—] `7e5be12` fix: resolve WP-REGISTRY schema drift cluster (#263)
- [—] `fc763e4` fix(WP-450): promote missing checklists.md pointer + ailev↔IWE glossary
- [—] `8b61285` fix(changelog): restore 0200a93 entry dropped by the auto-regeneration step
- [—] `0e933ee` fix(audit-installation): mark github_status as subscription-gated
- [—] `d55b855` fix(day-close): correct check-index-health.py path
- [—] `51f30fc` fix(iwe-drift): resolve script: helpers relative to the template, not IWE_ROOT
- [—] `b0d1fe0` fix(day-open-scaffold): resolve template-owned scripts locally, not via governance repo
- [—] `40c2d70` fix(strategist): retire redundant day-plan scenario on non-strategy-days (WP-484)
- [—] `a007d15` fix(create-wp): три отставших фикса из root-версии — папка WP-434, consent-file, WeekPlan replace-limit
- [—] `3c82107` fix(day-open): CP_PROFILE указывал на несуществующий cp-profile.json
- [—] `7cbd225` fix: 3 template bugs from bot-flagged issue sweep (#253, #255, #256)
- [—] `f87061e` fix(memory): исправить дрейф терминологии FPF — P2W (WP-481 Ф11)
- [—] `3a1b5ec` fix(hindsight): передать HINDSIGHT_API_LLM_API_KEY в контейнер
- [—] `3703abd` fix(residency-gate): replace hand-rolled YAML parsing with real yaml library
- [—] `9169115` fix(residency-gate): consistent package-relative imports
- [—] `658cfde` fix(residency-gate): test assertion referenced stale example name
- [—] `cec81a3` fix(hooks): DayPlan resolution had the same latest-on-disk bug as #248
- [—] `2ea3510` fix(manifest): drop stale deprecated_files[] entry for docs/DATA-RESIDENCY.md (#251)
- [—] `0bb38e5` fix(hooks): WeekPlan validator checks staged artifact, not latest-on-disk (#248)
- [—] `781e8bb` fix(wp474): D1/D9 addressed-критерии — плейсхолдер-конвенция расширена
- [—] `ae960a2` fix(close-protocols): move final commit after knowledge-write steps (#249)
- [—] `914a39b` fix(validate-template): checks 2/3 print same file types they count (#247)
- [—] `e98f152` fix(gitignore): cover .claude/state/ — create-wp.sh consent-sentinels leave untracked tail (#250)
- [—] `cd240eb` fix(script-promote.sh): bound smoke-test with 5s alarm, daemon scripts hung it forever
- [—] `242ec42` fix(manifest): deliver scripts/ by default instead of blanket-excluding it (#247, root #246)
- [—] `a5c6d0f` fix(day-open-scaffold): bound remaining unprotected network calls (#241 residual)
- [—] `b0ad33b` fix(update.sh): git-based author_diverged() guard replaces path whitelist (#238)
- [—] `65e6b76` fix(dry-run-gate): unified sentinel + command-split matcher closes 4 bypass holes (#237)
- [—] `39b58ac` fix(update.sh): --check не должен писать файлы при TOTAL_CHANGES=0
- [—] `86cf080` fix(update.sh): author_mode-guard для repair_pass()/Step 6 L1-паттерна — устраняет клоббер 66 файлов
- [—] `448daac` fix(note-review): страховка от воскрешения уже закрытого DayPlan (D6 РП-7)
- [—] `f37d93a` fix(exocortex): back up and restore extensions/, matching DATA-POLICY.md promise (#235)
- [—] `b3b6a37` fix(week): remove phantom auto-publisher claim, fix day_num GNU-date fallback (#245)
- [—] `a3d0b95` fix(day-open-scaffold): bound gh issue list calls with portable timeout (#241)
- [—] `e0f5031` fix(strategy-session): wire load-extensions before/after hooks (#236)
- [—] `cddc7aa` fix(seed): align WP-REGISTRY.md schema with create-wp.sh's 6-column output (#232)
- [—] `3647e57` fix(memory-active-wp-update): fall back to nested FMT-exocortex-template/ layout (#242)
- [—] `2b7109c` fix(dt-collect): read scheduler/reports, not scheduler/scheduler-reports (#243)
- [—] `fa23ff0` fix(hooks): scope destructive-guard force detection to git push segment (#233)
- [—] `b4a3fa9` fix(perms): restore executable bit on .claude/lib/frontmatter.sh
- [—] `d234799` fix(manifest): restore executable bit for shell scripts (#239)
- [—] `0f15820` fix(strategy): avoid false calendar and issue defaults in day plan (#238)
- [—] `6a7a7b0` fix(hooks): harden dry-run gate git and cleanup handling (#237)
- [—] `261c5a0` fix(update.sh): не перезаписывать .claude/settings.json при repair/update — только сеять при отсутствии
- [—] `3b00406` fix(day-close): postcondition 9a — xargs ломал проверку на пробеле в имени DayPlan
- [—] `189b62a` fix(en-projection): install command on the EN side forks iwesys/IWE, not the RU source
- [—] `a92471a` fix(en-projection): ONTOLOGY.md is bilingual by design — rewrite link instead of translating
- [—] `b8f8d22` fix(en-projection): heal 3 broken README links on iwesys/IWE found by live audit
- [—] `857cdad` fix(ontology): IWE abbreviation — Intellectual Work Environment (align with distinctions.md and README H1)
- [—] `f3111b2` fix(verify): тип pack в argument-hint — описание скилла не отставало от таблицы типов [wp474]
- [—] `e5c8b0d` fix(manifest): перегенерация generate-manifest.sh — алфавитный порядок verify-* + orz-cycle.svg в files [wp474]
- [—] `e4a23f0` fix(wp415): jq null-guard for per-commit added/modified/removed in translate-sync
- [—] `a0ea7c5` fix(pack-new,pack-creator): устранить дефекты финализации + ретроактивная дыра из Ф2 (WP-474 Ф3)
- [—] `0132fa2` fix(pack-new): устранить дефекты процедуры финализации имени Pack (WP-474 Ф2)
- [—] `4dea62e` fix(translate-sync): publish single attributed commits to iwesys, not en-draft's full history
- [—] `040012c` fix(translate-sync): handle null github.event.commits on workflow_dispatch
- [—] `1113cd0` fix(day-open): promote WP-5 VDV correction — snapshot refresh ordering + drop dead report step
- [—] `41c20fe` fix(translate-sync): attribute EN commits to the human source author, not a bot
- [—] `726fa80` fix(ci): restore scripts/iwe-bug-report.sh dropped from manifest by 7ae267a
- [—] `7ae267a` fix(#229,#228): protect owner:user memory files from stale-repair, add hot-budget validator
- [—] `c828396` fix(canon-sync): persist-credentials false on en-draft checkout
- [—] `eb2e1fe` fix(WP-7/SP1): R15 (accept/reject/defer) — только живой пилот, не агент
- [—] `8562439` fix(translate): strip <body> markers unconditionally, detect output truncation
- [—] `791df86` fix(translate-sync): stop rsync --delete mirror from wiping en-draft
- [—] `702244e` fix(translate): exclude blank fill-in templates from auto-translate
- [—] `e8c6d2e` fix(translate-sync): push HEAD:en-draft for detached worktree, tolerate ASCII-guard warnings, add manual dispatch
- [—] `60e3591` fix(#226): CLAUDE.md conflict no longer aborts update.sh mid-delivery
- [—] `1f00b75` fix(#225,#224): create-wp.sh legacy WP-N regex + archive-done-wp.sh git mv -f
- [—] `93828f4` fix(ci): register .claude/templates/ in delivery contract
- [—] `53c9711` fix: cold-review findings on #217/#220 — sed & escaping, WP-N without bold
- [—] `4eb05e2` fix(#217): CLAUDE.md/AGENTS.md exocortex backup+restore is OS-agnostic
- [—] `c26c0ae` fix(#218): CI catches renamed paths missing from deprecated_files[]
- [—] `1d1a2d9` fix(#220): drift detector executes check:script + recognizes bold WP-id
- [—] `b21d412` fix(#197): setup.sh generates executor-catalog.yaml on install
- [—] `4458412` fix(#221): protocol-artifact-validate.sh accepts <summary> as section heading
- [—] `ef3d728` fix(#192): enforce jq as required prerequisite in setup.sh
- [—] `84858e4` fix(release): sync-version-badge.sh --fix broken on macOS BSD sed + README badge drift
- [—] `0b5e140` fix(extractor): guard против запуска сырого файла шаблона + правка примеров
- [—] `b4d08a2` fix(v0.35.5): orphan-detection TypeError + DS-strategy validator + root detection (#214 #215)
- [—] `212fa2f` fix(setup): include rules-lazy in dry-run and section message

## 0.35.5 — записей: 4

- [—] fix(#215): orphan detection TypeError — `set(dict_list)` → `_path()` helper + set comprehension (`update.sh` Python heredoc)
- [—] fix(#215): bare `DS-strategy` literals in `update.sh` lines 306/533-544 → `${IWE_GOVERNANCE_REPO:-DS-strategy}` (no longer blocked by `validate-fmt-scripts.sh`)
- [—] fix(#215): add `roles/strategist/WORKPLAN.md`, `.claude/hooks/wakatime-heartbeat.sh`, `.claude/skills/peer-conversation/modes.md` to `update-manifest.json deprecated_files` — suppresses false orphan…
- [—] fix(#214): `iwe-env-bootstrap.sh` `.claude/` branch — inline `basename` check prevents `WORKSPACE_DIR` landing inside `FMT-exocortex-template` when bootstrap is sourced from `FMT/.claude/lib/`

## 0.35.4 — записей: 1

- [—] fix(WP-7): FMT delivery blockers от реального pilot update — доставка `setup/validate-template.sh` через `update-manifest.json`, hard-fail `update.sh` при неразрешённых конфликтах `CLAUDE.md`…

## 0.35.3 — записей: 5

- [—] `memory/feedback_community_communication_style.md` — стиль общения агентов с участниками сообщества (community-facing). 5 правил inline + полный набор в externalized memory: таблица переводов…
- [—] `AGENTS.md` — новая секция Response Style — Community-Facing (симметрично пилот-режиму).
- [—] `CLAUDE.md §S-38 «Стиль общения с участниками сообщества»` — inline-правила для Claude-агента, ссылка на полный набор в memory.
- [—] Архитектура доставки — та же, что и для пилот-режима (WP-388 Ф7): компактный inline (≤15 строк) + externalized memory с деталями. Экономия токенов: пилот-режим и community-режим не смешиваются…
- [—] Источник — актуализация WP-388 «Стиль общения агентов IWE» (1 июня 2026).

## 0.35.2 — записей: 3

- [—] `memory/feedback_response_clarity_for_pilot.md` frontmatter: удалена утечка `originSessionId` (локальный id Claude Code-сессии, не часть схемы memory-lifecycle), `description` синхронизирован с телом…
- [—] `CLAUDE.md §9 «Режим на пальцах (S-37)»`: в bullet-list правил режима добавлены метки `(A1)`...`(A11)` symmetric с `AGENTS.md` и `memory/feedback_response_clarity_for_pilot.md` — устранён drift между…
- [—] Источник правок — verify-агент (cold-context Sonnet) и research-агент (general-purpose с WebSearch+WebFetch на 8 источников, включая Jaroslawicz et al. 2025 IFScale). Полные отчёты — в…

## 0.35.1 — записей: 5

- [—] `AGENTS.md` (новый файл для Kimi-агента) — структурное место для правил, симметричное `CLAUDE.md` для Claude. Содержит: коммит-атрибуция Kimi, git staging без `-u/-A/-.`, координация через MCP Local…
- [—] `memory/feedback_response_clarity_for_pilot.md` — общеплатформенное правило для всех агентов в одном файле: 12 паттернов клаттера + 11 правил A1-A11 (как писать пилоту: путь не подлежащее, англицизмы…
- [—] `CLAUDE.md §9 «Режим на пальцах (S-37)»` — расширен: добавлен детектор канала (technical mode vs «на пальцах» по словам в сообщении пилота); расширены правила (запрет пути как подлежащего, требование…
- [—] `template-sync.sh` отрезает §9 при синхронизации, поэтому правки §9 в этом релизе сделаны прямой правкой `FMT/CLAUDE.md`, не через sync.
- [—] `update-manifest.json`: +2 пути (`AGENTS.md`, `memory/feedback_response_clarity_for_pilot.md`); версия `0.35.0 → 0.35.1`.

## 0.35.0 — записей: 116

- [—] `scripts/kimi-peer-adapter.sh` — bridge для вызова Kimi из Claude-писателя (скилл `/peer-conversation`).
- [—] `scripts/claude-peer-adapter.sh` — bridge для вызова Claude из Kimi-писателя (скилл `/peer-writer`).
- [—] `scripts/peer-adapter-filter.py` — `.agentigore` фильтр + PII sanity-check (16 content + 6 filename hard-block паттернов: токены, ключи, JWT, URL Basic Auth, СНИЛС, файлы `*.pem`/`*.key`/`*.token`).
- [—] `sessions/00-index.md` — пустой журнал peer-сессий (заголовок таблицы).
- [—] В манифест добавлены ранее промотированные `.claude/skills/peer-conversation/SKILL.md` и `.claude/skills/kimi-peer-writer/SKILL.md` (закрыт drift от 30 мая).
- [—] `IWE_GOVERNANCE_REPO`: если ваш governance-репозиторий называется не `DS-strategy` (default fallback), установите env-var `IWE_GOVERNANCE_REPO=<имя>` — иначе скиллы `/peer-conversation` и…
- [—] `7e9aa78` feat(triage): post-2026-06-01 backlog cleanup infrastructure
- [—] `dc18e90` feat(detection): MVP FMT critical/deadline issues alert (peer-session 2026-06-01-18) (#145)
- [—] `6be164d` feat(hindsight): WP-337/А.13 FMT template — docker-compose, start, launchd, docs *(автору FMT: файлы добавлены в репо, но НЕ в `update-manifest.json` — клиентам не доставляются; отдельный…
- [—] `43e8268` feat(WP-377): promote pack-creator + org-dev + spf-guard
- [—] `f47bf49` feat(WP-348): promote apply-captures defer_until invariant to L1
- [—] `bc5686f` feat(L1): B-005 reliability обхода Backlog и pending-фаз
- [—] `fbc5585` feat(L1): promote DP.D.052 v2 формулировок из peer-сессии 2026-05-31-11
- [—] `64276ac` feat(WP-372): promote personal-guide-render SKILL.md — narrative 4 уровней
- [—] `4c88807` feat(WP-367 Ф5 uplift): in-session ad-hoc signal + Decision Gate with резюме + audit script
- [—] `b144b3a` feat(strategist): read weekly-digest.md as Loop C input
- [—] `92a1548` feat(WP-367): promote peer-conversation + kimi-peer-writer v4 (Decision Gate fix + двухосная meta.yaml)
- [—] `04ba98e` feat: WP-358 Ф6 delivery — external sessions infrastructure
- [—] `abca838` feat(hooks): pre-commit gates PROMOTE-DRY-RUN + CLEAN-ENV-SMOKE (PD-2/PD-1, WP-347)
- [—] `a8eadab` feat(promote): promotion-status.yaml + record_promotion (PZ-6)
- [—] `36285bc` feat(coverage): coverage-skills.sh — B12a/b/c/d detector (PZ-3)
- [—] `ab2f461` feat(staging): staging-audit.sh — B12e decay detector (PZ-4)
- [—] `d575a6b` feat(sync): extend template-sync allowlist (PZ-2)
- [—] `2655dbb` feat(catalog): generate FMT skills-catalog.yaml (B12a artifact)
- [—] `a9ee8ac` feat(memory): backfill protocol-month-close.md to FMT (B12c)
- [—] `656262a` feat(rules): promote role-prefixes (S-15) to platform
- [—] `3b1cd77` feat(skills): promote bottleneck-pick (S-42+S-46) to platform L1
- [—] `8c15f16` feat(skill/day-close): мультипликатор считать ПО ФАКТУ + sanity check
- [—] `7285005` feat(distinctions): Ход (turn) ≠ Сессия (DP.SC.162 v2, WP-358)
- [—] `54e3f31` feat(distinctions): Session request/light/heavy — WP-358 peer-сессия 27 мая
- [—] `6e38782` feat(WP-350/Ф20): доставка Маршрутизатора и 5 скиллов в FMT через promote-конвейер
- [—] `1e32045` feat(manifest): MG5 — pre-commit hook для manifest coverage + 4 orphan-файла в манифест
- [—] `2136de9` feat(WP-350): JSON output, routing-path-distribution audit, routing-errors.log
- [—] `766eb3d` feat(WP-350): agent-fault skill для AGENT_FAULT routing
- [—] `33cc31d` feat(WP-350): strict/flex routing + test suite (8 cases)
- [—] `0b6afe1` feat(WP-350): промоция generate-executor-catalog.py + generate-helper-catalog.py
- [—] `cd2a295` feat(WP-350): routing-заголовки в 21 FMT хелпер-скрипт
- [—] `c571c55` feat(WP-350 Ф13): Маршрутизатор + Артефактор в Session Open
- [—] `7599ae5` feat(WP-350 Ф12): route-task.sh — Маршрутизатор задач IWE
- [—] `ceca611` feat(WP-350 Ф10): routing-заголовки в 20 скриптов + script_path в 3 SKILL.md
- [—] `6142f6a` feat(WP-350 Ф9): routing: секция в 21 скилл шаблона
- [—] `0ba2168` feat(WP-352/Ф3): add HD numbers to 4 FPF distinctions in distinctions.md
- [—] `b05a35b` feat(WP-352 Ф2): 4 FPF различения в distinctions.md
- [—] `016833a` feat(week-close): add step 7a iwe-backup-check.sh before backup
- [—] `836997c` feat: promote iwe-backup-check.sh to platform scripts
- [—] `a4260e7` feat(day-open): scaffold PENDING markers + protocol-close WP archiving step
- [—] `02bfe7d` feat: guard в script-promote.sh — блокирует перезапись фиксов FMT
- [—] `75d15f0` feat(WP-347 Ф3+Ф4): docs/RELEASE-PROCESS.md + правило валидатора в SCRIPT-PROMOTION.md
- [—] `95817fa` feat(WP-347 Ф2): CI-конвейер: B2 manifest CI + B8 set-e детектор + гранулярные флаги
- [—] `ce15f52` feat(rules): wp-scope — guard для umbrella РП
- [—] `40521e9` feat: WP-247 промоция — apply-captures + protocol-close.checks + inter-agent-handoff
- [—] `609eaa0` feat: promote iwe-agent-dispatcher.py to platform (WP-337 Ж-Ф4)
- [—] `e165020` feat(Ж-Ф4): headless-runner.sh — точка входа headless-адаптера DP.IWE.011
- [—] `78698f2` feat(WP-348): Ф6 — session-record extension point
- [—] `101bd44` feat(WP-348): Ф5 — skill-promote.sh v2 + skills-pull.sh (pull pipeline)
- [—] `cecf52d` feat(WP-348): Ф4 — create-skill.sh + validate-skill.sh
- [—] `d4e3db2` feat(WP-348): Ф3 — SKILL.md v2 шаблон + генератор каталога + мигратор
- [—] `2136141` feat: settings-promote.sh + pre-commit HOOK-PATH-CONVENTION gate
- [—] `333c83d` feat(strategist): complete runner migration — run_skill() for day-open/day-close/week-close/strategy-session
- [—] `scripts/validate-fmt-scripts.sh` — добавлена Проверка 5: ловит хардкоды `$HOME/IWE/<author-repo>/(scripts|sessions|docs|current)/` и `~/IWE/...` (Python `expanduser`) в `.claude/skills/*/SKILL.md`…
- [—] `22cdd0d` chore(WP-377): R29 Детектор → R47 в hooks/lib/detectors
- [—] `b9e1658` docs(release): метрика fix-коммитов в RELEASE-PROCESS.md (PD-4, WP-347)
- [—] `33537d6` docs(promotion): B12 class + pair-on-promote convention (PZ-5)
- [—] `f1caefd` improve(peer): adversarial prompt — критик обязан найти хотя бы одно возражение
- [—] `74d5b67` sync(wp-new): синхронизация с user-level — active-wp пересборка + блокирующее правило
- [—] `c098042` ci(validate-template): add validate-fmt-scripts.sh to CI pipeline
- [—] `89ea560` refactor(WP-350 Ф5): R29 Артефактор → Декомпозитор, /artifactor → /decompose
- [—] `a5b9aa8` docs(changelog): add 2c92438 warn() fix to Unreleased
- [—] `f721eb0` chore(audit-installation): add SKILL.md frontmatter (version, layer, status, triggers)
- [—] `af829fe` chore: sync headless-runner.sh
- [—] `c370fe9` docs: уточнить различение Скилл ≠ SKILL.md (WP-348 post-close)
- [—] `e77406c` chore: release 0.34.1
- [—] `5b43a38` chore: release 0.34.0
- [—] `f112f0d` fix: iwe-audit portability + release-audit-log.md (closes #24, #142) (#144)
- [—] `575ae4e` fix(notify): make TEMPLATES_DIR overridable via environment (#49)
- [—] `934e9c9` fix(verify): add model mapping for verification_class in wp type (#47)
- [—] `4a00339` fix(dt-collect): replace hardcoded DS-strategy with $GOVERNANCE_DIR (#46)
- [—] `065e60a` fix(day-close): portability — HOME_SLUG + rsync --delete (#119)
- [—] `df591ea` fix(dry-run-gate): make sentinel discovery session-agnostic (closes #59) (#60)
- [—] `bffd92c` fix(skill): quote pack-new description in SKILL.md frontmatter (#137)
- [—] `6b164f6` fix(promote): settings-promote --dry-run пропускает existence check (WP-347 PD-2 followup)
- [—] `c2e96e6` fix(promote): regenerate FMT skills-catalog.yaml (B12a)
- [—] `0ccb1e2` fix(catalog): generate-executor-catalog.py — раскрывать env IWE_GOVERNANCE_REPO в DEFAULT_OUTPUT
- [—] `143ca6a` fix(claude.md): restore IntegrationGate checklist items 1, 3
- [—] `32e3607` fix(server-calendar): add utf-8 encoding declaration to Python heredocs
- [—] `39ca8ea` fix(template): replace author-specific DS-my-strategy with placeholder
- [—] `beb7f15` fix(week-draft): WD1 — заполнять даты Пн-Вс в таблице метрик для совместимости с append
- [—] `8676d68` fix(setup): auto-enable core.hooksPath for repos with .githooks/
- [—] `ed67968` fix(validate): whitelist direct-call hooks + parametrize DS-strategy literal in iwe-audit
- [—] `89367b4` fix(router): interpreter auto-detection + T13 agent-fault args
- [—] `8bea701` fix(WP-350): Шаг 0 Маршрутизатор — безусловный, loop-guard, AGENT_FAULT
- [—] `03515f0` fix(WP-350): explicit return 0 in all dispatch branches
- [—] `4dd7cf2` fix(WP-350): llm_tokens field, 10 test cases, return consistency
- [—] `8a3fa5d` fix(WP-350): audit-log on script failure, return exit code
- [—] `8d51a01` fix(WP-350): audit-log calls, yaml check, args quoting, test rename
- [—] `63503aa` fix(test-route-task): add || true to ((VAR++)) under set -e
- [—] `27fecea` fix(validate-fmt-scripts): safe-pattern exclusions for detector false positives
- [—] `457950b` fix(manifest): B2 coverage gap — add 3 orphan scripts to update-manifest.json
- [—] `0bc537f` fix(script-promote): робастный hint + аргументы в любом порядке
- [—] `dde3e7f` fix: регрессии после sync + 2 новых дополнения
- [—] `9dfbfaa` fix: минимальный frontmatter в guard-else вместо touch
- [—] `0fe32f5` fix(WP-347): RELEASE-PROCESS.md — 3 правки по Kimi-ревью
- [—] `81e5727` fix: scaffold guard + D11 upgrade to FAIL
- [—] `8d316f4` fix: три замечания Евгения — manifest/day-plan/detector-11
- [—] `af3b15c` fix: remove stale deprecated entries + add detector 10 for runner/manifest cross-check
- [—] `0321fcf` fix(WP-247): исправить путь REPORTS_DIR в protocol-close.checks.md
- [—] `2c92438` fix(smoke-test): define warn() — undefined function broke Validate Template CI
- [—] `ea7ead8` fix(dispatcher): race-condition after claude -p — git reset --hard before status commit
- [—] `16b468a` fix(ci): setup.sh SETUP_CI=1 не требует claude/node/npm как prerequisites
- [—] `7f3fba0` fix(WP-348): SIGPIPE-баг в migrate-skills-to-v2.sh has_field()
- [—] `8a231a3` fix(CI): закрыть 3 реальных блокера Validate Template
- [—] `b00ef4c` fix(settings-promote): inline jq check вместо полного validate-fmt-scripts.sh
- [—] `72f7572` fix: hook paths — $CLAUDE_PROJECT_DIR/ convention for all hook commands
- [—] `e337183` fix(manifest): remove strategist prompts from deprecated_files — runner still uses them
- [—] `5bffbc9` fix: replace hardcoded DS-strategy with GOVERNANCE_DIR/GOVERNANCE_REPO env vars
- [—] `2c5e91d` fix(pack-templates): DP.WP.NNN — добавить §6 пример Stage Dependency Map

## 0.34.1 — записей: 1

- [—] `8a231a3` fix(CI): закрыть 3 реальных блокера Validate Template — regex detector #9, hardcoded DS-strategy, smoke-test gh auth, install.sh portability

## 0.34.0 — записей: 16

- [—] `4c7bf32` feat(calendar): promote day-open + week-close skills — meeting/task split, week mode, bot QA restored
- [—] `6df8f7a` feat(calendar): server-calendar.sh v2 — L3 template sync
- [—] `ea9d683` feat(WP-295): CLI iwe trace show/search/upload (Ф1 Шаг 6)
- [—] `c277672` feat(pack-ci): auto-install CI guard via pack-new + pack-ci-install.sh
- [—] `117da91` feat(pack-templates): CI guard для новых Pack-репо (.github/workflows/pack-lint.yml)
- [—] `c180e6a` feat(WP-316 Ф6): promote Agent Fault Profile v0.33.0 — scripts + extensions
- [—] `de23341` feat(strategy-session): добавить шаги 1b (KE-кандидаты) и 1c (Мир) в открытие недели
- [—] `8a72b50` feat(WP-295): agent-trace-recorder writer hooks (Ф1 шаг 5)
- [—] `72f7572` fix(WP-7): hook paths — $CLAUDE_PROJECT_DIR/ convention for all hook commands
- [—] `2136141` feat(WP-7): settings-promote.sh + pre-commit HOOK-PATH-CONVENTION gate
- [—] `b00ef4c` fix(settings-promote): inline jq check вместо полного validate-fmt-scripts.sh
- [—] `d451166` fix(memory-active-wp-update): fallback to exocortex when runtime memory is read-only
- [—] `0263a5a` fix(agent-inbox): add fetch+rebase before push in commit_and_push
- [—] `c715f5e` fix(WP-7 Ф-id-collisions): обновление slug-ссылок DP.SC.019→043, PD.SOTA.001→007
- [—] `767ad46` fix(dt-collect+templates): fix weekly multiplier parser + format note
- [—] `d13af21` fix(WP-295): pretty=format → tformat для produced_artifact_ids

## 0.33.0 — записей: 11

- [—] `de23341` feat(strategy-session): добавить шаги 1b (KE-кандидаты) и 1c (Мир) в открытие недели
- [—] `8a72b50` feat(WP-295): agent-trace-recorder writer hooks (Ф1 шаг 5)
- [—] `6970050` feat(WP-324): Agent Inbox 0.32.0 — pack-templates + dispatcher script
- [—] `223fb5f` feat(WP-324): promote S-45 Agent Inbox — extensions/agent-inbox/
- [—] `63aa96c` feat: changelog automation — changelog-append.sh + changelog-flush.sh + v0.31.0
- [—] `4002819` feat: promote S-44 to L1 — Telegram reminders as platform rule (rule 8)
- [—] `0c40b8f` feat: promote S-43 — напоминания через Telegram
- [—] `767ad46` fix(dt-collect+templates): fix weekly multiplier parser + format note
- [—] `d13af21` fix(WP-295): pretty=format → tformat для produced_artifact_ids
- [—] `9d96a63` fix(changelog): 5 багов из code review субагента
- [—] `4db37fd` fix: rename S-43→S-44 (Telegram reminders) to avoid numbering conflict with Agent Fault Profile

## 0.32.0 — записей: 11

- [—] Agent Inbox pack-templates (WP-324, новое): `pack-templates/digital-platform/08-service-clauses/DP.SC.NNN-agent-inbox.md` +…
- [—] `extensions/agent-inbox/scripts/iwe-agent-dispatcher.py` — диспетчер на headless `claude -p`. Не зависит от RemoteTrigger v1→v2 API issue. Pure-Python stdlib + минимальный YAML frontmatter parser…
- [—] Headless `claude -p` как референсный канал dispatcher (DP.ROLE.NNN §4 + §7 + SPEC.md §2): не зависит от RemoteTrigger v1→v2 API issue, работает на любой машине с установленным claude CLI; покрывает…
- [—] `extensions/agent-inbox/SPEC.md` §2 — добавлена таблица каналов запуска (claude CLI / RemoteTrigger / systemd / launchd) с рекомендацией headless CLI как референсной реализации.
- [—] S-45 (Agent Inbox) остаётся `testing` после расширения объёма: фундамент + script + pack-templates готовы, полная end-to-end automation smoke (4 реальные task по расписанию) deferred — требует Nix…
- [—] `223fb5f` feat(WP-324): promote S-45 Agent Inbox — extensions/agent-inbox/
- [—] `63aa96c` feat: changelog automation — changelog-append.sh + changelog-flush.sh + v0.31.0
- [—] `4002819` feat: promote S-44 to L1 — Telegram reminders as platform rule (rule 8)
- [—] `0c40b8f` feat: promote S-43 — напоминания через Telegram
- [—] `9d96a63` fix(changelog): 5 багов из code review субагента
- [—] `4db37fd` fix: rename S-43→S-44 (Telegram reminders) to avoid numbering conflict with Agent Fault Profile

## 0.31.0 — записей: 29

- [—] Полный набор promote-скриптов: `script-promote.sh`, `hook-promote.sh`, `skill-promote.sh` + `validate-fmt-scripts.sh` с автовалидацией в `template-sync.sh` (WP-5 L1-flow)
- [—] Smoke-тест в promote-скриптах — изолированный env с шаблонными переменными
- [—] `changelog-append.sh` + `changelog-flush.sh` — автоматическое ведение CHANGELOG при каждой промоции
- [—] S-44: Telegram-напоминания как платформенное правило (правило 8 в CLAUDE.md, WP-5)
- [—] S-33 (Hooks/Scripts Bypass Gate) промотирован в L1 §2 платформенных правил
- [—] Knowledge Routing Gate (WP-216 Ф4): `routing-vocab.md` fast-path + DP.SC.036
- [—] Флаг `--related` и секция «Связки с РП» в шаблоне WP-context + шаг 3.5 в Ритуале
- [—] cross-platform path leaks detector (WP-5/WP-7 Stability-4)
- [—] Secret Drift Detector: `iwe-grep-secret.sh` MVP + Railway GraphQL v2 cloud scan (WP-315)
- [—] Sync-фаза WP Gate resilience — pre-flight + graceful degradation (WP-294)
- [—] `reflection-template` + Шаги 6.7-6.8 в `personal-guide-render` (WP-309 Ф3)
- [—] EC-триггер для конфликтов НЭП в `strategy-session`
- [—] News Lens: шаг 6a Day Open — Haiku subagent синтез новостей
- [—] q-шкала качества недели в Week Close + якоря q=2 и q=4 (WP-310 Gap-А)
- [—] Agent Fault Profile: процесс учёта косяков агента + скрипты `agent_fault_remind.py`, `sync_feedback_to_memory.py`
- [—] S-45 Agent Inbox (WP-324): `extensions/agent-inbox/` структура (tasks/results/scout/templates/archive) + SPEC.md + README.md + 5 шаблонов промптов (analyze-section, scout-daily, evolution-cron…
- [—] Явный L1-flow для всех артефактов в CLAUDE.md (scripts + hooks + skills + CLAUDE.md)
- [—] WP-283 Ф-H: отказ от WORKPLAN.md hub-and-spoke (антипаттерн, OwnerIntegrity)
- [—] matrix-CI по `GOVERNANCE_REPO` + detector `.sh` scope + 2 hardcoded fix
- [—] `day-close`: wakatime path `~/.wakatime/wakatime-cli` (CLI не в PATH)
- [—] hardcoded `DS-strategy` в `dt-collect.sh` + repair-pass в `update.sh`
- [—] routing slow-path для FMT пользователей: `repo-type-rules.md` вместо `DP.KR.001` (недоступен без Pack)
- [—] WP-7: guard stale repair против нечитаемого dst под `set -e` + hash-check для stale propagated L1 files
- [—] `update.sh`: progress counter в step [2] + manifest version sync после apply
- [—] WP-315: два `set -e` бага в `iwe-grep-secret.sh` + E2E arithmetic zero-eval paths (`|| true`)
- [—] `load-extensions`: robust workspace resolution + BASH_SOURCE fallback
- [—] `setup.sh`: `source ~/.iwe-paths` before role install + validate `WORKSPACE_DIR`
- [—] `wp-sync-bundle`: self-test не зависит от hardcoded WP-294
- [—] S-44: переименование S-43→S-44 (конфликт нумерации с Agent Fault Profile)

## 0.30.0 — записей: 5

- [—] `scripts/week-draft-init.sh` — создаёт пустой черновик недельного поста на Пн Day Close
- [—] `scripts/week-draft-append.sh` — обновляет строку метрик дня в черновике (WakaTime, коммиты, закрытые РП)
- [—] `scripts/check-script-collisions.sh` — детектор коллизий имён между авторскими и FMT-скриптами; запускать ПЕРЕД любой промоцией L3→L1
- [—] `docs/SCRIPT-PROMOTION.md` — 7-шаговый процесс промоции скрипта (DP.KR.001 §5.6)
- [—] `knowledge_repo` — путь к knowledge-index репо (относительно `WORKSPACE_DIR`). Пустая строка → накопительный черновик пропускается (фича опциональна).

## 0.29.32 — записей: 0


## 0.29.31 — записей: 4

- [—] `memory/protocol-open.md` § Sync Gate переписан — дефолтное поведение веток A (тривиально, main agent), B (≥2 related или drift → Task → `wp-sync-actualizer`), C (противоречие → «Требует внимания»…
- [—] Race-guard — state-файл `.claude/state/wp-sync-<N>.done` предотвращает повторный sync для одного WP в одной сессии.
- [—] Exit 2 в bundler — `validate_frontmatter()` проверяет наличие двух `---` маркеров, иначе exit 2 + `[PARSE-ERROR]` в stderr. Ранее отсутствовало (контракт описан, не реализован).
- [—] `extensions/protocol-open.sync.md` (опционально, L3) — теперь чистая override-точка с шаблоном для замены sub-agent'а / порогов веток / сторонних обогащений bundle. По умолчанию не нужен.

## 0.29.30 — записей: 5

- [—] `memory/protocol-open.md` — новый шаг 3 «Sync Gate» в § WP Gate перед «→ Ритуал». EXTENSION POINT: `bash .claude/scripts/load-extensions.sh protocol-open sync`. Цель: исключить дублирование работы и…
- [—] `.claude/scripts/wp-sync-bundle.sh` — детерминированный bundler. Парсит YAML frontmatter без yq, извлекает `related:` блок + grep тела на WP-NNN, статус из REGISTRY, git log по WP-файлам за 14 дней.…
- [—] `.claude/agents/wp-sync-actualizer.md` — sub-agent (Sonnet 4.6) с context isolation. Возвращает unified diff в текстовом формате (`---ORIGINAL---`/`---REPLACEMENT---`); НЕ редактирует напрямую.…
- [—] `update.sh:609` — добавлен `.claude/agents/*` в паттерн копирования (sub-agent definitions = платформа, не workspace-local).
- [—] `setup/smoke-test-fresh-install.sh:193` — `agents` убран из исключений (теперь обязательно в паттерне `update.sh:609`).

## 0.29.29 — записей: 6

- [—] `roles/synchronizer/scripts/dt-collect.sh:234` — `collect_sessions()` использовал hardcoded `$WORKSPACE/DS-strategy/inbox/open-sessions.log` вместо `$GOVERNANCE_DIR`. На fresh clone с…
- [—] `update.sh:609` — паттерн копирования `.claude/X/*` пропускал `.claude/scripts/`. На fresh install скиллы (`day-open`, `day-close`, `month-close` и др.) звали `bash…
- [—] `setup/smoke-test-fresh-install.sh` Test 6 — install.sh запускался без `env -i HOME=$TEST_WS` (positive case), писал реальные plist в `~/Library/LaunchAgents/com.strategist.*` и звал `launchctl…
- [—] smoke `[6a]` расширен на template `roles/*/scripts/` — раньше скан только `.iwe-runtime/roles/`, dt-collect.sh:234 пропускался (он используется напрямую cron'ом, не из runtime).
- [—] smoke `[6d]` meta-detector — все `.claude/X/` каталоги в FMT обязаны быть в паттерне `update.sh:609`. Исключения: `agents`, `projects`, `context-cache`, `logs` (workspace-local / runtime-only).…
- [—] `validate-template.sh [8/8]` parameterization debt detector — переиспользует `setup/detector-regex.sh::DETECTOR_07_REGEX`. Скан областей: `roles/`, `scripts/`, `setup.sh`, `update.sh`. Текущий debt…

## 0.29.28 — записей: 3

- [—] `scripts/template-sync.sh` (новый, ~50 строк): синхронизация `$IWE_WORKSPACE/CLAUDE.md` → `$IWE_TEMPLATE/CLAUDE.md` с placeholder-подстановкой ($HOME → {{HOME_DIR}}, $IWE_GOVERNANCE_REPO →…
- [—] `CLAUDE.md` §2 Pre-action Gates: добавлен Routing Gate (создание/размещение артефакта → DP.KR.001 §5).
- [—] `CLAUDE.md` §2 IntegrationGate чеклист: добавлены пункт 1 (Service Clause) и пункт 3 (Role) с детализацией.

## 0.29.27 — записей: 1

- [—] `CLAUDE.md` §2 п.4: правило `Pull-on-Touch` расширено с «первого изменения» на «первое обращение» (любое — `ls`/`Read`/`find`/`grep`/Edit/commit). Применяется ко всем git-репо в `{{HOME_DIR}}/IWE/*`…

## 0.29.26 — записей: 1

- [—] `.claude/skills/day-close/SKILL.md`: шаг 1 «Сбор данных» — добавлены два `grep -vE` для исключения служебных коммитов и путей. Фильтр убирает: (а) Conventional Commits префиксы…

## 0.29.25 — записей: 2

- [—] `roles/strategist/prompts/strategy-session-weekly.md`: добавлен Шаг 0 (БЛОКИРУЮЩЕЕ) — «Если первая сессия месяца — прочитать архив прошлого месяца» (4 подшага: найти `archive/MonthClose YYYY-MM.md`…
- [—] `memory/r-questionnaire.md`: Month Close блок переработан — M1-M3+M6 заполняются агентом автоматически из данных (с указанием источника), M4-M5 — субъективные, спрашиваются у пользователя.

## 0.29.24 — записей: 5

- [—] `roles/strategist/scripts/launchd/com.strategist.morning.plist` и `com.strategist.weekreview.plist`: добавлен `IWE_GOVERNANCE_REPO={{GOVERNANCE_REPO}}` в `EnvironmentVariables`. launchd не загружает…
- [—] `roles/strategist/scripts/strategist.sh`: перевод на template-форму (`{{WORKSPACE_DIR}}/{{GOVERNANCE_REPO}}`, `{{CLAUDE_PATH}}`). Конкретные значения теперь только в `.iwe-runtime/` (генерируется…
- [—] `roles/strategist/prompts/*.md` (10 файлов): `DS-strategy` → `{{GOVERNANCE_REPO}}`. `strategist.sh` подставляет `$IWE_GOVERNANCE_REPO` через sed в runtime.
- [—] `roles/strategist/scripts/cleanup-processed-notes.py`: читает `IWE_GOVERNANCE_REPO` из env (fallback: `DS-strategy`).
- [—] `roles/synchronizer/scripts/dt-collect-neon.py`: удалены ADR-009 dual-write блоки к `development.user_events` (WP-268 cleanup).

## 0.29.23 — записей: 2

- [—] `/personal-guide-start` — bootstrap репо `personal-guide` на GitHub пилота (один раз). Создаёт репо через Aisystant MCP, делегирует наполнение render-скиллу.
- [—] `/personal-guide-render` — наполнение 6 файлов (profile, worldview, methods, README, weekly/, daily/) из Память.Derived + Персона. Вызывается повторно при обновлениях.

## 0.29.22 — записей: 2

- [—] Было: `section_re = re.compile(rf'Итоги\s+\S+\s+{day_num}\s+{month_ru}')` — `\S+` матчил `W16:` в заголовке недели «Итоги W16: 13 апр» раньше дневного «Итоги пн 13 апр»
- [—] Стало: `re.compile(rf'Итоги\s+(?:пн|вт|ср|чт|пт|сб|вс)\s+{day_num}\s+{month_ru}', re.IGNORECASE)` — матчит только дневные итоги с именованным днём недели

## 0.29.21 — записей: 6

- [—] `memory-validate.sh` — frontmatter-гейт: проверяет 9 обязательных полей (name, description, type, horizon, domains, status, valid_from, owner, schema_version), допустимые значения, инвариант…
- [—] `memory-health.sh` — метрики: кол-во файлов, HOT-лимит (≤150 строк), orphans%, распределение по горизонтам
- [—] `memory-bleed.sh` — детектор нарушений: HOT overflow, orphans без frontmatter, superseded без ссылки, TTL-кандидаты на понижение горизонта
- [—] `memory-migrate.sh` — автодобавление отсутствующих полей (type/horizon/domains/status/owner/schema_version/name/description/valid_from) с инференцией по имени файла; `--dry-run` и `--all` режимы
- [—] `week-close/SKILL.md` — добавлен шаг 7c Memory Validate (T22b): `bash ${IWE_SCRIPTS}/memory-bleed.sh`; нарушения → исправить до коммита, кандидаты понижения → информативно
- [—] `month-close/SKILL.md` — обновлён шаг 1f: конкретные команды `memory-health.sh` + `memory-bleed.sh` вместо описательного текста

## 0.29.20 — записей: 3

- [—] Шаг 1 разбит на два явных подшага:
- [—] Семантика идентична Day/Week Close (как описано в `run-protocol/SKILL.md` Шаг 1b)
- [—] Commit: `51b06a0` (прямой коммит в FMT, минуя broken template-sync pipeline)

## 0.29.19 — записей: 2

- [—] `DETECTOR_07_REGEX` дублировался в `setup/integration-contract-validator.sh:238` и `setup/test-detectors.sh:35`. При правке regex в одном месте второе расходилось → ложный pass на регрессии.
- [—] Вынесен в `setup/detector-regex.sh` как shared source. Оба скрипта теперь `source` его. Изменение regex → автоматическая sync.

## 0.29.18 — записей: 17

- [—] `integration-contract` job теперь идёт на `[ubuntu-latest, macos-latest]`. macOS preinstall: `brew install jq`.
- [—] Ловит портабельность-баги, которые были в 0.28.12 (BUG-2..4 на Linux).
- [—] Новый job `upgrade-test`: checkout previous version (по `git log update-manifest.json`) → smoke на ней → checkout HEAD → re-run validator + smoke. Симулирует upgrade-сценарий (а не fresh build).
- [—] Ловит класс 0.29.13 (template-sync перетёр стабильный код).
- [—] `setup/detector-fixtures/` — historical positive samples, которые detectors ДОЛЖНЫ ловить. Первый: `detector_07/positive_backtick_slash.md` (regression sample 0.29.14).
- [—] `setup/test-detectors.sh` — runner, прогоняет каждый detector regex на fixtures.
- [—] В `pre-commit` (если staged изменения в validator/fixtures) и в CI.
- [—] Ловит regex-gap регрессии в самих detector'ах (как 0.29.14 backtick+slash gap).
- [—] `.github/workflows/post-release-audit.yml` — на каждый push изменяющий `update-manifest.json` (= релиз) auto-создаёт GitHub Issue с adversarial-промптом. Также `workflow_dispatch` для ручного…
- [—] `setup/release-audit-prompt.md` — единый промпт-template для adversarial audit (10 классов проверок).
- [—] Автор/пилот прогоняет в Claude session, найденные классы → +detector в `integration-contract-validator.sh`.
- [—] `setup/ux-walkthrough-prompt.md` — symulator «новый пилот час 0» проходит онбординг буквально, фиксирует UX-провалы (broken links, скрытые prerequisites, jargon без расшифровки).
- [—] Запускается вручную через subagent (item 5 не покрывается автоматически — UX требует human-like reasoning).
- [—] Реальная установка на пилотской ОС/железе (не CI sandbox)
- [—] Тестирование long-tail сценариев накопленным use'ом
- [—] Различия mental models — другие blind spots чем у автора + sub-agent
- [—] Final UX-judge: «понятно ли реальному человеку»

## 0.29.17 — записей: 5

- [—] `extensions/README.md` table декларировал `day-close.after.md` как extension point, но `.claude/skills/day-close/SKILL.md` не имел caller'а — пилот, создавший `extensions/day-close.after.md`, не…
- [—] Добавлен шаг 9c `Extensions (after)` с `load-extensions.sh day-close after` (между шагами 9 «Запись итогов» и 10 «Закоммитить» — параллельно `week-close` структуре).
- [—] Detector #3 не ловил это, потому что mention `extensions/day-close.after.md` встречался в текстовых примерах README.
- [—] Detector #2 (`seed_references`) проверяет ссылки `seed/...` в `protocol-*.md`. Изменение в `seed/` не триггерило валидатор → drift возможен silently.
- [—] Расширен filter: `roles/|.claude/|setup/|memory/|extensions/|seed/|update-manifest.json`.

## 0.29.16 — записей: 11

- [—] `.claude/skills/day-close/SKILL.md` строки 50, 136, 171 читали exact `extensions/day-close.checks.md`. Suffix-расширения (`day-close.checks.beads.md`) не подхватывались.
- [—] Все 3 точки переведены на `bash .claude/scripts/load-extensions.sh day-close checks` (как day-close.before в 0.29.9 и week-close.before/after в 0.29.13).
- [—] Skill упомянут в `CHANGELOG.md`, `.claude/skills/ke/SKILL.md`, `roles/strategist/prompts/session-prep.md` — но физически отсутствовал.
- [—] Промотирован из авторского IWE с заменой констант `DS-my-strategy` → `{{GOVERNANCE_REPO}}` и `~/IWE/` → `{{WORKSPACE_DIR}}/`.
- [—] Добавлен в `update-manifest.json` files.
- [—] `memory/MEMORY.md:38-39` — ссылки на `claude-md-maintenance.md` и `wp-gate-lesson.md` (оба deprecated в 0.27, файлов нет). Удалены.
- [—] `memory/t-checklist.md:61` — ссылка на `memory/protocol-month-close.md` (нет такого файла, есть skill `.claude/skills/month-close/SKILL.md`). Ссылка на отсутствующий протокол убрана.
- [—] Новый блок `INTEGRATION-CONTRACT-VALIDATOR` запускает `setup/integration-contract-validator.sh` если staged файлы из scope (`roles/`, `.claude/`, `setup/`, `memory/`, `extensions/`…
- [—] FAIL → коммит блокируется. Escape: `git commit --no-verify`.
- [—] Новый job `integration-contract` запускает оба скрипта на каждый push/PR в main.
- [—] Defense-in-depth для `--no-verify` пропусков pre-commit.

## 0.29.15 — записей: 3

- [—] `.claude/skills/month-close/SKILL.md` создан (280 строк, заменены авторские константы `DS-my-strategy` → `{{GOVERNANCE_REPO}}`, `~/IWE/` → `{{WORKSPACE_DIR}}/`).
- [—] Содержит 2 EXTENSION POINT через `load-extensions.sh month-close before` (Шаг 0) и `load-extensions.sh month-close after` (Шаг 11).
- [—] Добавлен в `update-manifest.json` files (alphabetic order).

## 0.29.14 — записей: 7

- [—] `roles/auditor/prompts/audit-plan-consistency.md` строки 12-14 — 3 bare `DS-strategy/path` в backtick.
- [—] `roles/verifier/prompts/verify-wp-acceptance.md` строка 11 — bare `` `DS-strategy/inbox/...` ``.
- [—] Validator #7 regex `` '`DS-strategy`|/DS-strategy/| DS-strategy[ /]' `` не матчил паттерн `` `DS-strategy/ `` (backtick + slash без пробела). Расширен до `` '`DS-strategy[`/]|/DS-strategy/|…
- [—] Оба файла исправлены: `DS-strategy` → `{{GOVERNANCE_REPO}}`.
- [—] Файл в substituted-списке — `DS-strategy` в текстах логов вводил в заблуждение при нестандартном GOVERNANCE_REPO.
- [—] Заменено на `$_gov_repo` (переменная уже определена в том же scope строкой 103).
- [—] Detector #7 расширен: теперь ловит `` `DS-strategy/path` `` (backtick+slash) — паттерн из agential-промптов.

## 0.29.13 — записей: 14

- [—] `WORKSPACE` стал хардкодом `$HOME/IWE/DS-strategy` (было `{{WORKSPACE_DIR}}/{{GOVERNANCE_REPO}}`).
- [—] `PROMPTS_DIR` стал `$REPO_DIR/prompts` без `$IWE_TEMPLATE`-fallback (antipattern R5.1).
- [—] `run_claude()` потерял sed-substitution GOVERNANCE_REPO/WORKSPACE_DIR/GITHUB_USER в промптах (добавлен в 0.29.5, escaped в 0.29.6).
- [—] Восстановлено до 0.29.7 (git `66f8566`).
- [—] `WORKSPACE = Path.home() / "IWE" / "DS-strategy"` — жёсткий хардкод вернулся.
- [—] `_resolve_workspace()` (читает `IWE_WORKSPACE` + `IWE_GOVERNANCE_REPO` из env + fallback через `.exocortex.env`) была потеряна.
- [—] Восстановлено до 0.29.7.
- [—] `roles/strategist/prompts/{day-close,day-plan,note-review,session-prep,strategy-session,week-review}.md` — `DS-strategy` bare без `{{GOVERNANCE_REPO}}`.
- [—] Все 6 восстановлены до 0.29.7.
- [—] `GOVERNANCE_DIR="${GOVERNANCE_DIR:-$WORKSPACE/DS-strategy}"` — хардкод.
- [—] `SESSION_LOG="$WORKSPACE/DS-strategy/inbox/..."` — хардкод.
- [—] Файл в `substituted:` списке overlay — build-runtime не мог подставить `{{GOVERNANCE_REPO}}`. Восстановлены плейсхолдеры.
- [—] 0.29.11 добавил в `deprecated_files` 8 файлов с reason `"strategist role removed"`, но эти файлы остались в `files` и физически в репо (роль не удалена). update.sh получил конфликт «доставить и…
- [—] После R5.5 (0.29.9) `day-close.before` перешёл на loader-native, но `week-close.before` и `week-close.after` остались с `ls extensions/week-close.*.md` (exact filename). Обновлены оба по образцу…

## 0.29.12 — записей: 1

- [—] `scripts/iwe-audit.sh` — путь поиска `.exocortex.env` — скрипт искал файл в `$HOME/.exocortex.env`, но `setup.sh ≥0.7.0` (WP-273) сохраняет его в `$IWE_ROOT/.exocortex.env`. Пользователи с актуальной…

## 0.29.11 — записей: 5

- [—] `deprecated_files` в манифесте — `update.sh` теперь обнаруживает и удаляет устаревшие L1-файлы (WP-5 Ф-N артефакт #1). Добавлен раздел `deprecated_files` в `update-manifest.json` и…
- [—] `/iwe-bug-report` скилл — создаёт GitHub issue в FMT-exocortex-template через `gh issue create` (6 шагов: категоризация → детали → gh CLI check → issue → URL).
- [—] `docs/onboarding/iwe-layers.md` — онбординг-схема слоёв L1/L2/L3.
- [—] `.stignore` по умолчанию — шаблон добавлен в корень FMT (`717d2d8`). При `update.sh` пользователь получает рабочий `.stignore` для Syncthing (исключены `.git/`, `node_modules/`, `.venv/`, `*.pyc` и…
- [—] `day-close` шаг 10b rule-classifier — добавлен шаг `python3 $HOME/IWE/.claude/scripts/rule-classifier.py` после коммита в SKILL.md day-close (WP-272 Ф5.2, `0e41292`). Обогащает журнал…

## 0.29.10 — записей: 11

- [—] `scripts/iwe-drift.sh` функция `dir_newest_mtime_days_ago` безусловно вызывала `xargs -0 stat -f %m` (BSD-only). На Linux GNU stat `-f` = filesystem info → текст «Inodes: ...» → арифметика падала с…
- [—] `scripts/iwe-audit.sh:227` опечатка `$DRIFT_RC_` (trailing underscore) под `set -u` парсилась как имя переменной `DRIFT_RC_` → unbound при ненулевом exit code drift-скрипта.
- [—] Probe через format-check (`[[ "$_probe" =~ ^[0-9]+$ ]]`) вместо exit-check — отвергает мусор «Inodes: 99», даже если exit=0.
- [—] Detection вынесен на load-time → global array `STAT_MTIME_FLAGS` (один probe вместо повторов).
- [—] `stat $stat_fmt` (unquoted word-split) → `stat "${STAT_MTIME_FLAGS[@]}"` (массив, future-proof).
- [—] `mtime_days_ago` тоже переведён на массив (был тот же exit-check).
- [—] Probe на `/dev/null` вместо `/` (портативнее).
- [—] macOS smoke (BSD): `iwe-drift.sh --top 5` + `iwe-audit.sh` PASS.
- [—] macOS regression-mock (PATH override, fake busybox `stat -f` → «Inodes: 99», exit 0): format-check отверг мусор → GNU branch → drift-таблица c числовым lag. Alpine-регрессия закрыта.
- [—] `validate-template.sh` PASS.
- [—] Linux подтверждение от Дмитрия — ожидается после `update.sh`.

## 0.29.9 — записей: 5

- [—] `extensions/README.md` обновлён: 13 EP вместо 9 (добавлены `day-open.checks`, `day-close.before`, `month-close.before/after`); явный раздел про loader-native (с 0.29.9); manifest sorts ПОСЛЕ suffix…
- [—] `.claude/skills/extend/SKILL.md` каталог: 13 EP в таблице, явный раздел про suffix.
- [—] 7a — manifest + 2 suffix → 3 файла, alphabetic order `health → linear → manifest`.
- [—] 7b — hook без файлов → exit 1.
- [—] 7c — только suffix без manifest → exit 0.

## 0.29.8 — записей: 0


## 0.29.7 — записей: 5

- [—] Фикс: после Step 3 пересчитываю `ENV_FILE` по принципу «что реально есть на диске» (workspace → FMT legacy → exit). Dry-run использует существующий source без побочных эффектов.
- [—] Фикс: инициализация `BACKUP_DIR=""` в начале + защита печати условием `[ -n "$BACKUP_DIR" ] && echo …`. Hint не показывается при clean-FMT — там и backup'а нет.
- [—] Корневая причина: OwnerIntegrity нарушен — source-of-truth для `~/.iwe-paths` дублировался в `setup.sh [4d]` и должен быть в migrate, но не был.
- [—] Фикс системный: новый хелпер `setup/install-iwe-paths.sh` — единственный writer `~/.iwe-paths`. Вызывается из `setup.sh [4d]` (рефакторинг) и из `migrate-to-runtime-target.sh` Step 6 (новый шаг).…
- [—] Фикс: в исходных plist'ах (`roles/*/scripts/launchd/*.plist`, substituted) добавлены ключи `IWE_TEMPLATE/IWE_WORKSPACE/IWE_RUNTIME` в `EnvironmentVariables` как…

## 0.29.6 — записей: 2

- [—] smoke-test 6c переписан — теперь читает РЕАЛЬНЫЙ substituted runner из `.iwe-runtime/`, проверяет что в его sed-выражениях НЕТ literal-значений (только escape-токены), end-to-end проверяет что…
- [—] integration-contract-validator detector #8 `sed_placeholder_escape` — парсит overlay-реестр, для каждого substituted-файла проверяет НЕТ ли bare `{{X}}` в sed-выражениях. Catch'ит регрессию класса…

## 0.29.5 — записей: 8

- [—] `roles/strategist/scripts/cleanup-processed-notes.py:26` — `WORKSPACE = Path.home() / "IWE" / "DS-strategy"` — жёсткий хардкод в Python. Любой пилот с нестандартным `GOVERNANCE_REPO` → fail при…
- [—] 67 хардкодов `DS-strategy` в `roles/strategist/prompts/*.md` и `roles/extractor/prompts/*.md` — bare paths без `{{GOVERNANCE_REPO}}`. LLM получает неверный путь.
- [—] `cleanup-processed-notes.py` — `_resolve_workspace()` функция читает `IWE_WORKSPACE` + `IWE_GOVERNANCE_REPO` из env-vars, fallback на `.exocortex.env` (`grep GOVERNANCE_REPO=`), затем default…
- [—] 67 хардкодов в prompts → `{{GOVERNANCE_REPO}}`. Архитектурное решение: prompts остаются read-only в FMT с placeholders, runner подставляет sed'ом при чтении. Single source, no duplication.
- [—] `run_claude` в `strategist.sh` и `extractor.sh` — добавлена sed-substitution: `{{GOVERNANCE_REPO}}|{{WORKSPACE_DIR}}|{{GITHUB_USER}}` подставляются из env (`IWE_GOVERNANCE_REPO`, `IWE_WORKSPACE`…
- [—] smoke-test 6c: prompts substitution — создаёт временный prompt с `{{GOVERNANCE_REPO}}`, проверяет sed-substitution в стиле runner'а.
- [—] smoke-test 6d: `cleanup-processed-notes.py` резолвит `GOVERNANCE_REPO` из env (с `IWE_GOVERNANCE_REPO=DS-pilot-strategy` → `WORKSPACE = .../DS-pilot-strategy`).
- [—] integration-contract-validator detector #7 `prompts_python_coverage`: ищет hardcoded `DS-strategy` в `roles//*.py` и `roles//prompts/*.md`. Антипаттерн: `.py` без чтения `GOVERNANCE_REPO` env…

## 0.29.4 — записей: 7

- [—] R6.1 BLOCKER — `GOVERNANCE_REPO` dead placeholder. Плейсхолдер был зарегистрирован в overlay, но в 7 substituted-файлах путь `/DS-strategy` был захардкожен…
- [—] R6.2 BLOCKER — permanent false-positive в `update.sh:462`. `grep -rl '{{...}}' "$SCRIPT_DIR"` сканировал FMT, где плейсхолдеры это by design (clean upstream). Каждый запуск `update.sh` у каждого…
- [—] R6.3 IMPORTANT — race window в `build-runtime.sh:338-344`. Окно между `mv RUNTIME → RUNTIME.old.$$` и `mv $BUILD_DIR/runtime → RUNTIME` — `$RUNTIME_DIR` не существует. Если в этот момент scheduler…
- [—] R6.4 IMPORTANT — `update.sh:734` Step 7.5 regression. После WP-273 `.exocortex.env` живёт в workspace. Step 7.5 переприсваивал `ENV_FILE="$SCRIPT_DIR/.exocortex.env"` (FMT, где файла нет) — `if [ -f…
- [—] R6.5 NICE-TO-HAVE — scheduler self-reentrancy. Если предыдущий dispatch завис на 30 мин (Claude CLI), launchd запускал следующий — двойной morning strategist, двойные коммиты. Добавил non-blocking…
- [—] Test 6a: `GOVERNANCE_REPO=DS-pilot-strategy` подставляется в `.iwe-runtime/` (не остаётся literal `DS-strategy`).
- [—] Test 6b: 0 leftover placeholders в `.iwe-runtime/`.

## 0.29.3 — записей: 6

- [—] `setup/smoke-test-fresh-install.sh` — e2e smoke test архитектуры F. Имитирует пилота: создаёт чистый workspace, запускает build-runtime, проверяет idempotency, runner резолвит PROMPTS_DIR в FMT (не…
- [—] Detector #5 `runner_readonly` — runners (strategist.sh, extractor.sh) резолвят PROMPTS_DIR через `$IWE_TEMPLATE`; scheduler.sh имеет `ROLES_DIR_TEMPLATE` для role.yaml lookup. Закрывает R5.1…
- [—] Detector #6 `install_failfast` — все 3 install.sh имеют `grep -qE '\{\{[A-Z_]+\}\}'` check на PLIST_SRC. Закрывает R5.2 regression class.
- [—] Detector #3 `extension_table` regex — раньше терминировался на первом `` ` `` в строке, пропускал EXTENSION POINT'ы где в строке было несколько backtick'ов (например `` ДО `git commit` проверить…
- [—] Detector #4 `hook_artifact` regex — раньше ловил любой `grep TOOL_INPUT`, включая легитимный gating «это git commit вообще?». Уточнён до конкретного антипаттерна R4.5: grep на artifact-имена…
- [—] 3× runners (strategist.sh, extractor.sh, scheduler.sh): WARNING в stderr при использовании legacy fallback (когда `$IWE_TEMPLATE` не экспортирована). Раньше runner молча резолвил на…

## 0.29.2 — записей: 4

- [—] R5.1 — runtime неполный для runners. `.iwe-runtime/` содержал substituted скрипты, но НЕ содержал `roles/*/prompts/`, `roles/*/role.yaml`, `roles/synchronizer/scripts/notify.sh`. При этом…
- [—] R5.2 — install.sh ставил plist с literal `{{IWE_RUNTIME}}`. Если запущен без экспортированной env-переменной (например, в новом shell без source), fallback chain сваливался в legacy FMT path — а…
- [—] R5.3 — update.sh roles reinstall шёл ДО build-runtime. Если roles изменились, install.sh запускался против устаревшего `.iwe-runtime/`. Фикс: Step 6d (build-runtime) добавлен ПЕРЕД roles reinstall…
- [—] R5.4 — migrate-to-runtime-target.sh финальные инструкции неправильно упорядочены. Говорил «1. install agents → 2. source ~/.zshenv» — но install требует env уже expanded. Фикс: новый порядок «1.…

## 0.29.1 — записей: 1

- [—] `setup/integration-contract-validator.sh:43` — ShellCheck SC2145 («Argument mixes string and array») в `verbose() { $VERBOSE && echo " $@" || true; }`. `" $@"` смешивает literal-префикс и массив…

## 0.29.0 — записей: 16

- [—] `.claude/runtime-overlay.yaml` — реестр overlay-файлов (16 substituted + 2 copied_to_workspace + 10 placeholders, включая новый `IWE_RUNTIME`).
- [—] `setup/build-runtime.sh` — idempotent rebuild `.iwe-runtime/` из FMT + `.exocortex.env`. Поддерживает `--dry-run`, `--diff` (drift detection), `--workspace`, `--env-file`, `--quiet`. Atomic swap…
- [—] `scripts/migrate-to-runtime-target.sh` — миграция с dirty FMT (≤0.28.x) на Generated runtime. Backup + git restore + build-runtime.
- [—] `setup/integration-contract-validator.sh` — 4 детектора Spec↔State drift (R4.8, manifest paths / seed refs / extension table / hook artifact). Закрывает класс «корень → детектор откладывается →…
- [—] `.claude/scripts/load-extensions.sh` — wildcard suffix loader (R4.4): возвращает sorted list `extensions/<protocol>.<hook>*.md` (закрывает обещание из extensions/README.md о…
- [—] `memory/hooks-design.md` — принципы проектирования хуков (trigger = artifact, не TOOL_INPUT).
- [—] `seed/strategy/decisions/.gitkeep` — закрывает R4.2.
- [—] `setup.sh` v0.7.0: убран sed-cycle по `$TEMPLATE_DIR` (FMT остаётся clean upstream). `.exocortex.env` сохраняется в `$WORKSPACE_DIR/`, не в FMT. После сохранения env — вызов `build-runtime.sh`.…
- [—] `update.sh` v2.1.0: убран substitution-цикл по NEW/UPDATED файлам. Поиск `.exocortex.env` сначала в workspace, потом FMT (legacy). После git apply — вызов `build-runtime.sh` (R4.6 self-heal…
- [—] 3× `roles/{strategist,extractor,synchronizer}/install.sh`: `LAUNCHD_DIR` через `$IWE_RUNTIME/roles/<role>/scripts/launchd/` с fallback на `$IWE_WORKSPACE/.iwe-runtime/...` и…
- [—] 6× substituted runtime-файлов (plists, config.yaml, scheduler.sh): hardcoded `{{WORKSPACE_DIR}}/FMT-exocortex-template/roles/...` → `{{IWE_RUNTIME}}/roles/...` (R4.7 закрытие, ликвидирует hardcoded…
- [—] `roles/extractor/scripts/extractor.sh:50` — `notify_script` через `$IWE_RUNTIME` с fallback на `$WORKSPACE/.iwe-runtime/` и legacy FMT.
- [—] `memory/protocol-close.md` — EXTENSION POINT для `extensions/protocol-close.checks.md` перенесён ДО Step 1 (Commit + Push). Pre-commit gate, как обещает run-protocol skill (R4.3 закрытие).
- [—] `extensions/README.md` + `.claude/skills/extend/SKILL.md` — таблица hook-orderings обновлена («ДО commit+push» для protocol-close.checks).
- [—] `.claude/hooks/protocol-artifact-validate.sh` — trigger исключительно по `git diff --cached --name-only`, не по `TOOL_INPUT` тексту (R4.5 закрытие). Принцип «trigger = artifact» из…
- [—] `scripts/iwe-audit.sh` — добавлен Раздел 2b «Generated runtime drift» через `build-runtime.sh --diff`.

## 0.28.12 — записей: 4

- [—] `scripts/iwe-audit.sh` — опечатка `$DRIFT_RC_` → `${DRIFT_RC}_`. На macOS под `set -e` опечатка глоталась (bare `$DRIFT_RC_` = пустая строка), на Linux под `set -eu` падала с `unbound variable…
- [—] `scripts/iwe-drift.sh` — функция `dir_newest_mtime_days_ago` использовала `stat -f %m` (macOS-синтаксис) без fallback'а на `stat -c %Y` (Linux). На Linux `xargs stat -f %m` возвращал статистику ФС…
- [—] `roles/strategist/scripts/strategist.sh:9` — `caffeinate -diu -w $$ &` → guard `command -v caffeinate >/dev/null 2>&1 && caffeinate ...`. На Linux `caffeinate` отсутствует, скрипт сыпал `command not…
- [—] `roles/strategist/scripts/strategist.sh:102` — убран `--dangerously-skip-permissions`. Claude Code блокирует флаг под root/sudo (Linux cron от root → отказ). `--allowedTools…

## 0.28.11 — записей: 1

- [—] `generate-manifest.sh` теперь использует `git ls-files` вместо `find`. Раньше скрипт собирал ВСЕ файлы в дереве (включая runtime-артефакты вроде `.exocortex.env`, `.claude.md.base`…

## 0.28.10 — записей: 3

- [—] `setup/validate-template.sh` теперь имеет два режима — `--mode=pristine` (default) и `--mode=installed`. Pristine = текущее поведение (CI, author template-sync, fresh clone до setup) — все 7…
- [—] Guard на post-setup state. Если запущен в pristine-режиме, но детектор находит, что `{{HOME_DIR}}` в `CLAUDE.md` уже подставлен — скрипт печатает подсказку («используйте `setup.sh --validate` или…
- [—] `setup.sh --validate` теперь делегирует структурные инварианты валидатору шаблона. Добавлен шаг `[5/5] Структурные инварианты` — вызов `bash setup/validate-template.sh --mode=installed…

## 0.28.9 — записей: 2

- [—] Третий паттерн в правиле 6/6 — `bash (~|$HOME)/IWE/scripts/`. Раньше валидатор ловил только `FMT-exocortex-template/scripts` и `FMT-exocortex-template/roles/[a-z]*/scripts`. Bare-invocations типа…
- [—] Enumerate-all вместо first-fail. Раньше при FAIL'е выводилось `head -3` нарушений ОДНОГО паттерна, остальные паттерны проверялись, но их вывод тоже обрезался. Теперь все hits аккумулируются в…

## 0.28.8 — записей: 3

- [—] `scripts/iwe-audit.sh` — ложная рекомендация про `scripts/update.sh`. Старая логика для user-mode требовала `update.sh` в `workspace/scripts/`. Но `update.sh` физически живёт ТОЛЬКО в…
- [—] `audit-installation/SKILL.md` — отчёт писался только в терминал. Шаг 5 теперь сохраняет полный отчёт + verdict в `$AUDIT_LOG_DIR/iwe-audit-YYYYMMDD-HHMMSS.log`. Логика выбора пути…
- [—] `audit-installation/SKILL.md` Шаг 1 — отсутствие fallback при поиске `iwe-audit.sh`. Прежняя инструкция предписывала `bash $HOME/IWE/scripts/iwe-audit.sh` — для пилота в user-mode (особенно в Docker…

## 0.28.7 — записей: 2

- [—] `scripts/migrate-initial-marker.sh` — broken frontmatter (один `---`). Раньше при некорректном frontmatter (только открывающий `---` без закрывающего) awk не находил второго `---`, не вставлял…
- [—] `scripts/migrate-initial-marker.sh` — read-only файл молча перезаписывался. На macOS `mv "$TMP" "$TARGET"` заменяет read-only target если у owner'а есть write-permission на parent dir. Фикс: ранний…

## 0.28.6 — записей: 3

- [—] C1 — `.github/workflows/validate-template.yml` — release-blocker: CI был red на 7fbee95, потому что inline blacklist в CI расходился с локальным `setup/validate-template.sh` (CI добавил `roles/` в…
- [—] C2 — `setup/validate-template.sh` — default аргумент изменён с `$HOME/IWE/FMT-exocortex-template` (author-specific) на `dirname $0/..` (parent dir самого скрипта). Теперь `bash…
- [—] C3 — `scripts/migrate-initial-marker.sh` (новый) + `update.sh` — для пользователей со старым clone (до 0.28.5): их `Strategy.md` создан seed'ом, но без маркера `IWE-INITIAL-NEEDED`. После update до…

## 0.28.5 — записей: 10

- [—] B1 — `update-manifest.json` — добавлены 4 группы файлов, которые попали в FMT через коммиты, но не доставлялись через `update.sh`: `.claude/skills/audit-installation/SKILL.md`…
- [—] B2 — `setup.sh` + `update.sh` — substitution map расширен с 7 до 9 placeholder'ов: добавлены `{{GOVERNANCE_REPO}}` и `{{IWE_TEMPLATE}}`. Раньше эти placeholder'ы оставались литералами в…
- [—] B3 — `.claude/skills/strategy-session/SKILL.md` + `seed/strategy/docs/Strategy.md` — initial flow раньше включался только при отсутствии `Strategy.md`, но `seed/strategy/` его создавал → fresh setup…
- [—] B4 — `roles/strategist/prompts/strategy-session.md` + `strategy-session-weekly.md` — старый weekly prompt переименован в `strategy-session-weekly.md`; новый `strategy-session.md` — тонкий dispatcher…
- [—] B5 — `.claude/skills/{day-close,week-close,run-protocol}/SKILL.md` — skills делегировали в несуществующие секции `memory/protocol-close.md § День / § Неделя`. Day Close расширен до полного алгоритма…
- [—] B6 — `.claude/hooks/protocol-artifact-validate.sh:56` — `"Наработки Scout"` убран из mandatory `SECTIONS[]`. Раньше отсутствие секции блокировало DayPlan; теперь Scout проверяется отдельным…
- [—] B7 — `roles/strategist/prompts/{note-review,session-prep}.md` — feedback-triage QA-отчёт стал conditional через `[ ! -d "$WORKSPACE/DS-agent-workspace" ]`. Раньше требование было unconditional →…
- [—] B8 — `roles/synchronizer/scripts/dt-collect.sh:233` — `collect_sessions()` использовал hardcoded `$WORKSPACE/DS-strategy/inbox/open-sessions.log`, минуя `$GOVERNANCE_DIR`. Параметризовано…
- [—] B9 — `.githooks/pre-commit` — блок template validation перенесён ВЫШЕ `[ -z "$STAGED_SH" ] && exit 0`. Раньше commit с staged только `.md/.yaml/.json` пропускал валидацию шаблона → leak'и…
- [—] B10 — `.claude/skills/audit-installation/SKILL.md` + `scripts/iwe-audit.sh` + `scripts/iwe-drift.sh` — три фикса: (a) audit skill ищет `iwe-audit.sh` через `$IWE_SCRIPTS` (canonical) с fallback на…

## 0.28.4 — записей: 3

- [—] `.claude/skills/week-close/SKILL.md` — `{{HOME_DIR}}/IWE/scripts/{backup-icloud,check-dirty-repos}.sh` → `${IWE_SCRIPTS}/...`. Прежний путь — место, куда `setup.sh` ничего не клал; скрипты лежат в…
- [—] `update.sh` — case-фильтр пропагации в workspace расширен с `.claude/{skills,hooks,rules,settings.json}` до включения `.claude/{lib,config,detectors}/*`. Hook `capture-bus.sh` source-ит…
- [—] `.claude/skills/strategy-session/SKILL.md` — skill-обёртка-диспетчер. Detect наличия `Strategy.md` / `WeekPlan` в governance-репо → initial flow (4 шага: цели → неудовлетворённости → первый WeekPlan…

## 0.28.3 — записей: 13

- [—] `.claude/hooks/capture-bus.sh` — диспетчер capture-механизма (DP.SC.025). Запускает enabled-детекторы последовательно на PostToolUse / Stop, передаёт stdout детектора в writer. Никогда не блокирует…
- [—] `.claude/lib/capture_writer.sh` — writer событий: routing event_type → target_path, append в markdown/jsonl. Параметризован (Ф9a WP-217): `agent_incident` пишется в target_repo детектора по умолчанию…
- [—] `.claude/lib/log_formatter.sh`, `.claude/lib/resolve_target_repo.sh` — зависимости writer'а.
- [—] `.claude/lib/capture_selftest.sh` — sanity-check для capture-bus.
- [—] `.claude/lib/behaviour-report.sh` — агрегатор incident-log за период (для R-вопросника Week Close: алгоритм агента «(1) запустить behaviour-report, (2) прочитать incident-log, (3) предъявить…
- [—] `.claude/config/capture-detectors.sh` — реестр детекторов (pipe-separated). 3 активных: `incident`, `decision`, `pattern_awareness`. `permission_request` закомментирован — fail by architecture (30.7%…
- [—] `.claude/detectors/detector_incident.sh` — ловит P3_structure_without_map (Write нового .md в корень репо без проверки routing-карты).
- [—] `.claude/detectors/detector_decision.sh` — ловит решения пользователя по 5 event_type (для DP.M.* decision register).
- [—] `.claude/detectors/detector_pattern_awareness.sh` — ловит P1 (write в feedback_*.md).
- [—] `.claude/detectors/README.md` — контракт интерфейса детектора (input JSON, output JSON или пусто, exit 0 всегда).
- [—] `.claude/capture-config.sh.example` — шаблон override-конфигурации.
- [—] `.claude/settings.json` — регистрация `capture-bus.sh` для PostToolUse(Edit|Write|MultiEdit) и Stop.
- [—] WP-217 Ф9a: `capture_writer.sh` `agent_incident` routing убрал hardcoded путь к авторскому governance-репо. Generic-поведение для пилотов: инциденты пишутся рядом с исполнителем; авторская агрегация…

## 0.28.2 — записей: 5

- [—] `memory/t-checklist.md` — реестр T-действий ТО IWE: 22 действия в Session/Day/Week/Month Close, owner/trigger/symptom-if-skipped для каждого. Класс T (True maintenance, идемпотентно, автопилот).…
- [—] `memory/r-questionnaire.md` — R-вопросник Week/Month Close: 3 недельных + 6 месячных вопросов для переосмысления (не yes/no, экзоскелетный режим — агент даёт факты, человек судит). Класс R…
- [—] `.claude/sync-manifest.yaml` — реестр пар «источник → производное» для `iwe-drift.sh`. Шаблон с 3 generic-парами (protocols-to-skills, protocol-open-to-day-open-skill, staging-validated-to-fmt) +…
- [—] `scripts/iwe-drift.sh` — R23-детектор drift'а пар (mtime-lag, без LLM). MVP-версия: shell + git + stat + awk, без внешних зависимостей. Usage: `bash scripts/iwe-drift.sh [--critical|--top…
- [—] Регламент техобслуживания IWE (элемент #15 культуры работы) теперь промотирован в шаблон: пользователи получают T-checklist, R-вопросник, drift-механизм при `update.sh`. Класс T/S/R закреплён в…

## 0.28.1 — записей: 6

- [—] `memory/hard-distinctions.md` — переписан: 631 → 374 строки (40% сокращение). 23 различения в порядке релевантности (Персона/Скрипт-Агент/MCP-имена/Лог-Инцидент сверху). 15 различений →…
- [—] `memory/navigation.md` — удалена авторская таблица MCP-исходников (`DS-MCP/knowledge-mcp/...`) и ссылка на authored MCP-search. Эти пути относятся к авторскому workspace, не к шаблону.
- [—] `memory/checklists.md` — удалён давний урок про stale knowledge-mcp (фев 2026, не релевантен пилотам).
- [—] `memory/protocol-open.md`, `memory/repo-type-rules.md`, `roles/strategist/scripts/cleanup-processed-notes.py` — placeholder-sub: `DS-my-strategy` → `DS-strategy` (унификация с FMT-конвенцией).
- [—] `CLAUDE.md` — удалена строка «Бот = интерфейс / engines/tailor» в `### Различения (авторские)` §9 (специфика автора, не шаблон).
- [—] `template-sync.sh` strip-list расширен (DS-ai-systems источник): `DS-MCP`, `knowledge-mcp`, `gateway-mcp`, `digital-twin`, `content-pipeline`, `engines/tailor` теперь вычищаются. Sync был застрял в…

## 0.28.0 — записей: 7

- [—] `.claude/settings.json` — `defaultMode` изменён с `"dontAsk"` на `"acceptEdits"`. Это исправление: `dontAsk` означает «по умолчанию запрещать инструменты вне allow-листа», что приводило к скрытым…
- [—] `memory/hard-distinctions.md` HD #27 переписан: «Бот ≠ Платформа; Neon + DT MCP = один ЦД» → «Персона ≠ Память ≠ Контекст». Новая модель пользовательских данных (DP.D.052, WP-257) с критерием…
- [—] `memory/checklists.md` — урок «MCP-индекс может вернуть stale» переформулирован с конкретной датой/документом.
- [—] `memory/protocol-open.md`, `memory/repo-type-rules.md`, `memory/navigation.md` — мелкие уточнения формулировок.
- [—] `roles/strategist/prompts/note-review.md`, `session-prep.md`, `cleanup-processed-notes.py` — точечные правки.
- [—] `roles/synchronizer/scripts/dt-collect.sh` — упрощение (≈36 строк диффа).
- [—] Drift CHANGELOG ↔ update-manifest.json (5 версий 0.27.3-0.27.7 не имели bump манифеста, `update.sh --check` возвращал 0.26.1 как «актуальную»). Bump манифеста до 0.28.0 закрывает разрыв за один шаг.…

## 0.27.7 — записей: 1

- [—] `roles/extractor/scripts/extractor.sh` + `roles/extractor/prompts/inbox-check.md` (WP-7 Ф-1) — подсчёт pending captures и дефиниция в промпте. Старая логика `grep -c '\[analyzed'` ловила substring в…

## 0.27.6 — записей: 3

- [—] `roles/synchronizer/scripts/daily-report.sh` (WP-7 I2) — `mv SchedulerReport → archive/` падал при отсутствующем `archive/`. Под `set -euo pipefail` это прерывало скрипт с non-zero exit →…
- [—] `roles/strategist/scripts/strategist.sh` (WP-7 I1) — `BOLD_BEFORE=$(grep -c ... || echo 0)` при exit 1 от grep (0 matches) давал мультистрочный `"0\n0"` → `$(( BOLD_BEFORE - BOLD_NEW_BEFORE ))` падал…
- [—] Тот же антипаттерн `grep -c ... || echo N)` в 11 точках 7 файлов (субагент-ревью после I1+I2): `setup/validate-template.sh`, `.claude/hooks/protocol-artifact-validate.sh`…

## 0.27.5 — записей: 1

- [—] `roles/strategist/scripts/strategist.sh` переименован концептуально (не файл): context-файл зонтичного WP-7 в авторском governance-репо переехал `archive/wp-contexts/WP-7-bot-tech-debt.md` →…

## 0.27.4 — записей: 3

- [—] `roles/synchronizer/scripts/dt-collect.sh` помечен как author-only (header + raison d'être). Скрипт пишет напрямую в production-БД Neon платформы через `NEON_URL` / `DT_USER_ID`, и эти секреты есть…
- [—] `roles/synchronizer/scripts/scheduler.sh` добавлен guard: `dt-collect.sh` молча пропускается, если `~/.config/aist/env` не содержит `NEON_URL`+`DT_USER_ID`. У пользователей без секретов автора скрипт…
- [—] `roles/synchronizer/README.md` новая секция «Author-only скрипты» объясняет, почему файл есть в шаблоне, но не запускается у пользователей; даёт ссылку на правильный пользовательский путь…

## 0.27.3 — записей: 2

- [—] `setup/validate-template.sh` check 7 + `.github/workflows/validate-template.yml` job «Check hooks cross-ref» (systemic followup к #13). Проверяет cross-ref в обе стороны: (a) FAIL если hook упомянут…
- [—] `setup/validate-template.sh` check 2 добавлен `--exclude='CHANGELOG.md'` (зеркально с CI workflow) — CHANGELOG содержит `/Users/...` в описаниях и создавал false-positive.

## 0.27.2 — записей: 1

- [—] `.claude/hooks/extensions-gate.sh` (closes #13) — добавлен отсутствующий hook. Ссылка на файл жила в `.claude/settings.json:44` (PreToolUse matcher `Edit|Write`) с 7 апр (коммит `af73cd3`, WP-207)…

## 0.27.1 — записей: 7

- [—] Rollback S-27 «Здоровье платформы» — секция содержала авторские сервисы (`@aist_me_bot`, `digital-twin`, `gateway-mcp`, `content-pipeline`, `knowledge-mcp`), не применимые обычному пользователю FMT.…
- [—] L3 leak cleanup (параметризация через env-vars): `.claude/hooks/protocol-artifact-validate.sh`, `scripts/day-close.sh`, `roles/strategist/scripts/cleanup-processed-notes.py`…
- [—] `memory/hard-distinctions.md` HD #49: примеры MCP-именования обобщены (`digital-twin-mcp`, `knowledge-mcp` → `<domain>-mcp`). `memory/checklists.md`: урок «knowledge-mcp stale index» → «MCP-индекс».…
- [—] `.claude/skills/ke/SKILL.md`, `memory/{repo-type-rules,protocol-open}.md`: `DS-my-strategy` → `<governance-repo>` (env).
- [—] CI smoke-test (`.github/workflows/validate-template.yml`): job «Smoke-test protocol hooks on clean user env» — создаёт tmp-окружение с `DS-strategy` + минимальным DayPlan и прогоняет…
- [—] Расширенный blacklist (два уровня) в `validate-template.yml` + зеркально в локальном `setup/validate-template.sh`: глобальный (запрещено везде: `tserentserenov`, `aist_bot_newarchitecture`…
- [—] CI `validate-template.yml` — зеркалирование exclude-логики локального валидатора для путей (`/Users/...`, `/opt/homebrew`) + shellcheck severity: warning→error (0 pred-existing errors, CI зеленеет).

## 0.27.0 — записей: 4

- [—] seed/strategy/docs/Strategy.md — секция «Состояние месяца — фаза стратегической позиции» (PD.FORM.078: 4 фазы Развитие/Хаос/Потолок/Пивот, диагностика по 5 сигналам, playbook, сигналы перехода) +…
- [—] memory/templates-dayplan.md (WeekPlan) — блоки «Применённые критерии отбора РП» (PD.METHOD.017 + Time-boxing Shape Up: РП без 50% бюджета к четвергу → пересмотр на следующей сессии) + «ТОС недели +…
- [—] memory/templates-dayplan.md (DayPlan) — секция «Day Close» с 3 подсекциями (три варианта плана на завтра A/B/C, KE-маршрутизация, сверка с НЭП). Day Close теперь имеет видимую структуру весь день, а…
- [—] memory/templates-dayplan.md, .claude/skills/day-open/SKILL.md, .claude/hooks/protocol-artifact-validate.sh — секция `Здоровье бота (QA)` переименована в `Здоровье платформы` (семантически strict…

## 0.26.4 — записей: 2

- [—] .claude/skills/ke/SKILL.md — блок `## Scope` разграничивает три инструмента знания в IWE: `/ke` (inline capture, R14/R1), `extractor.sh inbox-check` (R2 launchd 3h work hours, создаёт…
- [—] roles/strategist/prompts/session-prep.md (шаг 6, очистка `extraction-reports/`) — условие удаления учитывает `status` во frontmatter: удаляются только `applied` / `rejected` / `no-pending` (старше 7…

## 0.26.3 — записей: 1

- [—] docs/LEARNING-PATH.md (§5.1b Session Open), roles/synchronizer/scripts/dt-collect.sh (collect_sessions) — путь к session log приведён к канону `DS-my-strategy/inbox/open-sessions.log` (вариант для…

## 0.26.2 — записей: 1

- [—] roles/extractor/prompts/inbox-check.md — шаг 1.3 «напиши в лог `No pending captures in inbox`» теперь явно запрещает создавать отдельный лог-файл в `DS-strategy/` или где-либо ещё. Сообщение…

## 0.26.1 — записей: 3

- [—] update-manifest.json — синхронизирован с реальным состоянием репо: добавлены пропущенные файлы `scripts/backup-icloud.sh`, `scripts/check-dirty-repos.sh` (0.26.0)…
- [—] generate-manifest.sh — расширены `EXCLUDE_PATTERNS`/`EXCLUDE_EXACT`: `README.en.md`, `CONTRIBUTING.md`, `LICENSE`, `params.yaml`, `extensions/day-close.after.md`, `extensions/mcp-user.json`.…
- [—] extensions/README.md — уточнена формулировка: `update.sh` не трогает пользовательские файлы (`*.after.md`, `*.before.md`, `*.checks.md`, `mcp-user.json`), но обновляет сам `README.md` как…

## 0.26.0 — записей: 3

- [—] scripts/backup-icloud.sh — еженедельный бэкап IWE в iCloud Drive. Архивирует без `.git`/`node_modules`/`.venv`, хранит 4 последних архива с ротацией. macOS only.
- [—] scripts/check-dirty-repos.sh — скан всех IWE репо (включая вложенные) на незакоммиченные изменения и незапушенные коммиты. Используется в Day Close (шаг 7г) и Week Close.
- [—] week-close/SKILL.md v1.1.0 — добавлены платформенные шаги: бэкап iCloud и скан грязных репо.

## 0.25.1 — записей: 1

- [—] protocol-close.md — KE (Knowledge Extraction) добавлен как обязательный шаг 2.5 Quick Close. Знание маршрутизируется в момент сессии (горячий контекст), не откладывается на Day Close. Чеклист Quick…

## 0.25.0 — записей: 8

- [—] protocol-close.md — сжат 454→97 строк. Остались: маршрутизация, Quick Close inline, формат «Осталось», чеклист Quick Close. Алгоритмы Day Close и Week Close вынесены в отдельные SKILL.md.
- [—] day-open/SKILL.md — шаблоны DayPlan/WeekPlan/итогов удалены из файла (→ `memory/templates-dayplan.md`). Файл сокращён с ~343 до 127 строк.
- [—] update-manifest.json — добавлены: `day-close/SKILL.md`, `week-close/SKILL.md`, `memory/templates-dayplan.md`.
- [—] navigation.md — добавлены строки для `day-close/SKILL.md`, `week-close/SKILL.md`, `templates-dayplan.md`.
- [—] run-protocol/SKILL.md — добавлена строка: `close` (без уточнения) → `close session` по умолчанию.
- [—] .claude/skills/day-close/SKILL.md — полный алгоритм Day Close (шаги 0–11) с TodoWrite enforcement. Шаг 0 = «создать список задач прямо сейчас». Главный фикс: агент больше не может пропустить шаги…
- [—] .claude/skills/week-close/SKILL.md — полный алгоритм Week Close (шаги 0–9) с TodoWrite enforcement.
- [—] memory/templates-dayplan.md — единый источник шаблонов DayPlan, compact dashboard, WeekPlan, итогов дня. Используется day-open (создание) и day-close (запись итогов).

## 0.24.1 — записей: 1

- [—] protocol-close.md — Day Close §3: правило архивации DayPlan (`mv current/DayPlan → archive/day-plans/`) + пункт в чеклист Day Close. Week Close §2: архивация WeekPlan прошлой недели + `git status`…

## 0.24.0 — записей: 5

- [—] protocol-stop-gate.sh — Stop hook: если в сессии был вызов протокольного Skill (day-open|day-close|run-protocol|wp-new), проверяет наличие TodoWrite ≥3 items. Нет → блокирует завершение.…
- [—] settings.json — Stop hook: protocol-stop-gate.sh добавлен первым в Stop-массив (до capture-bus)
- [—] settings.json — PostToolUse matcher расширен: `Read` → `Read|Skill`
- [—] protocol-completion-reminder.sh — расширен на Skill tool: теперь срабатывает при вызове `day-open|day-close|run-protocol|wp-new` и напоминает создать TodoWrite ДО исполнения
- [—] protocol-artifact-validate.sh — добавлены структурные проверки DayPlan: (1) `<details>` collapsible ≥3 блоков, (2) непустые секции Календарь/QA/Scout, (3) мультипликатор `~N.Nx`, (4) Carry-over…

## 0.23.1 — записей: 1

- [—] day-open SKILL.md — шаблон QA-секции: видео показывает только новые за сегодня (не весь stale-архив), заметки проверяются по git log note-review (не carry-over обработанных)

## 0.23.0 — записей: 7

- [—] protocol-artifact-validate.sh — PreToolUse hook (Bash matcher) блокирует `git commit` если DayPlan невалиден: 11 секций, mandatory check, бюджет в формате. Кодовый enforcement вместо промпт-инструкций
- [—] run-protocol SKILL.md — шаг 1b Extension Loading: автоматическая загрузка `extensions/{protocol}.before/after/checks.md` при исполнении любого протокола. Маршрутизация: протоколы с Skill-файлом…
- [—] day-open SKILL.md — шаг 5a2 (видео-сканирование), шаг 7 разбит на 7a-7d (Write → Checks → Commit → Dashboard)
- [—] day-open/protocol-open/protocol-close — HTML-комментарии `<!-- EXTENSION POINT -->` заменены на видимый markdown `EXTENSION POINT:` — агент их читает и исполняет
- [—] wp-gate-reminder.sh — при Day Open инжектирует extension loading reminder
- [—] settings.json — добавлен PreToolUse Bash matcher для protocol-artifact-validate.sh
- [—] settings.json — убрана лишняя строка `.claude/hooks` из `additionalDirectories` (вызывала открытие файлов хуков как вкладок в Cursor/VS Code на Windows)

## 0.22.0 — записей: 4

- [—] verify SKILL.md — два новых типа верификации: `chain` (data flow check, CoVe stage 3) и `adversarial` (scope & bias check, pre-mortem). Context isolation sub-agent с чеклистами
- [—] day-close.sh — маппинг dir→source из L2 (sources.json) + L4 (sources-personal.json). Раздельные вызовы selective-reindex через SOURCES_CONFIG. Фикс хронического reindex failure с 20 марта
- [—] verify SKILL.md — обновлена нумерация шагов (0→4), unified verdict формат, автоопределение chain/adversarial по контексту
- [—] update-manifest.json → v0.22.0

## 0.21.0 — записей: 5

- [—] setup.sh v0.5.1 — секция T3+ в `.exocortex.env`: ORY_TOKEN, L4_BACKEND, L4_DATABASE_URL. setup.sh при уровне T3/T4 спрашивает токен и backend (можно пропустить). Единый файл конфигурации для всей IWE…
- [—] update.sh — исправлен парсер env-файла: `IFS='=' read` заменён на `${line%%=*}` + `${line#*=}` — корректно читает значения с `=` внутри (URL, токены). Добавлен detect `~/.iwe-env`: если файл…
- [—] .githooks/pre-commit — блокирует коммит если `.exocortex.env` попал в staged files
- [—] update.sh — ORY_TOKEN/L4_BACKEND/L4_DATABASE_URL читаются из `.exocortex.env` но не подставляются в template-файлы (секция secrets, только для Gateway-скриптов)
- [—] update-manifest.json → v0.21.0

## 0.20.0 — записей: 4

- [—] setup.sh v0.5.0 — градиентный вход: флаг `--level=T1/T2/T3/T4` + интерактивный выбор при запуске. T1=минимум (≤15 мин), T2=+ОРЗ+extensions, T3=+Pack+бот, T4=+роли+launchd. Каждый уровень дополняет…
- [—] ADR-003 — спецификация платформы-хостинга: два слоя доставки (дистрибутив vs хостинг), скриптуемый API (`--yes`), градиентный вход, экспорт, Vagrant-образ, ЭМОГССБ 60/70
- [—] update-manifest.json → v0.20.0
- [—] setup.sh — INSTALL_LEVEL сохраняется в `.exocortex.env`; шаги 4, 5 зависят от уровня; Next steps адаптированы под уровень

## 0.19.0 — записей: 4

- [—] skill /extend — каталог расширяемости IWE. Показывает все extension points, параметры params.yaml, конфиг day-rhythm-config.yaml, инструкции по sharing. Предлагает следующий шаг на основе текущих…
- [—] update.sh Step 6b — авто-фикс ссылок при миграции: обновляет абсолютные пути и имя репо в пользовательских файлах extensions/ и MEMORY.md при переименовании/переезде IWE
- [—] extensions/README.md — секция «Несколько расширений одного hook» (суффиксы для конфликтов) и «Sharing» (формат bundle-пакетов расширений)
- [—] update-manifest.json → v0.19.0: добавлен `.claude/skills/extend/SKILL.md`

## 0.18.0 — записей: 13

- [—] extensions/ — 12 extension points в протоколах (day-open before/after, day-close checks, week-close before/after, protocol-close checks/after). Пользователь добавляет файл…
- [—] params.yaml — 8 персистентных параметров управляют условными шагами протоколов: `video_check`, `multiplier_enabled`, `reflection_enabled`, `lesson_rotation`, `auto_verify_code`, `verify_quick_close`…
- [—] extensions/day-close.after.md — пример расширения: рефлексия дня (3 вопроса). Управляется `reflection_enabled` в params.yaml
- [—] update.sh — 3-way merge для CLAUDE.md через `git merge-file`. Пользовательские правки в §1-7 сохраняются при обновлении платформы. Fallback на USER-SPACE для первого обновления
- [—] setup.sh — создаёт `.claude.md.base` при установке (base для 3-way merge)
- [—] .gitignore — `.claude.md.base` (служебный файл merge)
- [—] CLAUDE.md §7 — инструкции для Claude по загрузке extensions и чтению params.yaml
- [—] protocol-close.md — `<!-- YOUR CUSTOM CHECKS HERE -->` заменены на `<!-- EXTENSION POINT: загрузить extensions/X.md -->` (единый формат)
- [—] protocol-close.md — условные шаги привязаны к params.yaml: multiplier_enabled (шаг 5), video_check (шаг 6д), lesson_rotation (week-close шаг 1), auto_verify_code (шаг 4b), verify_quick_close (шаг 7)
- [—] update.sh — «Не затрагиваются» обновлён: extensions/, params.yaml, 3-way merge вместо USER-SPACE
- [—] skill /iwe-update — агент-обновитель: вызывает update.sh, парсит CHANGELOG, объясняет изменения на человеческом языке, анализирует совместимость с extensions/params, помогает разрешить конфликты…
- [—] day-open шаг 5 — автоматическая проверка обновлений (`update.sh --check`) → «Требует внимания» если доступна новая версия
- [—] AUTHOR-ONLY — механизм `<!-- AUTHOR-ONLY -->` заменён на extensions/ (авторские блоки мигрированы в extension-файлы)

## 0.17.1 — записей: 2

- [—] day-open/SKILL.md — БЛОКИРУЮЩЕЕ: пошаговое исполнение через TodoWrite. Каждый шаг = задача, переход только после отметки. Предотвращает пропуск шагов (carry-over, mandatory, запись) из-за загрязнения…
- [—] protocol-open.md — ссылка на пошаговое исполнение Day Open (аналогично Close)

## 0.17.0 — записей: 6

- [—] day-open/SKILL.md v1.1 — carry-over из вчерашнего DayPlan теперь обязательная логика (не конфиг-флаг). Убран `day_close.review_yesterday_close`
- [—] day-open/SKILL.md — алгоритм и шаблоны объединены в один файл. Шаг 2: приоритет входов (carry-over → WeekPlan → mandatory)
- [—] day-open/SKILL.md — `{{GOVERNANCE_REPO}}` вместо prose-текста (формализация)
- [—] day-rhythm-config.yaml — добавлен `calendar_ids: []` (Day Open запрашивает все календари или указанные)
- [—] day-rhythm-config.yaml — убран `day_close` (carry-over = часть алгоритма, не настройка)
- [—] day-open/SKILL.md §6 — ссылки на источники (URL) обязательны в секции «Мир»

## 0.16.9 — записей: 3

- [—] scheduler.sh — `TASK_TIMEOUT_SHORT` (300s) и `TASK_TIMEOUT_LONG` (1800s) для всех задач dispatch
- [—] scheduler.sh — macOS perl timeout fallback (нет GNU timeout)
- [—] scheduler.sh — AC sleep check (pmset) в dispatch() — предупреждение при sleep≠0 на зарядке

## 0.16.8 — записей: 3

- [—] day-open/SKILL.md — механизм `mandatory_daily_wps`: стратег читает из `day-rhythm-config.yaml` обязательные РП для каждого дня. Нет в WeekPlan → «Требует внимания»
- [—] day-open/SKILL.md — механизм `review_yesterday_close`: опциональное чтение Close прошлого дня при Day Open (carry-over, незакрытые вопросы)
- [—] day-rhythm-config.yaml — секции `mandatory_daily_wps` и `day_close` (закомментированные примеры)

## 0.16.7 — записей: 1

- [—] hooks/close-gate-reminder.sh — v3: hook теперь инжектирует БЛОКИРУЮЩУЮ инструкцию вызвать `/run-protocol` вместо напоминания «Read protocol-close.md». Устраняет пропуск шагов при ручном исполнении…

## 0.16.6 — записей: 2

- [—] docs/onboarding — актуализация onboarding-документов: IWE = ОС (не среда/платформа), 4 компонента (Ядро мышления, Культура работы, Модель мастерства, Сообщество), теории (ШСМ) + культура работы (14…
- [—] docs/DATA-POLICY — убраны несуществующие standard/personal, добавлена свобода данных (§6.1), два слоя доставки, актуальная структура (memory/, extensions/, params.yaml)

## 0.16.5 — записей: 1

- [—] docs — синхронизация документации: README сценарии → ссылки на SC.001-SC.015 (USE-CASES.md), FAQ подписки унифицированы («при необходимости»), IWE-HELP роли уточнены (3 в шаблоне / 21 на платформе)…

## 0.16.4 — записей: 1

- [—] notify-update.yml — 3-уровневый фильтр уведомлений: (1) наличие коммитов, (2) наличие changelog с буллет-пунктами, (3) проверка значимости (ключевые слова, значимые файлы, ≥3 пунктов). Незначительные…

## 0.16.3 — записей: 1

- [—] seed/strategy/docs/Strategy.md — переструктурирование шаблона: Фокус Q{N} (текущий квартал, details open) первым, затем Годовой план (фазы, roadmap, MAPSTRATEGIC, риски, Q итоги внутри). Убрана…

## 0.16.2 — записей: 1

- [—] skill /iwe-rules-review — 3 вопроса → 4 вопроса (по актуальному DP.M.008: чему научился? какое правило мешало? какого не хватало? какое обходил?)

## 0.16.1 — записей: 1

- [—] skill /archgate — L2.1 Переносимость данных добавлена, L2.2–L2.7 перенумерованы (7 доменных характеристик). АрхГейт 8.0+ (WP-177)

## 0.16.0 — записей: 16

- [—] WeekReport deprecated — итоги недели теперь записываются в секцию «Итоги W{N}» внутри WeekPlan. Отдельный файл WeekReport больше не создаётся. АрхГейт 8.9 (62/70)
- [—] week-review.md — пишет секцию в WeekPlan, не создаёт файл
- [—] session-prep.md — читает секцию из WeekPlan, не ищет файл WeekReport
- [—] Кроссплатформенное предотвращение сна — `strategist.sh` и `scheduler.sh` автоматически блокируют засыпание: macOS `caffeinate -diu` / Linux `systemd-inhibit`. Флаг `-s` не используется — он…
- [—] SETUP-GUIDE: инструкции wake+sleep для macOS, Linux, Windows. Включая `pmset -b sleep 0` для ноутбуков и Charge Limit рекомендацию
- [—] PLATFORM-COMPAT: sleep prevention — документация кроссплатформенных ограничений
- [—] Agent Workspace (optional, WP-176) — `setup/optional/setup-agent-workspace.sh` создаёт отдельный репо для данных агентов. SETUP-GUIDE Этап 7 с осознанным описанием когда нужен/не нужен
- [—] daily-report.sh conditional — если DS-agent-workspace/.git существует → отчёты туда, иначе DS-strategy/current/ (обратная совместимость)
- [—] LEARNING-PATH §11 FAQ — 3 развёрнутых ответа (Windows+WSL, заметки, бот отвечает не то) + 6 табличных строк (WP-166: feedback_triage кластеры)
- [—] docs/LEARNING-PATH, USE-CASES, SETUP-GUIDE, onboarding-guide — убран WeekReport
- [—] roles/strategist/README, seed/strategy/CLAUDE.md — WeekReport помечен deprecated
- [—] synchronizer/scripts/templates/strategist.sh — ищет WeekPlan вместо WeekReport
- [—] README.md FAQ — обновлён вопрос про сон/выключение
- [—] install.sh — кроссплатформенные подсказки при установке
- [—] session-prep.md, note-review.md — ссылки на QA-отчёт: agent-workspace или DS-strategy
- [—] collectors.d/README.md — unsatisfied → agent-workspace path

## 0.15.2 — записей: 1

- [—] «Правила IWE» → «Культура работы IWE» — переименование в skill /iwe-rules-review и шаблоне отчёта (согласование с DP.M.008)

## 0.15.1 — записей: 1

- [—] Битые ссылки — исправлено 17 ссылок в 6 файлах: кросс-репо `../../../../PACK-digital-platform/` → абсолютные GitHub URL в onboarding-guide, `LEARNING-PATH.md`/`SETUP-GUIDE.md` → `docs/` в CHANGELOG…

## 0.15.0 — записей: 8

- [—] Context Compression (WP-172) — входной overhead снижен с ~27K до ~13K токенов (2x сжатие). АрхГейт 8.9
- [—] CLAUDE.md — сжат до ~90 строк ядра (было ~280). Убраны детали, дублирующие memory/ и .claude/rules/
- [—] protocol-open.md — шаблоны DayPlan/WeekPlan вынесены в skill `/day-open` (lazy loading, ~8K экономия в обычных сессиях)
- [—] skill `/day-open` — `.claude/skills/day-open/SKILL.md`: шаблоны DayPlan, WeekPlan, compact dashboard. Загружаются только при Day Open
- [—] Lesson Hygiene в protocol-close.md (Day Close §3b) — симметрия: Open пишет уроки → Close чистит. Предотвращает раздувание MEMORY.md. Цель: ≤8 уроков
- [—] validate-template.sh — проверка `.claude/skills/day-open/SKILL.md`
- [—] skill `/iwe-rules-review` — еженедельное ревью культуры работы IWE (DP.M.008 #14). Триггер: Week Close
- [—] HD #43 — различение «Правило ≠ Реализация правила» (DP.M.008)

## 0.14.2 — записей: 2

- [—] protocol-open.md § Ритуал (Шаг 1) — каждый элемент отчёта с новой строки (было: всё в одну строку)
- [—] LEARNING-PATH.md § Ритуал — аналогичное форматирование

## 0.14.1 — записей: 1

- [—] wp-gate-reminder.sh — при Day Open триггере инжектит реальную дату через `date` (currentDate от Anthropic может врать из-за timezone). На остальные сообщения — стандартный WP Gate reminder

## 0.14.0 — записей: 5

- [—] dt-collect.sh plugin-архитектура — ядро (L3) содержит 11 стандартных коллекторов, `collectors.d/*.sh` — точка расширения для персональных (L4) коллекторов. Plugin loader автоматически source'ит файлы…
- [—] collectors.d/README.md — документация формата плагинов (COLLECTOR/TARGET headers, формат функций)
- [—] 6 новых коллекторов в ядре — multiplier (DayPlan budget), WP-REGISTRY stats, Pack entities, fleeting notes, scheduler reports health
- [—] 2 новых JSONB-секции — `2_8_ecosystem`, `2_9_knowledge` (через плагины)
- [—] portable_date_offset — кроссплатформенная обёртка для `date -v` (macOS + Linux)

## 0.13.5 — записей: 2

- [—] protocol-close.md — формула мультипликатора: partial РП считаются (% × бюджет), мелкие РП = 0.25h (не 0). Недельный мультипликатор = Σ бюджетов ВСЕХ отработанных РП / WakaTime. Убран плановый бюджет…
- [—] hard-distinctions — HD #42: Тир ≠ Квалификация (DP.D.042)

## 0.13.4 — записей: 3

- [—] Priority Gate — новый Pre-action Gate в CLAUDE.md: при создании РП ≥3h обязательный вопрос «К какому результату месяца?» (R{N} / поддержка / off-plan)
- [—] wp-new SKILL — 5-е место записи: маппинг РП → Результат в `Strategy.md`. Порог ≥3h
- [—] Strategy template — секции «Результаты месяца» и «РП → Результаты» с пояснениями допустимых значений

## 0.13.3 — записей: 1

- [—] MCP подключение — `setup.sh` использовал нерабочий `claude mcp add --transport http` → заменён на инструкцию через claude.ai/settings/connectors. Обновлены: SETUP-GUIDE §1.3b, IWE-HELP…

## 0.13.2 — записей: 3

- [—] cloud-scheduler.yml — расширенный IWE Health Check: мульти-репо коммиты (24ч + 7д), проверка свежести backup (>48ч), статус бота (health endpoint), WP-статистика, светофор (🟢/🟡/🔴). Настройка через…
- [—] LEARNING-PATH §2.6 — практический гайд настройки расширенного Health Check (4 шага)
- [—] cloud-scheduler.yml — защита от пустого `STRATEGY_REPO` при `basename`, точный grep для WP-статистики (`| in_progress` вместо `in_progress`)

## 0.13.1 — записей: 4

- [—] inbox-check.md — `[processed]` → `[analyzed]`: метка при анализе captures, не при записи в Pack. Корневая причина потери 76% captures
- [—] session-close.md — добавлен шаг 8a: пометка captures `[processed]` только после подтверждённой записи в Pack
- [—] extractor.sh — учёт `[analyzed]` в подсчёте pending captures
- [—] session-prep.md — архивация `[processed]` captures в `archive/captures/` вместо удаления

## 0.13.0 — записей: 2

- [—] generate-post-image.py (S48) — генерация обложек для постов через OpenAI GPT Image 1 API. SOTA-промпт: полный текст статьи → визуальная метафора. Настроение по аудитории (wide/community/advanced).…
- [—] COVER-IMAGES.md — подробная инструкция: API key, промпты, параметры, стоимость, интеграция с публикаторами

## 0.12.0 — записей: 6

- [—] cloud-scheduler.yml — GitHub Actions workflow для облачной автоматики IWE. Базовый уровень (без LLM, $0/мес): backup memory → exocortex, health check ночной автоматики, опциональные…
- [—] setup-cloud-scheduler.sh — скрипт настройки: проверка gh CLI, установка GitHub Secrets, тестовый запуск workflow
- [—] LEARNING-PATH §2.6 — Cloud Scheduler добавлен в таблицу опциональных сервисов
- [—] README FAQ — вопрос про работу IWE при выключенном Mac
- [—] CLAUDE.md — 3-слойная структура: L1 (§1-§7 платформа), L2 (§8 staging), L3 (§9 авторское). `update.sh` обновляет только L1. UC Gate добавлен в Pre-action Gates
- [—] cloud-scheduler Telegram — HTML-формат вместо markdown (корректное отображение bold)

## 0.11.1 — записей: 3

- [—] Haiku R23 верификатор в Quick Close — закрытие сессии теперь запускает sub-agent Haiku R23 с context isolation (VR.SOTA.002). Шаг 7 в алгоритме Quick Close. Исключения: сессия ≤15 мин, сессия без…
- [—] roles/verifier/README.md — таблица «Когда вызывается» уточнена: Quick Close (шаг 7) + Day Close (шаг 10) + Session Close (Verification Gate)
- [—] CLAUDE.md правило 6 — обновлено: Quick Close + Day Close через Haiku R23

## 0.11.0 — записей: 6

- [—] update.sh v2.0.0 — полностью переписан: curl + манифест вместо git merge. Работает с template repos (created via "Use this template"), которые не имеют общей git-истории с upstream. Self-update…
- [—] Превью перед обновлением — показывает новые файлы, обновлённые, не затрагиваемые. Пользователь решает: применить или отменить
- [—] setup-calendar.sh — уточнён текст предупреждения Google (название «IWE MIM», пояснение про unverified app)
- [—] [update-manifest.json](https://github.com/TserenTserenov/FMT-exocortex-template/blob/main/update-manifest.json) — манифест всех платформенных файлов (100+ записей) с описаниями. Используется…
- [—] [DP.SC.019](https://github.com/MimEcoSys/PACK-digital-platform/blob/main/pack/digital-platform/08-service-clauses/DP.SC.043-template-update.md) — сценарий «Обновление экзокортекса» + сервис S50…
- [—] Инструкция «настрой календарь» в CLAUDE.md — при запросе пользователя Claude запускает `setup-calendar.sh`

## 0.10.0 — записей: 7

- [—] Трёхуровневый Close — Session Close (13 шагов) заменён на Quick Close (6 шагов, ~3 мин) + Day Close (13 шагов, ~10 мин) + Week Close (3 шага). Governance перенесён с сессии на конец дня. Экономия…
- [—] Haiku R23 — верификация только при Day Close (≥10 пунктов), не Quick Close (6 пунктов). Экономия N-1 вызовов sub-agent в день
- [—] MEMORY.md ≤100 строк — done-РП удаляются при Day Close (были ≤200, копились). Экономия ~30% токенов на авто-загрузку
- [—] CHANGELOG FMT перенесён из Day Close в Quick Close (шаг 1b) — пока контекст свежий, не теряется к вечеру
- [—] [scripts/day-close.sh](https://github.com/TserenTserenov/FMT-exocortex-template/blob/main/scripts/day-close.sh) — автоматизация 3 механических шагов Day Close одной командой: backup memory/ →…
- [—] Мультипликатор IWE — шаг 5 Day Close: расчёт усиления от агента-экзоскелета (Бюджет закрыт / WakaTime). Таблица в итогах дня
- [—] Week Close — ротация уроков (≤15 актуальных), свежая таблица РП, аудит memory-файлов

## 0.9.1 — записей: 1

- [—] Close Gate hook — `close-gate-reminder.sh`: при триггерах закрытия инжектит compact-чеклист Session Close (10 шагов) или направляет на полный Day Close. Экономия ~5K токенов (не перечитывает…

## 0.9.0 — записей: 4

- [—] Hooks enforcement — три автоматических hook'а для надёжности агента: WP Gate (напоминание на каждый prompt), Protocol Completion (верификация после загрузки протокола), PreCompact Checkpoint…
- [—] Скилл `/run-protocol` — пошаговое выполнение протокола ОРЗ через TodoWrite с обязательной верификацией. `.claude/skills/run-protocol/`
- [—] Различение `settings.json` ≠ `settings.local.json` — проектный (hooks, в git) vs персональный (permissions, gitignored). При клонировании hooks работают из коробки
- [—] Compliance-метрика верификации — строка «запускался ли /verify» в чеклисте Session Close

## 0.8.8 — записей: 2

- [—] Google Calendar одной командой — `bash setup/optional/setup-calendar.sh`: скачивает OAuth credentials с Gist, настраивает MCP, запускает авторизацию в браузере. Пользователю не нужен GCP Console…
- [—] [SETUP-GUIDE](https://github.com/TserenTserenov/FMT-exocortex-template/blob/main/docs/SETUP-GUIDE.md) Этап 5 обновлён: `setup-calendar.sh` вместо ручной настройки GCP

## 0.8.7 — записей: 1

- [—] Чеклист-верификация (Haiku R23) — блокирующее правило в [CLAUDE.md](https://github.com/TserenTserenov/FMT-exocortex-template/blob/main/CLAUDE.md) §2: после любого протокола с чеклистом запускается…

## 0.8.6 — записей: 4

- [—] Роли верификации (R23-R24) — skill /verify + [hard-distinctions](https://github.com/TserenTserenov/FMT-exocortex-template/blob/main/memory/hard-distinctions.md) #38-40 (WP-122)
- [—] Governance-синхронизация в [Day Close](https://github.com/TserenTserenov/FMT-exocortex-template/blob/main/memory/protocol-close.md) — проверка REPOSITORY-REGISTRY, navigation.md, MAP.002↔PROCESSES.md…
- [—] Collapsible sections в [LEARNING-PATH](https://github.com/TserenTserenov/FMT-exocortex-template/blob/main/docs/LEARNING-PATH.md) и…
- [—] Онбординг переработан: пользователь в центре, принципы двусторонние

## 0.8.5 — записей: 1

- [—] [USE-CASES.md](https://github.com/TserenTserenov/FMT-exocortex-template/blob/main/docs/use-cases/USE-CASES.md) — каталог всех 15 сценариев использования IWE (WP-116):

## 0.8.4 — записей: 1

- [—] [docs/onboarding/](https://github.com/TserenTserenov/FMT-exocortex-template/blob/main/docs/onboarding/) — руководство-онбординг IWE для новичков (WP-120):

## 0.8.3 — записей: 1

- [—] [LEARNING-PATH.md](https://github.com/TserenTserenov/FMT-exocortex-template/blob/main/docs/LEARNING-PATH.md) §11 — FAQ: cross-device workflow (ноут + десктоп, кросс-ОС)

## 0.8.2 — записей: 4

- [—] [protocol-open.md](https://github.com/TserenTserenov/FMT-exocortex-template/blob/main/memory/protocol-open.md) — 4-й класс верификации `trivial` (Haiku): результат очевиден, проверка не нужна
- [—] [protocol-open.md](https://github.com/TserenTserenov/FMT-exocortex-template/blob/main/memory/protocol-open.md) — два сценария переключения модели:
- [—] [SETUP-GUIDE.md](https://github.com/TserenTserenov/FMT-exocortex-template/blob/main/docs/SETUP-GUIDE.md) §0.5b — класс верификации в таблице моделей + описание двух сценариев
- [—] [LEARNING-PATH.md](https://github.com/TserenTserenov/FMT-exocortex-template/blob/main/docs/LEARNING-PATH.md) §5.1b — trivial в таблице классов + два сценария переключения

## 0.8.1 — записей: 3

- [—] CLAUDE.md — различение «Скилл ≠ Роль ≠ Протокол» (WP-104)
- [—] hard-distinctions.md HD #11 — переработка: обещание (SC) ≠ описание метода ≠ сервис (WP-101, DP.D.039)
- [—] protocol-open.md — режим `interactive: false` для Day Open (вывод одним блоком, «Требует внимания» в конце)

## 0.8.0 — записей: 7

- [—] Видеоинтеграция (WP-102) — 6 сценариев связи видеозаписей с РП:
- [—] day-rhythm-config.yaml → `video` — секция конфигурации: directories (массив), extensions, stale_days, auto_transcribe, content
- [—] video-scan.sh — скрипт сканирования (`roles/synchronizer/scripts/`): --new, --stale, --dry-run
- [—] protocol-close.md — шаг «Видео за день» в Day Close + пункт в чеклисте Session Close
- [—] protocol-work.md §2b — сценарии транскрипции и генерации контента из видео
- [—] protocol-open.md — шаблоны DayPlan и WeekPlan дополнены секцией «Видеозаписи» и «Видео-ревью»
- [—] Повестка Strategy Session — добавлен пункт «Видео-ревью (С3)»

## 0.7.0 — записей: 3

- [—] Google Calendar MCP — Этап 5 в SETUP-GUIDE: подключение Google Calendar за 2 мин
- [—] protocol-open.md шаг 4c — «Календарь дня»: все календари, локальный timezone, фильтр конфиденциальных, свободные слоты
- [—] Шаблон DayPlan — секция «Календарь» с таблицей событий

## 0.6.4 — записей: 9

- [—] gh repo fork: убран несовместимый флаг `--remote` из SETUP-GUIDE, setup.sh, ADR-001
- [—] README.md: `git clone` → `gh repo fork --clone` (согласованность с SETUP-GUIDE)
- [—] strategist.sh: `cleanup-processed-notes.py` → `.sh` (файл .py не существовал)
- [—] strategist.sh: хардкод авторского пути к notify.sh → относительный через `$SCRIPT_DIR`
- [—] strategist.sh, dt-collect.sh: `$HOME/IWE` → `{{WORKSPACE_DIR}}` (подставляется setup.sh)
- [—] update.sh: нумерация шагов `[1/4],[2/4]` → `[1/6],[2/6]`
- [—] setup-wakatime.md: `wakatime-cli` → `~/.wakatime/wakatime-cli` (полный путь)
- [—] SETUP-GUIDE.md: MCP-команды отделены от bash-блока (пользователи пытались запускать в терминале)
- [—] DS-strategy naming: унифицировано `DS-my-strategy` → `DS-strategy` в protocol-open.md (15 замен). Убран FAQ-костыль из LEARNING-PATH

## 0.6.3 — записей: 7

- [—] Cross-platform compat: `sed -i ''` → `sed_inplace` (setup.sh, update.sh) — GNU sed (Linux)
- [—] Cross-platform compat: `date -v` → `portable_date_offset` (fetch-wakatime.sh, dt-collect.sh, scheduler.sh) — GNU date (Linux)
- [—] Cross-platform compat: `osascript` → fallback notify-send (strategist.sh, extractor.sh) — Linux desktop
- [—] Cross-platform compat: setup.sh шаг 5 пропускается на Linux (нет launchctl)
- [—] docs/PLATFORM-COMPAT.md — чеклист + обёртки + grep-команды
- [—] .githooks/pre-commit — блокирует коммит с raw платформозависимыми конструкциями
- [—] CLAUDE.md §Различения — правило кроссплатформенности

## 0.6.2 — записей: 13

- [—] Правило Ru-first (SPF §5 п.13) — русский как основной язык шаблонов/протоколов/документов. EN только для YAML-ключей, аббревиатур из онтологии, имён собственных
- [—] AUTHOR-ONLY зоны — маркеры `<!-- AUTHOR-ONLY -->` для пользовательских расширений протоколов. При обновлении шаблона (template-sync/update.sh) пользовательский контент сохраняется
- [—] Параметризация strategy_day — день стратегирования читается из `day-rhythm-config.yaml`, не хардкодится. Пользователь может выбрать любой день недели
- [—] Strategy_day guard в Day Open — в день стратегирования DayPlan не создаётся (план дня уже в WeekPlan → секция «План на [день]»)
- [—] LEARNING-PATH — §2.4 три паттерна кастомизации (L3→L4), §5.1 strategy_day guard, §5.5 настройка дня стратегирования, Quick Reference: 2 новых вопроса
- [—] Четвёртая зона — CONFIG (day-rhythm-config.yaml) + AUTHOR-ONLY в описании структуры (§2.2)
- [—] Двухуровневый FAQ — категоризация Pack FAQ (§11, 5 категорий) и LEARNING-PATH Quick Ref (§11, 4 категории). Процесс capture-to-FAQ формализован. Правило синхронизации FAQ в CLAUDE.md
- [—] strategist.sh — маршрутизация morning читает `strategy_day` из конфига вместо `DAY_OF_WEEK -eq 1`
- [—] protocol-open.md — шаг 4 блокирующий (strategy_day → пропуск DayPlan), шаг 7 с guard, DayPlan Gate с исключением
- [—] README.md §FAQ — расширен (3 новых вопроса) + ссылки на полный FAQ в Pack и LP
- [—] `day-rhythm-config.yaml` уже содержит `strategy_day: monday` — менять не нужно, если понедельник подходит
- [—] Если вы скопировали `scheduler.sh` из авторского репо — замените `"$DOW" = "1"` на чтение из конфига (см. авторский `scheduler.sh`)
- [—] AUTHOR-ONLY зоны: в протоколах появятся плейсхолдеры `<!-- YOUR CUSTOM CHECKS HERE -->` — замените на свой контент при необходимости

## 0.6.1 — записей: 7

- [—] README переработан — концептуальный файл для новичков: проблемы пользователей, аналогия IDE↔IWE, протокол ОРЗ, сценарии (рабочие + личные), сравнение с Obsidian/Notion. Детали установки →…
- [—] LEARNING-PATH полная актуализация — §5 ОРЗ-фрактал (День+Сессия), §1.3 тиры T0-T4, §3.2 различения HD #25-36, §5.3 dual routing, §8.1 АрхГейт + coordination cost, §11 чеклист Close 7→15 шагов
- [—] Backport live→template — protocol-work.md (ОРЗ День+Сессия), protocol-close.md (ветки, ad-hoc), hard-distinctions.md (HD #25-36), checklists.md (Pack + посты)
- [—] Activation Gate — колонка «Активация» в WP-REGISTRY (3 типа: date/dep/on-demand) + Dormant Review в WeekPlan
- [—] ONTOLOGY.md расширение — 4 реализационных понятия (Creative Pipeline, Guard, DayPlan, WeekPlan) + 14 аббревиатур (TTL, HD, SOTA, SOP, DDD, CLI, API, LMS, S2R, PII, RSS, TG, ZP)
- [—] Activation Check + Dormant Review — секции в protocol-open.md (шаблон WeekPlan + повестка стратегирования)
- [—] LEARNING-PATH §5.5 — описание Activation Gate, 2 новых вопроса в Quick Reference

## 0.6.0 — записей: 22

- [—] Session tracking — `open-sessions.log` в протоколах Open/Close для отслеживания активных сессий
- [—] TG-оповещения об обновлениях — GitHub Action ежедневно проверяет коммиты и отправляет дайджест подписчикам через бот
- [—] 5-й архитектурный вид (Методы) — sync с DP.IWE.001, расширение архитектурной документации
- [—] roles.md — описание ролей экзокортекса + обновление memory policy
- [—] ONTOLOGY.md в формате SPF.SPEC.002 — каскадная онтология с двуязычным глоссарием
- [—] KE dual routing — экстрактор знаний разделяет: доменное → Pack, реализационное → DS docs/
- [—] dt-collect — скрипты сбора данных активности для ЦД (WakaTime + git + sessions + WP stats) в роли синхронизатора
- [—] Day Rhythm config — конфиг ритма дня: помодоро-напоминания через WakaTime + launchd
- [—] Опциональные компоненты — README для модульных расширений, обновлённое дерево структуры
- [—] HD #29-31 — новые hard distinctions: Pack≠DS, роли владельца, Шаг 0 Open-протокола, Capture реализации
- [—] README компактный — переработан для новичков, убраны лишние детали
- [—] DP.AGENT → DP.ROLE — миграция идентификаторов, удалён дубль strategist-agent/ (WP-63)
- [—] repo-type-rules — DS-ecosystem-development = governance + staging for Pack
- [—] LEARNING-PATH — добавлен триал 30 дней + подписка БР в таблице тиров
- [—] CLAUDE.md §6 — правила форматирования таблиц РП (bold active, strikethrough done)
- [—] notify-update workflow — рефакторинг: webhook → бот рассылает подписчикам (вместо прямых Telegram API вызовов)
- [—] Memory policy — обновлены лимиты и правила хранения
- [—] MCP серверы — регистрация через `claude mcp add` вместо JSON config (фикс для Claude Code)
- [—] Memory symlink — добавлен в setup.sh + правило workspace root в CLAUDE.md
- [—] Стейлые промпты — удалены дублирующие файлы из roles/strategist/prompts/
- [—] CHANGELOG v0.5.0 — русскоязычный текст, убраны ссылки на Github
- [—] Пути шаблона — исправлены пути для Day Rhythm конфига

## 0.5.0 — записей: 7

- [—] CHANGELOG.md — история изменений шаблона в формате release notes
- [—] update.sh: release notes — при обновлении показывает «Что нового» из CHANGELOG
- [—] update.sh: re-substitution — автоматическая подстановка рабочей директории после обновления
- [—] DATA-POLICY.md — политика данных IWE + подтверждение при установке
- [—] Захардкоженные пути — 14 файлов теперь используют переменную рабочей директории (шаблон работает с любым расположением)
- [—] update.sh — убран хардкод пути, теперь динамическое определение директории
- [—] Рабочая директория по умолчанию — документация теперь рекомендует ~/IWE

## 0.4.0 — записей: 11

- [—] setup.sh встроен в шаблон (ADR-001, АрхГейт 6.4→8.3)
- [—] Модульные роли с `role.yaml` autodiscovery (ADR-002, АрхГейт 8.9)
- [—] Core-режим установки (`--core`) — только git, без сети
- [—] Vendor-agnostic AI CLI — поддержка Codex, Aider, Continue.dev через переменные
- [—] Авто-переименование репо при установке
- [—] Творческий конвейер — 7 категорий заметок, draft-list, guards
- [—] WP-REGISTRY — seed template для отслеживания РП
- [—] Экзоскелет vs протез — принцип #21 в LEARNING-PATH
- [—] setup.sh fallback — явное предупреждение при отсутствии `seed/strategy/`
- [—] Битая ссылка FPF/README.md
- [—] Приватные ссылки убраны из README

## 0.3.0 — записей: 7

- [—] LEARNING-PATH.md — полный путь изучения экзокортекса (T0→T4 + TM/TA/TD)
- [—] update.sh — обновление шаблона из upstream (fetch + merge + reinstall)
- [—] SETUP-GUIDE.md — пошаговое руководство установки
- [—] IWE-HELP.md — быстрый справочник
- [—] АрхГейт (ЭМОГССБ) — 7 характеристик в CLAUDE.md
- [—] SOTA-reference.md — справочник SOTA-практик
- [—] WakaTime — интеграция в стратег-отчёты

## 0.2.0 — записей: 4

- [—] Note-Review — сценарий обзора заметок + детерминированная очистка
- [—] WP Context Files — поддержка inbox/WP-*.md
- [—] CI: validate-template.yml — проверка генеративности на каждый push
- [—] ONTOLOGY.md — терминология платформы

## 0.1.0 — записей: 4

- [—] Начальная структура шаблона экзокортекса
- [—] CLAUDE.md, memory/, roles/ (стратег, экстрактор, синхронизатор)
- [—] Стратег: session-prep, day-plan, strategy-session, week-review
- [—] seed/strategy/ — шаблон DS-strategy
