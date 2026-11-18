#!/run/current-system/sw/bin/bash
# Runs the candidate's own test suites in a clean clone as the disposable user; one log per suite.
# Usage: suites-rc12.sh <clone-dir> <log-dir>
SRC=${1:?clone dir}; L=${2:?log dir}
cd "$SRC" || exit 1
run(){ local name=$1; shift; local s=$(date +%s); "$@" > "$L/$name.log" 2>&1; local rc=$?
  echo "rc=$rc secs=$(( $(date +%s)-s ))" >> "$L/$name.log"; printf '%-34s код %s\n' "$name" "$rc"; }
run legacy-template-base   bash setup/test-update-legacy-template-base.sh
run rc-channel             bash setup/test-update-rc-channel.sh
run issue-226              bash setup/test-update-issue-226.sh
run check-verdict          bash setup/test-update-check-verdict.sh
run guarded-rm-cases       python3 .claude/hooks/tests/destructive-guard/guarded_rm_cases.py
run find-chain             bash .claude/hooks/tests/test-destructive-guard-find-chain.sh
run hook-cases             python3 .claude/hooks/tests/destructive-guard/hook_cases.py
