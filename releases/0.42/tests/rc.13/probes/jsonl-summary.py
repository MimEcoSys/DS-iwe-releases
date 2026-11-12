#!/usr/bin/env python3
"""Summarise a Claude Code stream-json log: session, turns, duration, tool calls, final answer.

Usage: jsonl-summary.py <log.jsonl> [answer.md]
Writes the final answer to answer.md when given; prints counts and the tool calls (truncated).
"""
import json
import sys

log_path = sys.argv[1]
answer_path = sys.argv[2] if len(sys.argv) > 2 else None
calls, result, session = [], None, None
for line in open(log_path, encoding="utf-8", errors="replace"):
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        continue
    session = session or event.get("session_id")
    if event.get("type") == "assistant":
        for block in event["message"].get("content", []):
            if block.get("type") == "tool_use":
                calls.append(f'{block["name"]}: {json.dumps(block["input"], ensure_ascii=False)[:150]}')
    elif event.get("type") == "result":
        result = event

if result is None:
    sys.exit(f"{log_path}: no final result event")
print(f"сессия {session}; ходов {result.get('num_turns')}; {round(result.get('duration_ms', 0) / 60000, 1)} мин; "
      f"инструментов {len(calls)}; ошибка: {result.get('is_error')}")
for call in calls:
    print("  " + call)
if answer_path:
    with open(answer_path, "w", encoding="utf-8") as out:
        out.write(result.get("result") or "")
