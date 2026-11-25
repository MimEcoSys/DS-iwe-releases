#!/bin/bash
# usage: probe-memory-hook-sensitive.sh <case-dir> <label>
# rc.3 attack on the sensitive-path filter of memory-write-permission.sh (#1626): the hook must stay
# silent (the prompt remains) for .git/.claude/.github/.ssh/.gnupg and every hidden name inside memory.
# No agent: the hook receives the request JSON on stdin. Every fixture lives in the case dir.
# RT_HOOK=<file> runs the same fixtures against the hook of another build.
set -u
CASE="$1"; LABEL="$2"; RT="$(cd "$(dirname "$0")/.." && pwd)"; W="$CASE/ws"; H="$CASE/home"
case "$CASE" in "$RT"/*) ;; *) echo "refusing: case outside red team folder"; exit 98 ;; esac
HOOK="${RT_HOOK:-$W/.claude/hooks/memory-write-permission.sh}"
MEM="$(cd "$W/memory" && pwd -P)"
mask() { sed "s#$RT#<RT>#g"; }
n=0; unexpected=0

# ask <expect: allow|silent> <label> <mode> <tool> <field> <path> [env assignments...]
ask() {
  local expect="$1" label="$2" mode="$3" tool="$4" field="$5" path="$6"; shift 6
  local out rc d flag=ok
  out=$(jq -n --arg m "$mode" --arg t "$tool" --arg f "$field" --arg p "$path" \
        '{hook_event_name:"PermissionRequest",permission_mode:$m,tool_name:$t,tool_input:{($f):$p,content:"x"}}' \
        | env -i HOME="$H" PATH="/usr/bin:/bin:$RT/../tools/brewbin" CLAUDE_PROJECT_DIR="$W" "$@" bash "$HOOK" 2>/dev/null); rc=$?
  if printf '%s' "$out" | grep -q '"behavior": *"allow"'; then d=allow; elif [ -z "$out" ]; then d=silent; else d="other"; fi
  n=$((n + 1))
  [ "$d" = "$expect" ] || { flag="UNEXPECTED"; unexpected=$((unexpected + 1)); }
  printf '%-10s | expect=%-6s got=%-6s exit=%s | %s | mode=%s tool=%s | %s\n' "$flag" "$expect" "$d" "$rc" "$label" "$mode" "$tool" "$(printf '%s' "$path" | mask)"
}

echo "# hook under test: $LABEL"
echo "# fixtures (all inside the disposable memory folder)"
M="$W/memory"
mkdir -p "$MEM/.git/hooks" "$MEM/.claude" "$MEM/.github/workflows" "$MEM/.ssh" "$MEM/.gnupg" "$MEM/.hidden/deep" \
         "$MEM/sub/.git/hooks" "$MEM/sub/deep" "$MEM/plain/hooks" "$MEM/alias-parent"
ln -sfn "$MEM/.git/hooks" "$MEM/githooks-link"          # plain name -> hidden folder
ln -sfn "$MEM/.git" "$MEM/gitdir-link"
ln -sfn "$MEM/.claude" "$MEM/claude-link"
: > "$MEM/.git/config"; ln -sfn "$MEM/.git/config" "$MEM/config-link.md"      # plain file name -> file under .git
ln "$MEM/.git/config" "$MEM/hardlink-to-git-config.md" 2>/dev/null || true    # same inode, plain name
# hidden NAME that is a link to a plain folder: the written path says .git, the real path does not
ln -sfn "$MEM/plain" "$MEM/alias-parent/.git"
ln -sfn "$MEM/plain" "$MEM/alias-parent/.claude"
ln -sfn "$MEM/plain/hooks/target.md" "$MEM/alias-parent/.zshrc"; : > "$MEM/plain/hooks/target.md"

echo "# 1. baseline: ordinary files still get the answer"
ask allow  "ordinary file"                              acceptEdits Write file_path "$M/rt-note.md"
ask allow  "ordinary file, nested"                      auto        Edit  file_path "$M/sub/deep/a.md"
ask allow  "name that only CONTAINS a dot-word (my.git.md)" acceptEdits Write file_path "$M/my.git.md"
ask allow  "folder named git (no dot)"                  acceptEdits Write file_path "$M/plain/hooks/x.md"
echo "# 2. the names of the fix, both modes, all four tools"
for mode in acceptEdits auto; do
  ask silent ".git/hooks/pre-commit"                    "$mode" Write file_path "$M/.git/hooks/pre-commit"
  ask silent ".git/config"                              "$mode" Edit  file_path "$M/.git/config"
  ask silent ".claude/settings.json"                    "$mode" Write file_path "$M/.claude/settings.json"
  ask silent ".github/workflows/x.yml"                  "$mode" Write file_path "$M/.github/workflows/x.yml"
  ask silent ".ssh/authorized_keys"                     "$mode" Write file_path "$M/.ssh/authorized_keys"
  ask silent ".gnupg/gpg.conf"                          "$mode" Write file_path "$M/.gnupg/gpg.conf"
done
ask silent "MultiEdit .git/config"                      acceptEdits MultiEdit file_path "$M/.git/config"
ask silent "NotebookEdit under .claude"                 acceptEdits NotebookEdit notebook_path "$M/.claude/x.ipynb"
echo "# 3. hidden files and folders"
for name in .zshrc .bashrc .profile .gitconfig .gitmodules .gitattributes .gitignore .mcp.json .claude.json .env .npmrc .hidden/x.md .hidden/deep/x.md; do
  ask silent "hidden name $name"                        acceptEdits Write file_path "$M/$name"
done
ask silent "hidden folder below an ordinary one"        acceptEdits Write file_path "$M/sub/.git/hooks/pre-commit"
echo "# 4. other spellings of the same place"
ask silent "upper case .GIT (same folder on this volume)" acceptEdits Write file_path "$M/.GIT/hooks/pre-commit"
ask silent "mixed case .Git/Hooks"                      acceptEdits Write file_path "$M/.Git/Hooks/pre-commit"
ask silent "upper case .CLAUDE"                         acceptEdits Write file_path "$M/.CLAUDE/settings.json"
ask silent "double slash"                               acceptEdits Write file_path "$M//.git//hooks/pre-commit"
ask silent "dot segment"                                acceptEdits Write file_path "$M/./.git/./hooks/pre-commit"
ask silent "dot-dot detour sub/../.git"                 acceptEdits Write file_path "$M/sub/../.git/hooks/pre-commit"
ask silent "dot-dot detour .git/../.git"                acceptEdits Write file_path "$M/.git/../.git/config"
ask silent "detour through a hidden folder to an ordinary file: .hidden/../rt-note.md (real path is ordinary)" acceptEdits Write file_path "$M/.hidden/../rt-note.md"
ask silent "trailing slash on the hidden folder"        acceptEdits Write file_path "$M/.git/"
ask silent ".git itself"                                acceptEdits Write file_path "$M/.git"
ask silent "macOS data fork of a hidden file"           acceptEdits Write file_path "$M/.git/config/..namedfork/data"
ask silent "name with a trailing dot: .git."            acceptEdits Write file_path "$M/.git./x"
ask silent "name with a trailing blank"                 acceptEdits Write file_path "$M/.git /x"
ask silent "zero-width character before the dot"        acceptEdits Write file_path "$M/"$'\xe2\x80\x8c'".git/hooks/pre-commit"
ask silent "zero-width character inside: .g<ZWNJ>it"    acceptEdits Write file_path "$M/.g"$'\xe2\x80\x8c'"it/hooks/pre-commit"
ask silent "full-width dot"                             acceptEdits Write file_path "$M/"$'\xef\xbc\x8e'"git/hooks/pre-commit"
echo "# 5. links inside memory"
ask silent "plain link name -> .git/hooks"              acceptEdits Write file_path "$M/githooks-link/pre-commit"
ask silent "plain link name -> .git"                    acceptEdits Write file_path "$M/gitdir-link/config"
ask silent "plain link name -> .claude"                 acceptEdits Write file_path "$M/claude-link/settings.json"
ask silent "plain file link -> .git/config"             acceptEdits Write file_path "$M/config-link.md"
ask silent "hard link with a plain name to .git/config (same inode; the hook cannot see it)" acceptEdits Write file_path "$M/hardlink-to-git-config.md"
echo "# 5a. the reverse: the WRITTEN path names .git/.claude/.zshrc, the name is a link to an ordinary place"
ask silent "written .git/hooks/pre-commit, .git is a link to an ordinary folder" acceptEdits Write file_path "$M/alias-parent/.git/hooks/pre-commit"
ask silent "written .claude/settings.json, .claude is a link to an ordinary folder" acceptEdits Write file_path "$M/alias-parent/.claude/settings.json"
ask silent "written .zshrc, the file is a link to an ordinary file" acceptEdits Write file_path "$M/alias-parent/.zshrc"
echo "# 6. modes outside the approve list keep silent for ordinary and hidden names alike"
for m in default plan bypassPermissions dontAsk ""; do
  ask silent "mode '$m', ordinary file"                 "$m" Write file_path "$M/rt-note.md"
done
echo "# what the file system says about the odd spellings (does the name reach the real .git?)"
for spelling in ".GIT" ".Git" $'\xe2\x80\x8c'".git" ".g"$'\xe2\x80\x8c'"it" $'\xef\xbc\x8e'"git" ".git." ".git "; do
  if [ -d "$MEM/$spelling/hooks" ]; then r="reaches .git"; else r="another name (no such folder)"; fi
  printf 'fs         | %-28s -> %s\n' "$(printf '%s' "$spelling" | LC_ALL=C sed 's/[^ -~]/?/g')" "$r"
done
echo "# total requests: $n, answers different from the expected one: $unexpected"
