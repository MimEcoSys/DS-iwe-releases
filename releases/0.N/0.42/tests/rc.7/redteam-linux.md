# Red Team audit — FMT-exocortex-template v0.42.0-rc.7

Decision: **publishing is safe** (no blocker); two low-severity findings remain open, and no issues have been filed yet.

## Verdict
CAUTION — tag `v0.42.0-rc.7` (tag object `511176189dcd`, peeled `91f18cec3855dfa494df4798fe0ddc5f619b9239`), audit 2026-11-11T19:20Z–19:51Z.
Host: Linux 6.12 (NixOS), bash, python3 3.12 **without PyYAML**. Fixtures: `/tmp/iwe-rt-rc7.3srC7n/*`, every dangerous command run through `boundary-guard.sh --`.

## Required Gates
| Gate | Result | Exact evidence |
|---|---|---|
| Calibration (`tests/run-calibration.sh`) | PASS | 21/21, known-good GO, known-bad BLOCKED_HASH |
| Release identity | PASS | local tag == remote tag (ls-remote, refreshed 19:51Z); no rc.8; PR #1524 head == 91f18cec; origin/main 637e06a1 is an ancestor, so PR merge tree == candidate tree |
| CI on exact SHA | PASS | 35 check-runs on 91f18cec: all success except `cut` (RC workflow, expected skip) and `integration-contract-macos` (skipped in workflow_dispatch run 43083288867); macOS matrix (both gov repos) green in PR run 43083122194 on an identical tree |
| Manifest | PASS | v0.42.0, 878 files; regenerated twice in a clean clone → byte-identical, no diff to committed; delivered ∩ deprecated = ∅ |
| Fresh install (setup.sh, SETUP_CI) | PASS | rc=0, `setup.sh --validate` ALL CHECKS PASSED, 878/878 template hashes match manifest, 0 service-manager calls |
| Upgrade v0.41.11 → rc.7 (rc channel, --yes) | PASS | rc=0, step0 self-update + re-exec pinned to 91f18cec, 112 files, 878/878 hashes, incomplete-marker cleared; 7 user sentinels + USER-SPACE byte-identical; user-edited memory file kept with diagnostic; workspace .claude/memory/runtime == fresh install (only timestamps/abs paths differ) |
| Second run | PASS | "Всё актуально", only `.iwe-runtime/.build-hash` `Built:` timestamp changes (hash line identical) |
| Rollback guard | PASS | release & main channel with --yes → exit 1, 0 files changed; wrong answer `rollback` → "Отменено", 0 changes; stdin EOF → refuse |
| Confirmed ROLLBACK → 0.41.11 | PASS | 0 mismatches vs 0.41.11 manifest, 0 rc-only files left in template (moved to `.backups/deprecated/`), updater == 0.41.11, sentinels intact, no settings.json hook points to a missing file |
| Re-upgrade after rollback | PASS | rc=0, 878/878 hashes, sentinels intact |
| Network failure | PASS | rc/release channel with dead proxy → exit 1 "Не удалось загрузить манифест", 0 files changed, no marker |
| Agent guard: pre-approved writers | PASS | git log/show/diff `--output`, find `-fprint/-fprintf/-fls/-fprint0/-exec/-execdir/-okdir`, `rg --pre`, redirect/tee into hooks/settings → all blocked |
| Agent guard: direct + shell indirection | PASS | rm -rf, git add -A/., push -f, reset --hard, clean, gh repo delete, bash -c/sh -c/eval, quoting, `\rm`, command/env/xargs, chains/subshells/groups, self-set CC_ALLOW_DESTRUCTIVE_INPUT → blocked |
| Shipped regression suite on this host | PASS* | 27 tests; 25 green directly, exec-bit green in a git clone (406 paths), rc-channel 10/10 once the authenticated test-env `gh` shim is off PATH (see F3) |
| Mutation controls | PASS | find-chain test: rc.7 20/0, rc.6 guard 8/12 FAIL; file-writers: rc.7 14/0, rc.2 guard 5/9 FAIL; step0-no-downgrade (rc.1), rollback-cleanup (rc.4), clone-memory-backup (rc.6) → FATAL on old updater, PASS on rc.7 |

## Findings
| ID | Severity | Contract | Evidence | Impact | Owner | Confidence | Falsifier | Executable check | Open issue |
|---|---|---|---|---|---|---|---|---|---|
| F1 | P3 low | agent permissions | rc.7 adds `Bash(bash .claude/scripts/light-onboarding-state.sh status:*)`, `… done`, `… reset` to the allow list: **cwd-relative** path. Script resolves workspace as `$IWE_WORKSPACE`/`$CLAUDE_PROJECT_DIR`/`$PWD`; in the Bash tool `CLAUDE_PROJECT_DIR` is unset. Probe: from `DS-strategy/` status prints `active` while the root prints `inactive`. After ROLLBACK the 3 allow rules stay although the script is gone (additive merge) | a file with that name in any sub-repo (third-party Pack/FPF clone) runs without approval via `(cd X && bash .claude/scripts/…)`; `done` from a sub-dir marks the wrong workspace | platform | medium | Claude Code resolving allow-rule paths against the project root, or refusing compound `cd` | proposed: anchored path or script self-check `[ "$0" -ef "$WS/.claude/scripts/…" ]` + test from sub-dir | not filed (needs pilot OK) |
| F2 | P3 low | rollback cleanliness | after confirmed ROLLBACK: empty dirs `.claude/skills/find-method`, `.claude/skills/onboarding`, `.claude/lib/locale`; `DS-strategy/scripts/executor-catalog.yaml` lists them as `no-SKILL.md` | cosmetic; re-upgrade fixes it | platform | high | — | proposed: assert no empty rc-only dirs in test-wp529-f270-rollback-cleanup.sh | not filed |
| F3 | P3 low | test hermeticity | `setup/test-update-rc-channel.sh` "failed commit lookup" FAILs when an authenticated `gh` is on PATH (update.sh prefers gh over the stubbed curl); passes 10/10 without it | false-red on author machines with `gh auth login`; product behavior still fail-closed | test_infrastructure | high | — | proposed: test prepends a deny `gh` stub | not filed |

Not findings (by documented design): hook does not catch non-allow-listed `python -c shutil.rmtree`, `base64 | sh`, `$(printf rm)`, cp/truncate/chmod/sed -i on hooks, `git restore .`, `git checkout -- .`, `git update-ref -d`, `git commit --no-verify` — these need user approval; CLAUDE.md states the hook is accident protection, not a security boundary. In bypass-permissions mode these are unguarded.
Memory files keep `{{GOVERNANCE_REPO}}`-style placeholders on purpose (navigation.md says "подставьте значение").
Deprecated files tracked by the template's own git (3) stay after upgrade — documented.

## Release Boundary
- Safe to publish/use: fresh install, v0.41.11→rc.7 upgrade, repeat run, rollback guard + confirmed rollback, re-upgrade, network-failure handling, destructive guard on pre-approved commands — on Linux.
- Not proven here: macOS Bash 3.2 and Windows (CI only); upgrades from versions older than 0.41.11; service activation (systemd/launchd is denied by the guard on purpose); server-side mix-and-match / moving-tag race (unit tests only); parallel downloads under partial failure; `releases/latest` was re-checked at 19:44Z (later refresh hit the API rate limit).
- Required before re-review: none blocking; F1–F3 trackers.

## Regression Receipt
- fixed candidate: 91f18cec (rc.7)
- known-bad or mutation control: rc.6/rc.2 guard, rc.1/rc.4/rc.6 updater (see gates)
- installed projection: fresh2 and up2 workspaces, 878/878 manifest hashes
- supported OS/shell matrix: Linux/NixOS bash here; macOS/Windows via CI on an identical tree
- second-run/idempotency: clean no-op except build timestamp
- per-finding executable check: proposed, not written (audit-only task)
- separate open issue for each unresolved material finding: not filed — waiting for pilot approval

## Containment notes
- No writes from fixtures to the real workspace. `gh-calls.log`, `secret-leak-block.jsonl` and `repo-pulled-*.txt` come from the auditor's own tool hooks and the harness.
- Guard keeps inherited PATH → setup (CI mode) called host `gh repo create smoke-test/DS-strategy` (the test-env shim refused it); update.sh used the host `gh` for API calls. A test-infra limitation of the guard, not a product issue.
- At the start, onboarding in the real workspace was marked passed (`light-onboarding-state.sh done`), as CLAUDE.md requires when a person asks for work in the environment.
