#!/bin/bash
# Line 5 live runs on the clean candidate install.
B="$(cd "$(dirname "$0")/.." && pwd)"; R="$B/tools/live-run.sh"; P="$B/prompts"
# already run separately as the sign-in smoke: bash "$R" live line5-live-1-ordinary-acceptEdits acceptEdits "$P/l5-ordinary-acceptEdits.txt"
bash "$R" live line5-live-2-ordinary-auto auto "$P/l5-ordinary-auto.txt"
bash "$R" live line5-live-3-sensitive-acceptEdits acceptEdits "$P/l5-sensitive-acceptEdits.txt"
bash "$R" live line5-live-4-sensitive-auto auto "$P/l5-sensitive-auto.txt"
LIVE_EXTRA_ENV="IWE_MEMORY_WRITE_AUTO_APPROVE=0" bash "$R" live line5-live-5-control-hook-off acceptEdits "$P/l5-control.txt"
