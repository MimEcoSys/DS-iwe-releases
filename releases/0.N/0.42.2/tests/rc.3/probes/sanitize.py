#!/usr/bin/env python3
"""Publish test logs without local paths, machine ids, e-mails, user names or sign-in tokens.

usage: sanitize.py <base-dir> <logs-dir> <live-raw-dir> <dst-dir> <user-name>
  <logs-dir>/*.raw.log and line2-hooks-*.txt  -> <dst>/<name>.txt
  <live-raw-dir>/line[45]-live-*.jsonl (Claude Code stream-json) -> <dst>/<name>.txt, condensed transcript
"""
import json
import re
import sys
from pathlib import Path

base, logs, raw, dst, user = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), sys.argv[5]
slug = re.sub(r"[^A-Za-z0-9]", "-", base)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
UUID = re.compile(r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}")
TOKEN = re.compile("sk-" + r"ant-[A-Za-z0-9_\-]+")
# any other long opaque string that is not a plain hex digest (git and sha256 hashes stay readable)
LONG = re.compile(r"(?<![A-Za-z0-9_+=\-])(?![0-9a-f]{40,64}(?![A-Za-z0-9_+=\-]))[A-Za-z0-9_+=\-]{60,}(?![A-Za-z0-9_+=\-])")
ALLOWED_EMAILS = {"noreply@anthropic.com", "noreply@github.com"}


def clean(text: str) -> str:
    text = TOKEN.sub("<TOKEN>", text)
    text = text.replace(base, "<TMP>").replace(slug, "<TMP-SLUG>")
    text = re.sub(r"-private-tmp-claude-\d+--Users-[A-Za-z0-9]+-IWE-[A-Za-z0-9\-]*", "<TMP-SLUG>", text)
    text = re.sub(r"/private/tmp/claude-\d+/-Users-[A-Za-z0-9]+-IWE/[^\s\"'`)]*", "<TMP-OTHER>", text)
    text = UUID.sub("<uuid>", text)
    text = EMAIL.sub(lambda m: m.group(0) if m.group(0).lower() in ALLOWED_EMAILS else "<email>", text)
    text = re.sub(r"/Users/[A-Za-z0-9._-]+", "/Users/<user>", text)
    text = re.sub(r"/var/folders/[A-Za-z0-9_]+/[A-Za-z0-9_]+/", "/var/folders/<id>/", text)
    text = text.replace(user, "<user>")
    text = LONG.sub("<TOKEN>", text)
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def cut(value, limit: int) -> str:
    value = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return value if len(value) <= limit else value[:limit] + f" …[обрезано, всего {len(value)} знаков]"


def result_text(content) -> str:
    if isinstance(content, list):
        return "\n".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content)


def condense(path: Path) -> str:
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = event.get("type")
        if kind == "system" and event.get("subtype") == "init":
            servers = ", ".join(f"{s.get('name')}={s.get('status')}" for s in event.get("mcp_servers", []))
            out.append(f"# Claude Code {event.get('claude_code_version')} · модель {event.get('model')} · "
                       f"режим разрешений {event.get('permissionMode')} · MCP: {servers or 'нет'}")
        elif kind == "system" and event.get("subtype") == "permission_denied":
            out.append("[система] запрос разрешения отклонён: в неинтерактивном запуске отвечать некому")
        elif kind == "assistant":
            for part in event.get("message", {}).get("content", []):
                if part.get("type") == "text":
                    out.append("АГЕНТ: " + part["text"])
                elif part.get("type") == "tool_use":
                    out.append(f"ВЫЗОВ {part.get('name')}: " + cut(part.get("input"), 1500))
        elif kind == "user":
            content = event.get("message", {}).get("content", [])
            if isinstance(content, str):
                continue
            for part in content:
                if isinstance(part, dict) and part.get("type") == "tool_result":
                    flag = "ОТКАЗ/ОШИБКА" if part.get("is_error") else "ОТВЕТ"
                    out.append(f"{flag}: " + cut(result_text(part.get("content")), 2500))
        elif kind == "result":
            denials = [d.get("tool_name", "?") + " " + cut(d.get("tool_input"), 300) for d in event.get("permission_denials", [])]
            out.append(f"# ИТОГ: {event.get('subtype')} · ходов {event.get('num_turns')} · "
                       f"условная стоимость ${event.get('total_cost_usd', 0):.2f} · отклонённых вызовов {len(denials)}")
            out.extend("#   отклонено: " + d for d in denials)
    return "\n".join(out) + "\n"


dst.mkdir(parents=True, exist_ok=True)
for source in sorted(logs.glob("*.raw.log")) + sorted(logs.glob("line2-hooks-*.txt")):
    name = source.name.replace(".raw.log", ".txt")
    text = clean(source.read_text(encoding="utf-8", errors="replace"))
    (dst / name).write_text(text, encoding="utf-8")
    print(name, len(text))
for source in sorted(raw.glob("line[45]-live-*.jsonl")):
    name = source.name.replace(".jsonl", ".txt")
    text = clean(condense(source))
    (dst / name).write_text(text, encoding="utf-8")
    print(name, len(text))
