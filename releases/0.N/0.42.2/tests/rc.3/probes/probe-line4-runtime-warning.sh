#!/bin/bash
# Standard install environment (.iwe-paths) -> reconcile script; look only for the legacy-caller warning.
W="$1"; SCRIPT="$2"; . "$W/.iwe-paths"
out=$(bash "$SCRIPT" "$W/DS-strategy" main 2>&1); rc=$?
echo "exit=$rc"; printf '%s\n' "$out" | tail -3
if printf '%s' "$out" | grep -q "used as a directory"; then echo "RESULT: warning present"; else echo "RESULT: no 'IWE_RUNTIME used as a directory' warning"; fi
