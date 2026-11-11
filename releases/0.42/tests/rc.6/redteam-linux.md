# Red Team audit — FMT-exocortex-template v0.42.0-rc.6

Decision: **do not publish** — the release's headline agent-safety claim is bypassable through the pre-allowed `find`, and the CI gate that should prove the release→candidate upgrade never ran for this candidate.

## Verdict
BLOCKED — tag `v0.42.0-rc.6` (tag object 59aef139a6aff24ebdbdb33ee987a30388aabaa3 → commit 557ecb21bbf388d7ae4a60a7b09c18f6a4d52225), audit 2026-11-11 18:02–18:20 UTC, host Linux NixOS, GNU bash 5.2.37, python3 without PyYAML.

Calibration (`tests/run-calibration.sh`): 21/21 PASS (guard containment + integrity contract GO/BLOCKED_HASH).

## Required Gates
| Gate | Result | Exact evidence |
|---|---|---|
| Artifact identity | PASS | tag→557ecb21 identical locally and on remote; manifest version 0.42.0, 877 files, sha256(update-manifest.json)=9009d0cb…77080; tagger github-actions[bot]; no GitHub Release object (404) — consistent with prior RCs (tags only) |
| CI receipt on exact SHA | PARTIAL | 32 check-runs on 557ecb21: 31 success, 1 `integration-contract-macos` skipped (matrix parent; both macOS legs success). Release Candidate run 43068628486 has jobs `next-rc`, `cut` only — **no `upgrade-from-release`** (F2) |
| Clean install | PASS | `setup.sh --core`: 877/877 files match manifest, 0 NOEXEC, 0 unresolved placeholders, `.iwe-install-mode`=core, `--validate` passes; full `setup.sh` under SETUP_CI=1 rc=0 (gh repo create refused by test shim) |
| Service/scheduler activation | CANNOT_VERIFY | guard denies systemctl/crontab by design; no service-manager call attempted |
| Upgrade 0.41.11 → rc.6 (real `IWE_UPDATE_CHANNEL=rc update.sh`) | PASS | `--check` verdict «можно ставить»; `--yes` rc=0, delivered from `v0.42.0-rc.6 (557ecb21bbf3)`; 877 files: 0 MISSING / 0 NOEXEC / 1 DIFFERS (CLAUDE.md, expected USER-SPACE merge); extensions/params.yaml/settings.local.json sentinels byte-identical; USER-SPACE line kept; governance sentinel kept; 2nd run «Всё актуально» rc=0 |
| Rollback rc.6 → 0.41.11 (release channel) | PASS | `--yes` refused rc=1, 0 files changed; cancel rc=0, 0 changed; `ROLLBACK`: 853/853 match 0.41.11, 26/26 0.42-only paths gone, 37 files moved to `.backups/deprecated/…` and listed; 3rd run no-op. Edited-0.42-only-file case: developer test `test-wp529-f270-rollback-cleanup.sh` PASS (source tree, not e2e) |
| Installed projection (manifest-only) | PASS* | 18/18 delivered hook test scripts rc=0; hook_cases 475/475; long_cases 17/17; guarded_rm_cases 25/37 — all 12 failures caused by host rm location (37/37 with host rm path), F4 |
| Agent safety (destructive-guard claims of 0.42) | **FAIL** | F1: 8 find-chain forms allowed and executed (deletion, guard overwrite) |
| Platform matrix | PARTIAL | Linux/NixOS bash 5.2 only; macOS bash 3.2 / Windows — CANNOT_VERIFY here (CI legs green) |
| Negative control | PARTIAL | calibration known-bad BLOCKED; F1 detector fails on rc.6; upgrade negative control on rc.3 not run (API quota: 60/h unauthenticated) — SKIP |
| Supply chain / provenance | SKIP | not audited in depth; attestation job is "diagnostic" only |

## Findings
| ID | Severity | Contract | Evidence | Impact | Owner | Confidence | Falsifier | Executable check | Open issue |
|---|---|---|---|---|---|---|---|---|---|
| F1 | P1 | 0.42 notes: agent cannot, without the user, delete via `find`, write via `find -fprint`, run anything but reading via `find -exec`, overwrite guard files | Delivered hook ALLOWs `find . -name v -exec grep -l foo {} \; -delete`, `… -exec cat {} \; -delete`, `… -execdir cat {} \; -exec rm {} \;`, `… -exec cat {} \; -exec rm -f {} \;`, `… -exec wc -l {} \; -exec sh -c 'rm "$0"' {} \;`, `… -exec head -1 {} \; -execdir rm {} +`, `… -exec cat {} \; -fprint out.txt`; executed in fixture: victim deleted / file written. `find .claude/hooks -name destructive-guard.sh -exec cat {} \; -fprint .claude/hooks/destructive-guard.sh` ALLOW → guard copy 73426 B → 35 B. `Bash(find:*)` is in delivered `permissions.allow`. `+`-terminated reader and reader-after-delete are blocked → parser stops after first `\;`-terminated read-only action | agent deletes/overwrites any file (incl. the guard) with no prompt; headline security claim false | platform | high (hook decision + effect); medium for end-to-end auto-run inside Claude Code (no live agent session tested) | false if the delivered hook returns 2 for these commands, or Claude Code prompts for them despite `Bash(find:*)` | `bin/find_bypass.py` + `bin/guardfile.py` (fail on rc.6; same forms allowed on 0.41.11 — pre-existing gap the release claims to close) | not created: test env gh shim forbids `issue create` — draft below |
| F2 | P2 (blocking gate) | CHANGELOG [ci]: `upgrade-from-release` runs right after each rc tag; "a failure means the candidate must not go to testers" | job exists only on `release/v0.42.0` (557ecb21) — absent on main 637e06a1; workflow_dispatch uses main's definition; run 43068628486 (rc.6 tagging) jobs: `next-rc`, `cut` | required upgrade gate silently never runs for rc.5/rc.6; receipt looks green | test_infrastructure | high | false if any run of `upgrade-from-release` exists for rc.6 | check: run jobs list must contain `upgrade-from-release`; mitigated: manual real upgrade in this audit PASS | draft below |
| F3 | P2 | update output: «если в клоне шаблона была ваша правка, она в прежней версии; прежняя версия: <.backups/memory-pre-update/…>» | edited `FMT-exocortex-template/memory/navigation.md` (random sentinel) before upgrade; after: sentinel absent everywhere in fixture, incl. the named backup (backs up the deployed copy, not the clone) | user edit irrecoverably lost while the tool claims it is backed up; editing the clone is discouraged by docs, so the loss itself is by design, the diagnostic is false | platform | high | false if the sentinel is found in any backup path | sentinel grep after upgrade (harness `upgrade`) | draft below; pre-existing (#965/#967), not rc-specific |
| F4 | P3 | safe deletion `.claude/bin/guarded-rm` usable on Linux | `REAL_RM=/usr/bin/rm`, fallback `/bin/rm`; on NixOS neither exists → refuses everything (fail-closed). 37/37 with host path | safe-delete path unusable on NixOS; no safety bypass | platform | high | false if guarded-rm finds rm via a trusted resolver | `guarded_rm_cases.py` on NixOS | pre-existing (0.41.11 same); NixOS not declared supported |
| F5 | P3 | rerun is a clean no-op | 2nd `setup.sh --core` changes `.iwe-runtime/.build-hash`; "Всё актуально" update rerun rewrites 16 `.iwe-runtime` state files | noise only | platform | high | false if build-hash is deterministic | snapshot diff in harness | — |

Not findings: `sed -i`, `cp`, `mv`, `git config remote.origin.url`, `git update-ref -d`, `git format-patch -o`, `git -c core.pager=…` pass the hook but are not pre-allowed → user prompt (documented limitation "hook sees only text").

## Release Boundary
- Safe to publish/use: install (`--core`), upgrade 0.41.11→rc.6, rollback with ROLLBACK and `--yes` refusal — all proven end-to-end on Linux.
- Not proven or blocked: destructive-guard claims for `find` (F1); CI upgrade gate (F2); macOS/Windows; service activation.
- Required before re-review: fix F1 (evaluate every action of a find expression, not only up to the first `\;`-terminated reader; include `-fprint*`/`-fls` after readers); add F1 forms to `hook_cases.py`; make `upgrade-from-release` run from main's workflow (merge it to main or dispatch on the release ref) and show its run for the new rc; cut rc.7 and re-run this audit.

## Regression Receipt
- fixed candidate: none yet (rc.6 audited)
- known-bad or mutation control: calibration known-bad BLOCKED; F1 detector reproduces on rc.6 and 0.41.11
- installed projection: manifest-only tree, 877 files; hook suites as above
- supported OS/shell matrix: Linux NixOS / bash 5.2 only
- second-run/idempotency: update no-op PASS (state files rewritten, F5)
- per-finding executable check: scratchpad `bin/find_bypass.py`, `bin/guardfile.py`, `bin/h.sh` (fresh/upgrade/rollback)
- separate open issue for each unresolved material finding: **not created** — test environment's gh shim blocks GitHub writes; drafts below must be filed by the pilot

## Issue drafts
1. **destructive-guard: find chain after a read-only `-exec … \;` bypasses the 0.42 find rules** — repro: pipe `{"tool_input":{"command":"find . -name v -exec cat {} \\; -delete"}}` into `.claude/hooks/destructive-guard.sh` → exit 0; same for `-exec rm`, `-execdir rm`, `-fprint <guard file>`. `Bash(find:*)` pre-allowed ⇒ no prompt. Blocks v0.42.0.
2. **release-candidate.yml: upgrade-from-release never runs** — job defined only on release branch; dispatch from main runs main's file (run 43068628486 has no such job).
3. **update.sh memory policy: false "your edit is in the previous version" message for template-clone edits** — backup holds the deployed copy only.
4. **guarded-rm: hardcoded /usr/bin/rm,/bin/rm fails on NixOS** (fail-closed).
