#!/bin/bash
B="$(cd "$(dirname "$0")/.." && pwd)"; R="$B/tools/live-run.sh"; P="$B/prompts"
bash "$R" upg line5-live-upg-2-auto auto "$P/l5-upg-2.txt"
bash "$R" upg line5-live-upg-3-sensitive-acceptEdits acceptEdits "$P/l5-upg-3.txt"
bash "$R" upg line5-live-upg-4-sensitive-auto auto "$P/l5-upg-4.txt"
LIVE_EXTRA_ENV="IWE_MEMORY_WRITE_AUTO_APPROVE=0" bash "$R" upg line5-live-upg-5-control-hook-off acceptEdits "$P/l5-upg-5.txt"
