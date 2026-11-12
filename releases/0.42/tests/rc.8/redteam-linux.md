# Red Team audit — v0.42.0-rc.8

Decision (RU): Публиковать можно с оговоркой — установка, обновление с 0.41.11, повтор, откат и защиты агента прошли; открыт один пункт среднего уровня (P2).

## Verdict
CAUTION — tag v0.42.0-rc.8 (tag object 73a31e086c40, commit b871465497e0a2abfc2ab8f1c9a5b2ef86b90be5), audit 2026-11-12, Linux x86_64 (NixOS), GNU bash 5.2.37.
Scope requested: fresh install, upgrade from v0.41.11, second run, rollback, agent permissions. Supply-chain/attestation review was out of scope.

## Required Gates
| Gate | Result | Exact evidence |
|---|---|---|
| Calibration | PASS | tests/run-calibration.sh: 21/21, known-good GO, known-bad BLOCKED_HASH |
| Artifact identity | PASS | local tag object == remote tag object 73a31e08 -> commit b8714654; update.sh resolved "кандидат v0.42.0-rc.8 (снимок b871465497e0)" |
| Manifest integrity | PASS | 878 files, 0 missing, 0 hash mismatch, 0 duplicates, 0 delivered&deprecated; regenerated twice -> identical sha256 5b672112…; scripts/verify-manifest.sh OK |
| CI receipt (exact SHA) | PASS | public check-runs for b8714654: 33 success, 2 skipped (`cut` = cut-mode only; `integration-contract-macos` umbrella skipped, both matrix legs success). Includes upgrade-from-release, release-receipt, platform-compat |
| Clean install | PASS | disposable fork clone at rc.8, `setup.sh --core` rc 0, `setup.sh --validate` rc 0; repo smoke-test-fresh-install 53/53 |
| Upgrade 0.41.11 -> rc.8 | PASS | `IWE_UPDATE_CHANNEL=rc update.sh --check` verdict "можно ставить"; `--yes` rc 0, 113 files; 878/878 hashes match; 7 synthetic sentinels byte-identical except CLAUDE.md (merged: USER-SPACE kept, §1-§7 identical to fresh install) |
| Second run | PASS | "Всё актуально. Обновлений нет. (878)", 0 template files changed; only .iwe-runtime timestamps (Built/checked_at) rewritten |
| Rollback guard | PASS | release channel (0.41.11) with `--yes`: refused, rc 1, 0 files changed; interactive non-ROLLBACK answer: "Отменено", 0 files changed |
| Confirmed rollback | PASS | ROLLBACK: 853/853 files match v0.41.11, update.sh replaced by 0.41.11, 0 rc-only files left (moved to .backups/deprecated), all 7 sentinels byte-identical incl. CLAUDE.md |
| Recovery forward | PASS | rc channel after rollback: 878/878 match again |
| Agent permissions | PASS | settings.json fresh == upgraded; vs 0.41.11 only +3 allow rules for light-onboarding-state.sh (status/done/reset; script writes only .claude/state markers); 32 hook commands, 0 missing targets |
| Agent-safety suites, manifest-only projection | PASS (1 CANNOT_VERIFY) | 18/19 delivered hook suites pass; guarded_rm_cases needs /usr/bin/rm or /bin/rm (absent on NixOS) |
| Repo update/setup suites | PASS (2 CANNOT_VERIFY) | 67 suites; 10 initial failures all traced to host contamination (see Regression Receipt); after removing them 65 pass; 2 need /usr/bin coreutils (NixOS) |
| Isolation | PASS | real template repo unchanged at b8714654, clean; no ~/.config/systemd/user in real HOME; all service-manager calls intercepted by boundary-guard |
| macOS /bin/bash 3.2 | CANNOT_VERIFY locally | covered only by CI receipt (integration-contract-macos legs success) |

## Findings
| ID | Severity | Contract | Evidence | Impact | Owner | Confidence | Falsifier | Executable check or exception decision link | Open issue if unresolved |
|---|---|---|---|---|---|---|---|---|---|
| RT8-1 | P2 | Update must not add automation the user did not choose (rc.5 RT5-2 fix) | 0.41.11 `setup.sh --core` writes no `.iwe-install-mode`; every rc.8 `update.sh --yes` (incl. a no-op second run) runs the extractor feeders backfill: systemd units written to ~/.config/systemd/user and `systemctl` called (boundary-guard BLOCKED, guard rc 3) | Existing pre-0.42 core users get a headless scheduled LLM job (twice daily) on first 0.42 update; recoverable via `setup-extractor-feeders.sh --uninstall`. Pre-existing in 0.41.11; CHANGELOG says installs without the file behave "как раньше" | platform | high | False if a 0.41.11 --core install updated to rc.8 without SETUP_CI makes no systemctl/crontab call and writes no extractor units | Proposed: fixture = 0.41.11 core install -> rc update with service-manager deny shims, assert zero calls (bad: rc.8 fails; candidate must pass). Or exception accepted by product owner (not the author) | NOT FILED — gh write blocked in this environment; needs an issue |
| RT8-2 | P3 | Agent safe-delete helper portability | `.claude/bin/guarded-rm` hardcodes /usr/bin/rm then /bin/rm; refuses "не найден rm" on NixOS | Fails closed (safe), but agent cannot delete temp files at all on such hosts | platform | high | False if guarded-rm resolves rm on a host without /usr/bin/rm and /bin/rm | none yet | not filed |
| RT8-3 | P3 | Diagnostics | Rollback refusal under --yes prints "ОШИБКА: update.sh прервался на строке 1: exit \"$EXIT_USAGE\"" from the ERR trap after the correct explanation | Misleading "crash" line on intended refusal | platform | high | False if the refusal path prints no ERR-trap line | none | not filed |
| RT8-4 | P3 | Clean rollback state | After confirmed rollback, scripts/artifactor.py and scripts/check-manifest-coverage.py keep +x (shebang rule) while 0.41.11 tree has 100644: fork git shows 2 mode-only modifications | Cosmetic dirty state | platform | high | False if git status is clean after rollback | none | not filed |

Not findings (expected, documented): 3 deprecated files kept because tracked by the fork's git, with printed `git rm` hint; skill SKILL.md placeholders ({{GOVERNANCE_REPO}} etc., 71) identical in 0.41.11 and rc.8; file modes 600/700 from host umask; CLAUDE.md hash change from 3-way merge.

## Release Boundary
- Safe to publish/use: fresh install (--core), rc-channel upgrade from 0.41.11 with user-owned files preserved, idempotent re-run, rollback refusal and confirmed rollback with clean cleanup, forward recovery, agent permission set and hook suites.
- Not proven or blocked: full (non-core) setup path with gh/Claude login; macOS locally; guarded-rm and one scheduler test on hosts without /usr/bin coreutils; GitHub Release object / attestation (rc has no Release by design; not reviewed).
- Required before re-review: decide RT8-1 (fix with executable fixture, or owner-accepted exception with issue link).

## Regression Receipt
- fixed candidate: b871465497e0 (v0.42.0-rc.8)
- known-bad or mutation control: calibration known-bad BLOCKED; rollback refused without ROLLBACK (0 files changed); repo fail-closed suites (hash mismatch, network failure, runtime fail) pass
- installed projection: manifest-only tree, 18/19 agent-safety suites pass
- supported OS/shell matrix: Linux bash 5.2 local; macOS/Windows via CI receipt only
- second-run/idempotency: PASS (0 template changes)
- per-finding executable check or exception decision link: none yet (RT8-1 proposed fixture above)
- separate open issue for each unresolved material finding: RT8-1 needs one — not filed (no GitHub write access here)

Host contamination explained (not product defects): host `gh` shim reports "logged in" so update.sh took the authenticated API path past test curl stubs (5 suites; pass with shim removed from PATH); boundary-guard forces SETUP_CI=1 (scheduler suite passes without it, 24 checks); clone dir named `rc8` breaks iwe_resolve_root's FMT-exocortex-template layout marker (smoke passes 53/53 in a correctly named clone); PyYAML absent (fork-guard suite passes in a disposable venv).
