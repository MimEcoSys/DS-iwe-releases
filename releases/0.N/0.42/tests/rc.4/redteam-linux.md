# Red Team audit — v0.42.0-rc.4

## Verdict
CAUTION — tag v0.42.0-rc.4 (annotated a639f260 → commit 5f1277bea5c639bc571126651aa0b8abe27b9ceb), audit 2026-11-11T12:14Z–13:09Z, Linux only (NixOS container, bash). Remote tag re-checked at 13:09Z: unchanged, no newer rc.

No P0/P1 found. All findings below are pre-existing in v0.41.11 (not regressions) and are P2/P3 defense-in-depth or test-infrastructure gaps.

## Required Gates
| Gate | Result | Exact evidence |
|---|---|---|
| Calibration | PASS | tests/run-calibration.sh: 21/21, guard + integrity contract |
| Artifact identity | PASS | tag→5f1277be; 18/18 check-runs success on head_sha 5f1277be; manifest 0.42.0, 875 files, sha256 4bac02f4… |
| Manifest integrity | PASS | generate-manifest.sh twice → identical, equals committed; verify-manifest.sh OK |
| Clean install | PASS | setup.sh (SETUP_CI) rc0; setup.sh --validate ALL CHECKS PASSED; 875/875 hashes |
| Upgrade 0.41.11→rc.4 | PASS | rc channel pinned 5f1277be in preview and apply; 875/875 hashes; workspace .claude/* identical to fresh install; 7/7 sentinels byte-identical; user-edited memory/protocol-work.md kept with diagnostic |
| Idempotency | PASS | second run: "Всё актуально", only .iwe-runtime/state timestamps change |
| Rollback guard | PASS | release/main channel --yes → rc1, unchanged; interactive "no" → unchanged; "ROLLBACK" → 0.41.11 (converges on 2nd run, see F4); forward again → 875/875 |
| Failure injection | PASS | corrupted payload (2 files, parallel+retry paths) → sha256 mismatch, "Обновление остановлено", rc2, manifest stays 0.41.11, only update.sh self-updated; recovery run → 875/875, sentinels kept |
| Installed projection | PASS | manifest-only tree: 17 delivered hook test suites + hook_cases.py 475/475 |
| Negative control | PASS | v0.41.11 destructive-guard against rc.4 tests: find-delete 33 FAIL, file-writers 9 FAIL |
| Agent safety | PARTIAL | see F1, F2 (pre-existing) |
| Platform matrix | CANNOT_VERIFY locally | macOS/bash 3.2, Windows only via CI job names (green), not reproduced |
| Scheduler activation | CANNOT_VERIFY | blocked by design in disposable run (no manager calls recorded) |

## Findings
| ID | Severity | Contract | Evidence | Impact | Owner | Confidence | Falsifier | Executable check / exception | Open issue |
|---|---|---|---|---|---|---|---|---|---|
| F1 | P2 | secret-leak-block: sensitive file not read via Bash | hook allows `cat .e*`, `printenv GITHUB_TOKEN`, `git show HEAD:.env`, `cp .env x`, python open(); `Bash(cat:*)` is pre-approved | secret value can reach model context without prompt | platform | medium (harness glob handling not verified) | Claude Code prompts on `cat .e*` despite `Bash(cat:*)` | none yet — proposed: add cases to test-secret-leak-block-*.sh | not created (needs pilot approval; gh shim forbids) |
| F2 | P2 | pre-approved commands must not mutate state (RT2-3 class) | `Bash(git branch:*)`, `Bash(git remote:*)` pre-approved; hook allows `git branch -D/-f`, `git remote set-url/remove/add` | branch deletion/redirect of origin without prompt; recoverable via reflog | platform | high (hook) / medium (impact) | hook denies these forms | none yet — proposed: file-writers-style test | not created |
| F3 | P2 | CI upgrade-test proves upgrade | job takes 2nd manifest commit (2c74befa, rc-internal) as "previous", never runs update.sh, tolerates prev smoke failure | 0.41.11→rc path not CI-gated (only this manual run) | test_infrastructure | high | job runs update.sh from last published tag | none yet | not created |
| F4 | P3 | rollback is one transaction | confirmed ROLLBACK leaves rc.4 update.sh with 0.41.11 manifest, says "Обновление завершено"; 24 0.42-only files remain | mixed updater until next run; inert orphans | platform | high | — | none | not created |

Pre-existing in v0.41.11: F1, F2 confirmed by same probes on a 0.41.11 install.

## Release Boundary
- Safe to publish/use: install, upgrade 0.41.11→rc.4, rollback guard, payload integrity, user data preservation on Linux.
- Not proven: macOS/Windows behaviour (CI only), scheduler activation, harness-level permission handling of globs.
- Required before re-review: issues for F1–F3 (or accepted exceptions by a release approver).

## Regression Receipt
- fixed candidate: 5f1277be
- known-bad/mutation: old destructive-guard fails 42 new cases; corrupted payload refused
- installed projection: PASS
- OS/shell: Linux bash only
- second-run: PASS
- per-finding check/exception: none yet
- open issues: none created (outward action needs pilot approval)

Note on test infrastructure: first injection attempt (argv-matching curl shim) never fired because update.sh downloads via `curl --parallel -K cfg`; it was discarded, not counted as evidence.
