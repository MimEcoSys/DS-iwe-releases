# Candidate's own test suites in a clean clone of the tag, as iwe-test (macOS).
. /private/tmp/iwe-rc13-probes/env.sh
L="$W/logs/suites"; mkdir -p "$L"; SRC="$W/src"; cd "$SRC" && git checkout -q "$RC" && [ "$(git rev-parse HEAD^{tree})" = 29bfeab0a737ea6b0e0ce73c5f95e5c282e3d657 ] || { echo "дерево не то"; exit 1; }
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin"   # tests run without the gh stub
run(){ local name=$1; shift; local s=$(date +%s); "$@" > "$L/$name.log" 2>&1 </dev/null; local rc=$?
  echo "rc=$rc secs=$(( $(date +%s)-s ))" >> "$L/$name.log"; printf '%-34s код %s  (%s с)  %s\n' "$name" "$rc" "$(( $(date +%s)-s ))" "$(grep -E 'PASS|FAIL|из .* как ожидалось|passed|failed' "$L/$name.log" | tail -1 | cut -c1-90)"; }
run legacy-template-base   bash setup/test-update-legacy-template-base.sh
run rc-channel             bash setup/test-update-rc-channel.sh
run issue-226              bash setup/test-update-issue-226.sh
run check-verdict          bash setup/test-update-check-verdict.sh
run issue-1143-roles       bash setup/test-update-issue-1143.sh
run core-mode-feeders      bash scripts/tests/test-wp529-f270-core-mode-feeders.sh
run exec-bit               bash scripts/tests/test-wp529-f270-exec-bit.sh
run rollback-cleanup       bash scripts/tests/test-wp529-f270-rollback-cleanup.sh
run rollback-by-version    bash scripts/tests/test-wp529-f261-rollback-by-installed-version.sh
run step0-no-downgrade     bash scripts/tests/test-wp529-f270-step0-no-downgrade.sh
run guarded-rm-cases       python3 .claude/hooks/tests/destructive-guard/guarded_rm_cases.py
run find-chain             bash .claude/hooks/tests/test-destructive-guard-find-chain.sh
run hook-cases             python3 .claude/hooks/tests/destructive-guard/hook_cases.py
