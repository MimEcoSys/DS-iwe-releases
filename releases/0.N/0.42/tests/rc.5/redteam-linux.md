# Red Team audit — FMT-exocortex-template v0.42.0-rc.5

Decision: safe to publish for the audited scope (Linux, bash); no P0/P1 found. Not GO: macOS/bash 3.2 not run here, CI receipt could not be re-fetched at verdict time (GitHub API rate limit of the unauthenticated test shim).

## Verdict
CAUTION — tag v0.42.0-rc.5 (tag object f50c91fa83a0ac64f99dc0652e8880eb361839a4, peeled 48dd21520fb5321112bd4893faacca73beabb881), audited 2026-11-11T15:40Z–16:15Z, Linux 6.12 (NixOS), GNU bash.

## Required Gates
| Gate | Result | Exact evidence |
|---|---|---|
| Calibration | PASS | tests/run-calibration.sh: 21/21, known-good GO, known-bad BLOCKED_HASH |
| Artifact identity | PASS | local tag == `git ls-remote` (re-checked 16:14Z); manifest version 0.42.0, 877 files; rc channel resolved `кандидат v0.42.0-rc.5 (снимок 48dd21520fb5)` |
| CI receipt | PARTIAL / CANNOT_VERIFY refresh | 15:45Z: 32 check-runs on 48dd2152, all conclusion=success (one duplicate row status in_progress); `upgrade-from-release` (release-candidate.yml) run not linked to this SHA; refresh at verdict blocked by API 403 rate limit |
| Manifest integrity | PASS (deterministic regeneration SKIP) | installed tree vs manifest: 0 mismatches (fresh, upgrade, re-upgrade) |
| Clean install | PASS | clone rc.5 + `SETUP_CI=1 setup.sh --core` rc=0; 877/877 hashes; no `{{…}}` left in .iwe-runtime; template git clean |
| Upgrade v0.41.11 -> rc.5 | PASS | `IWE_UPDATE_CHANNEL=rc update.sh --yes` rc=0; 877/877; all delivered 100755 files +x; 6/6 synthetic sentinels byte-identical incl. user-edited memory/navigation.md |
| Idempotency | PASS | 2nd/3rd run rc=0 "Всё актуально", only timestamps in .iwe-runtime/state change |
| Rollback | PASS | from rc.5: release --yes rc=1, main --yes rc=1, declined prompt rc=0, all 0 files changed; confirmed `ROLLBACK` -> 853/853 v0.41.11 hashes, 0 of 26 0.42-only files left (moved to .backups/deprecated), sentinels intact; re-run no-op; forward again to rc.5 recovers |
| Fault injection | PASS | via curl shim (API mock from real ls-remote data): corrupted payload rc=2, corrupted manifest rc=1, failed download rc=2, corrupted update.sh rejected at step 0 and in manifest check; in all cases only update.sh changed, sentinels intact; rerun recovers to 877/877 |
| Agent safety (destructive-guard) | PASS with P3 gaps | 78 command forms against installed hook; all pre-approved write forms blocked (find -fprint/-fls, git diff/log/show --output, rg --pre, redirect/tee into .claude/hooks|bin|settings, git branch -D, git remote set-url/remove) |
| Negative control | PASS | same 20 hook cases: rc.4 hook ALLOWs branch -D, remote set-url, redirect into hooks/settings; rc.5 BLOCKs. test-wp529-f270-rollback-cleanup FATAL on rc.4, PASS on rc.5; f261 test FAIL(3) on v0.41.11, PASS on rc.5 |
| Platform matrix | CANNOT_VERIFY (macOS) | only Linux/NixOS run here; CI integration-contract-macos jobs green at 15:45Z |
| Containment | PASS | all runs via boundary-guard.sh; 0 blocked service calls recorded; no writes outside fixtures except this session's own harness logs |

## Findings
| ID | Severity | Contract | Evidence | Impact | Owner | Confidence | Falsifier | Executable check / exception | Open issue |
|---|---|---|---|---|---|---|---|---|---|
| RT5-1 | P2 | Self-update: pinned identity + re-exec guard | step 0 `exec bash update.sh "$@"` re-resolves the channel; with API mock alternating rc.5 / "rc.6" (=rc.4 commit) the updater re-executed 401 times in 240 s until killed; also update.sh is replaced before manifest verification, so any later failure leaves new updater + old payload (rc!=0, recoverable by rerun) | runaway loop / API exhaustion under an inconsistent tag view; no data loss | platform | high (reproduced), realism low | no loop if the re-exec'd process receives the resolved SHA (or a depth guard) and a 2nd drift ends with an error | proposed: drift fixture from this audit (alternating matching-refs mock) — not committed | not filed (outward action; needs pilot) |
| RT5-2 | P2 | Install mode honoured by update | `setup.sh --core` skips extractor feeders ("пропущено (core mode)"); first `update.sh --yes` writes extractor-git-diff-feed.{service,timer} and, outside SETUP_CI, runs `systemctl --user enable --now` (scripts/setup-extractor-feeders.sh:290-291); core mode is not persisted | offline/core user gets scheduled jobs they did not opt into | platform | medium (activation not observed — guarded) | false if update.sh reads a persisted core flag and skips backfill | proposed: core-install + update fixture asserting no unit files | not filed |
| RT5-3 | P3 | Defense-in-depth for pre-approved readers | hook allows `cat /dev/null > DS-strategy/current/WeekPlan.md`, `head -c0 /dev/null > params.yaml`, `git remote update --prune`, `git branch --unset-upstream` | user-data truncation without prompt only if the host auto-approves redirections under `Bash(cat:*)` | platform | low (host behaviour not verified) | false if Claude Code prompts for any output redirection | — | not filed |
| RT5-4 | P3 | Truthful diagnostics | release re-run after rollback prints "обновлён слиянием" for settings.json and writes a backup although content is byte-identical, then "Всё актуально" | misleading log line | platform | high | — | — | not filed |
| RT5-5 | P3 | rc channel robustness | rc resolution reads one page of `git/matching-refs/tags/v` and fails closed at >=100 refs (48 now); ~6-7 unauthenticated API calls per run, 60/h limit observed as rc=2 fail-closed | rc channel stops working after ~50 more tags; shared-IP users hit limits | platform / external_dependency | high | — | — | not filed |

None of RT5-1..5 is a regression: RT5-1 and RT5-2 code exists in v0.41.11.

## Release Boundary
- Safe to publish/use: clean install, upgrade from v0.41.11, rollback with explicit ROLLBACK, fail-closed integrity on Linux/bash.
- Not proven: macOS bash 3.2 paths; settings.local.json preservation (sentinel write was refused by this session's own guard hook, not bypassed); CI receipt refresh at verdict time; deterministic manifest regeneration; real service activation.
- Required before re-review: macOS run of the same matrix; issues for RT5-1/RT5-2 filed or explicitly accepted by the product owner.

## Regression Receipt
- fixed candidate: v0.42.0-rc.5 / 48dd2152
- known-bad or mutation control: rc.4 hook and v0.41.11 updater fail the rc.5 checks (above)
- installed projection: setup/update-delivered tree only, 877 files, consumers (hook, updater, runtime build) executed from it
- supported OS/shell matrix: Linux GNU bash only
- second-run/idempotency: PASS
- per-finding executable check or exception decision link: none committed (audit is read-only)
- separate open issue for each unresolved material finding: not created — needs pilot decision
