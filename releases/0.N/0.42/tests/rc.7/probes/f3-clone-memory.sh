#!/run/current-system/sw/bin/bash
# F3 check inside a bwrap sandbox holding a fresh 0.41.11 install: put a random marker into the template
# clone's memory/navigation.md, update over the rc channel pinned to <tag> through the API mock, then look
# for the marker in the backup folder the update output names.
# Usage: f3-clone-memory.sh <tag> <lsremote-file pinned to that tag> <log-dir>
set -u
tag=$1 ls=$2 L=$3
mkdir -p "$L" ~/shim ~/api && cp ~/rt5-1/curl ~/rt5-1/apimock.py ~/shim/ && cp "$ls" ~/api/lsremote.txt
T=~/IWE/FMT-exocortex-template
mark="F3-MARK-$(od -An -N6 -tx1 /dev/urandom | tr -d ' \n')"
echo "<!-- $mark правка в папке шаблона -->" >> "$T/memory/navigation.md"
cd "$T" || exit 1
PATH=~/shim:$PATH RT_SHIM_DIR=$HOME/shim IWE_UPDATE_CHANNEL=rc bash update.sh --yes > "$L/f3-$tag-update.log" 2>&1 </dev/null
echo "$tag: update.sh --yes код $?; $(grep -m1 'Канал поставки' "$L/f3-$tag-update.log" | sed 's/^ *//')"
echo "  метка в папке шаблона после обновления: $(grep -c "$mark" "$T/memory/navigation.md")"
echo "  файлы с меткой в установке:"; grep -rl --exclude-dir=.git "$mark" ~/IWE ~/.claude 2>/dev/null | sed "s#^$HOME#  ~#"
echo "  строки вывода про память шаблона:"; grep -n 'template-clone\|клоне шаблона\|клон шаблона\|memory-pre-update' "$L/f3-$tag-update.log" | head -6 | cut -c1-260 | sed 's/^/    /'
named=$(grep -o "$HOME/IWE/.backups/memory-pre-update/[^ ]*template-clone[^ )»,;]*" "$L/f3-$tag-update.log" | head -1)
if [ -n "$named" ]; then
  f="$named"; [ -d "$f" ] && f="$f/navigation.md"
  echo "  путь из вывода: ${named/#$HOME/~}; метка в $(basename "$f"): $(grep -c "$mark" "$f" 2>/dev/null || echo 'файла нет')"
else
  echo "  путь template-clone в выводе не назван"
fi
