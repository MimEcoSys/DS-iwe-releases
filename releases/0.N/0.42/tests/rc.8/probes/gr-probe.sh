#!/usr/bin/env bash
# RT2-2 re-check: guarded-rm with a TMPDIR outside the system temp dirs must refuse and keep the folder.
# Target lives in the disposable test user's home (outside /tmp); control case deletes inside /tmp.
set -u
SRC=/home/iwe-test/IWE/FMT-exocortex-template
TAG="${1:?tag}"
FIX=$(mktemp -d /tmp/gr-probe.XXXXXX)
mkdir -p "$FIX/ws"
git -C "$SRC" archive "$TAG" | tar -x -C "$FIX/ws"
GR="$FIX/ws/.claude/bin/guarded-rm"
# NixOS has no /bin/rm or /usr/bin/rm; point a private copy at the real rm (known finding, not under test).
sed -i "s#/usr/bin/rm#$(command -v rm)#g; s#\([^a-z]\)/bin/rm#\1$(command -v rm)#g" "$GR"
OUT="$HOME/gr-victim-$TAG"
run() {  # $1 label, $2 TMPDIR value or "-", $3 target dir
  local label=$1 td=$2 target=$3 rc
  mkdir -p "$target/sub" && echo keep > "$target/sub/f"
  if [ "$td" = "-" ]; then env -i PATH="$PATH" HOME="$HOME" bash "$GR" -rf "$target" 2>"$FIX/err"; rc=$?
  else env -i PATH="$PATH" HOME="$HOME" TMPDIR="$td" bash "$GR" -rf "$target" 2>"$FIX/err"; rc=$?; fi
  printf '%-34s rc=%s folder=%s | %s\n' "$label" "$rc" "$([ -d "$target" ] && echo на_месте || echo удалена)" "$(tr '\n' ' ' < "$FIX/err")"
}
echo "== $TAG guarded-rm"
run "no TMPDIR, target in home"   -           "$OUT/IWE"
run "TMPDIR=home, target in home" "$OUT"      "$OUT/IWE"
run "TMPDIR=\$HOME, target in home" "$HOME"   "$OUT/IWE"
run "control: target inside /tmp" -           "$FIX/victim"
rm -rf "$OUT" "$FIX"
