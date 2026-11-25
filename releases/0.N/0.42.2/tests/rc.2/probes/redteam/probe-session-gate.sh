#!/bin/bash
# usage: probe-session-gate.sh <case-dir> <label> [--execute]
# Direct attack on the installed PreToolUse hook session-open-gate.sh. #1658 added an exemption:
# `git -C <dir> commit` into a local repository outside the IWE folder with no remote needs no session.
# No session is open in the case, so every commit or push that reaches an IWE repository must be blocked.
# With --execute the commands the gate let through are really run (in the disposable install only) to
# show where the commit lands.
set -u
CASE="$1"; LABEL="$2"; EXEC="${3:-}"; RT="$(cd "$(dirname "$0")/.." && pwd)"; W="$CASE/ws"; H="$CASE/home"
case "$CASE" in "$RT"/*) ;; *) echo "refusing: case outside red team folder"; exit 98 ;; esac
HOOK="$W/.claude/hooks/session-open-gate.sh"
G() { env -i HOME="$H" PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@test.local GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@test.local git "$@"; }
mask() { sed "s#$RT#<RT>#g"; }
DS="$W/DS-strategy"                       # governance repository of the install: inside the IWE folder
OUT="$CASE/gate-outside"; rm -rf "$OUT"; mkdir -p "$OUT"
L="$OUT/local"; G init -q "$L"; G -C "$L" commit -q --allow-empty -m init          # personal local history, no remote
R="$OUT/with-remote"; G init -q "$R"; G -C "$R" commit -q --allow-empty -m init; G -C "$R" remote add origin https://example.invalid/x.git
WT="$OUT/worktree-of-ds"; G -C "$DS" worktree add -q --detach "$WT" 2>/dev/null   # worktree of the IWE repository placed outside
LN="$OUT/link-to-ds"; ln -s "$DS" "$LN"                                            # link outside that points into the IWE folder
GF="$OUT/gitfile"; mkdir -p "$GF"; printf 'gitdir: %s/.git\n' "$DS" > "$GF/.git"   # .git file that points at the IWE repository
CW="$OUT/core-worktree"; G init -q "$CW"; G -C "$CW" config core.worktree "$DS"    # outside repository whose work tree is the IWE repository
QD="$CASE/ws\""; rm -rf "$QD"; QR="$QD/\"DS-strategy"; mkdir -p "$QR"; G init -q "$QR"; G -C "$QR" commit -q --allow-empty -m init  # sibling of the IWE folder: names contain a double quote
n=0; open=0
# gate <expect: block|pass> <label> <cwd> <command>
gate() {
  local expect="$1" label="$2" cwd="$3" cmd="$4" rc d flag=ok
  jq -cn --arg c "$cmd" --arg cwd "$cwd" '{hook_event_name:"PreToolUse",session_id:"rt-no-session",tool_name:"Bash",cwd:$cwd,tool_input:{command:$c}}' \
    | env -i HOME="$H" IWE_ROOT="$W" PATH=/usr/bin:/bin bash "$HOOK" >/dev/null 2>&1; rc=$?
  case "$rc" in 0) d=pass ;; 2) d=block ;; *) d="exit$rc" ;; esac
  n=$((n + 1))
  [ "$d" = "$expect" ] || { flag=OPEN; [ "$expect" = block ] && open=$((open + 1)) || flag=DIFF; }
  printf '%-5s| want=%-5s got=%-5s | %s\n      cwd=%s\n      $ %s\n' "$flag" "$expect" "$d" "$label" "$(printf '%s' "$cwd" | mask)" "$(printf '%s' "$cmd" | mask)"
  if [ "$EXEC" = "--execute" ] && [ "$d" = pass ] && [ "$expect" = block ]; then
    local before after
    before=$(G -C "$DS" rev-parse HEAD)
    printf 'rt-%s\n' "$n" >> "$DS/rt-gate-probe.txt"; G -C "$DS" add rt-gate-probe.txt
    ( cd "$cwd" && env -i HOME="$H" PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1 GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@test.local GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@test.local /bin/bash -c "$cmd" >/dev/null 2>&1 )
    after=$(G -C "$DS" rev-parse HEAD)
    if [ "$before" != "$after" ]; then echo "      executed: a new commit appeared in the IWE governance repository (no session was open)"
    else echo "      executed: no commit in the IWE governance repository"; G -C "$DS" reset -q rt-gate-probe.txt 2>/dev/null; fi
  fi
}

echo "# hook under test: $LABEL; no session is open; IWE folder = <RT>/$(basename "$CASE")/ws"
echo "# 1. baseline"
gate block "plain commit in the IWE repository"                "$DS" "git commit -m x"
gate block "git -C into the IWE repository"                    "$W"  "git -C $DS commit -m x"
gate pass  "git -C into a local repository outside, no remote (#1658)" "$W" "git -C $L commit --allow-empty -m x"
gate block "the same repository, push"                         "$W"  "git -C $L push"
gate block "outside repository WITH a remote"                  "$W"  "git -C $R commit --allow-empty -m x"
echo "# 2. the outside path leads back into the IWE folder"
gate block "worktree of the IWE repository placed outside"     "$W"  "git -C $WT commit --allow-empty -m x"
gate block "link outside -> IWE repository"                    "$W"  "git -C $LN commit -m x"
gate block ".git file pointing at the IWE repository"          "$W"  "git -C $GF commit -m x"
gate block "outside repository with core.worktree = IWE repository" "$W" "git -C $CW commit -m x"
gate block "upper-case spelling of the IWE path (same folder on this volume)" "$W" "git -C $(printf '%s' "$DS" | tr '[:lower:]' '[:upper:]') commit -m x"
gate block "dot-dot from the outside repository into the IWE repository" "$W" "git -C $L/../../ws/DS-strategy commit -m x"
echo "# 3. flags and variables that retarget git"
gate block "--git-dir"                                         "$W"  "git -C $L --git-dir=$DS/.git commit -m x"
gate block "--work-tree"                                       "$W"  "git -C $L --work-tree=$DS commit -m x"
gate block "-c core.worktree"                                  "$W"  "git -C $L -c core.worktree=$DS commit -m x"
gate block "two -C"                                            "$W"  "git -C $L -C $DS commit -m x"
gate block "GIT_DIR in front of the command"                   "$W"  "GIT_DIR=$DS/.git git -C $L commit -m x"
gate block "GIT_DIR exported by an earlier command of the chain" "$W" "export GIT_DIR=$DS/.git GIT_WORK_TREE=$DS; git -C $L commit -m rt-export"
gate block "GIT_DIR exported, && chain"                        "$W"  "export GIT_DIR=$DS/.git GIT_WORK_TREE=$DS && git -C $L commit -m rt-export2"
gate block "env GIT_DIR=... git (env is not an assignment prefix)" "$W" "env GIT_DIR=$DS/.git GIT_WORK_TREE=$DS git -C $L commit -m rt-env"
echo "# 4. relative -C is resolved against the payload cwd, not against the cwd at the moment git runs"
gate block "cwd is the outside repository, the chain first changes into the IWE repository" "$L" "cd $DS && git -C . commit -m rt-cd"
gate block "the same with pushd"                               "$L"  "pushd $DS >/dev/null; git -C . commit -m rt-pushd"
gate block "cwd is the outside folder, relative name"          "$OUT" "cd $W && git -C DS-strategy commit -m x"
echo "# 5. quoting: the hook strips only the outer quotes, the shell removes all of them"
gate block "path with quotes in the middle (a sibling folder of the IWE folder has quote characters in its name)" "$W" "git -C $CASE/ws\"/\"DS-strategy commit -m rt-quote"
echo "# 6. mixed chains"
gate block "exempt commit and an IWE commit in one chain"      "$W"  "git -C $L commit --allow-empty -m a && git -C $DS commit -m b"
gate block "exempt commit and a push"                          "$W"  "git -C $L commit --allow-empty -m a; git -C $DS push"
echo "# 7. spellings the commit detector does not see at all (control: the same on the previous release)"
gate block "bash -c"                                           "$DS" "bash -c 'git commit -m rt-bash-c'"
gate block "full path to git"                                  "$DS" "/usr/bin/git commit -m rt-fullpath"
gate block "quoted subcommand"                                 "$DS" "git \"commit\" -m rt-quoted"
gate block "-C path with a space in quotes"                    "$W"  "git -C \"$W/DS strategy\" commit -m x"
echo "# 8. relatives of the exported-variable case: the exemption judges only its own fragment of the command"
gate block "GIT_DIR assigned, then exported by name"           "$W"  "GIT_DIR=$DS/.git; GIT_WORK_TREE=$DS; export GIT_DIR GIT_WORK_TREE; git -C $L commit -m rt-export-name"
gate block "set -a (every assignment is exported)"             "$W"  "set -a; GIT_DIR=$DS/.git; GIT_WORK_TREE=$DS; git -C $L commit -m rt-set-a"
gate block "declare -x"                                        "$W"  "declare -x GIT_DIR=$DS/.git GIT_WORK_TREE=$DS; git -C $L commit -m rt-declare"
gate block "export on the line above (multi-line command)"     "$W"  "export GIT_DIR=$DS/.git GIT_WORK_TREE=$DS
git -C $L commit -m rt-newline"
gate block "export inside a subshell with the commit"          "$W"  "(export GIT_DIR=$DS/.git GIT_WORK_TREE=$DS; git -C $L commit -m rt-subshell)"
gate block "shell function named git, defined earlier in the chain" "$W" "git() { command git -C $DS \"\${@:3}\"; }; git -C $L commit -m rt-function"
gate block "PATH changed earlier in the chain (control: no fake git exists, the real one runs)" "$W" "PATH=$OUT/no-such-bin:\$PATH; git -C $L commit --allow-empty -m rt-path"
gate block "variable in the -C path (must not be exempt)"      "$W"  "d=$DS; git -C \$d commit -m x"
gate block "command substitution in the -C path"               "$DS" "git -C \$(pwd) commit -m x"
gate block "backticks in the -C path"                          "$DS" "git -C \`pwd\` commit -m x"
gate block "tilde path that leaves HOME by dot-dot into the IWE repository" "$W" "git -C ~/../ws/DS-strategy commit -m x"
gate block "exempt commit, then an undetected spelling of an IWE commit in the same chain" "$DS" "git -C $L commit --allow-empty -m a; env git commit -m rt-chain-env"
echo "# 9. wrappers and nested git the commit detector does not see at all (control: compare with the previous release)"
gate block "env git commit"                                    "$DS" "env git commit -m rt-env-git"
gate block "env with a variable, then git"                     "$DS" "env LANG=C git commit -m rt-env-var"
gate block "sh -c"                                             "$DS" "sh -c 'git commit -m rt-sh-c'"
gate block "eval"                                              "$DS" "eval \"git commit -m rt-eval\""
gate block "here-string into bash"                             "$DS" "bash <<< 'git commit -m rt-herestring'"
gate block "xargs builds the command"                          "$DS" "echo rt-xargs | xargs git commit -m"
gate block "xargs supplies the subcommand"                     "$DS" "echo commit | xargs -I{} git {} -m rt-xargs-sub"
gate block "git alias that runs a nested git"                  "$DS" "git -c alias.ci='!git commit -m rt-alias' ci"
gate block "git alias for the subcommand itself"               "$DS" "git -c alias.ci=commit ci -m rt-alias2"
gate block "variable holds the word git"                       "$DS" "g=git; \$g commit -m rt-var-git"
gate block "variable holds the subcommand"                     "$DS" "c=commit; git \$c -m rt-var-sub"
gate block "braces group"                                      "$DS" "{ git commit -m rt-braces; }"
gate block "after then"                                        "$DS" "if true; then git commit -m rt-then; fi"
gate block "after the negation sign"                           "$DS" "! git commit -m rt-bang"
gate block "time / nohup prefix"                               "$DS" "nohup git commit -m rt-nohup"
gate block "backslash-newline between git and commit"          "$DS" "git \\
commit -m rt-backslash"
gate block "find -exec"                                        "$DS" "find . -maxdepth 0 -exec git commit -m rt-find \\;"
gate block "push through env"                                  "$DS" "env git push"
gate block "push through bash -c"                              "$DS" "bash -c 'git push'"
echo "# total: $n, commit or push let through although it should be blocked (OPEN): $open"
G -C "$DS" worktree remove --force "$WT" 2>/dev/null
