#!/bin/bash
# usage: upg-batch.sh <summary-file> <variant>...   each variant = "label shape answer [update args]"
set -u
B="$(cd "$(dirname "$0")/.." && pwd)"; SUMMARY="$1"; shift
: > "$SUMMARY"
for v in "$@"; do
  # shellcheck disable=SC2086
  set -- $v
  label="$1"; shape="$2"; answer="$3"; shift 3
  { echo "=================== $label"; bash "$B/tools/upg-variant.sh" "$label" "$shape" "$answer" "$@" | grep -v '^[0-9]*:  (1/'; } >> "$SUMMARY" 2>&1
done
echo done
