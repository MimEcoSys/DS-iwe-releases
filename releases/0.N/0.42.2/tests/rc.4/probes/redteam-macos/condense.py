#!/usr/bin/env python3
"""Condensed, publishable transcript of a live Claude Code run (stream-json) and cleaned text logs.

usage: condense.py <redteam-dir> <src-file> <dst-file> <user-name>
  *.jsonl -> tool calls, tool answers, the agent's words; any other file -> cleaned copy.
No local paths, machine ids, e-mails, user names or sign-in tokens are left in the output.
"""
import json
import re
import sys
from pathlib import Path

base, src, dst, user = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
parent = str(Path(base).parent)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
UUID = re.compile(r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}")
TOKEN = re.compile("sk-" + r"ant-[A-Za-z0-9_\-]+")
# any other long opaque string that is not a plain hex digest (git and sha256 hashes stay readable)
LONG = re.compile(r"(?<![A-Za-z0-9_+=\-])(?![0-9a-f]{40,64}(?![A-Za-z0-9_+=\-]))[A-Za-z0-9_+=\-]{60,}(?![A-Za-z0-9_+=\-])")
# test identities of the disposable installs, written in two halves so that this file holds no address
TEST_DOMAIN = "@" + "test.local"
ALLOWED_EMAILS = {"noreply@anthropic.com", "noreply@github.com"}


def slug(path: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", path)


def clean(text: str) -> str:
    text = TOKEN.sub("<TOKEN>", text)
    for root, mark in ((base, "<RT>"), (parent, "<TMP>")):
        text = text.replace(root, mark).replace(slug(root), mark + "-SLUG")
    text = re.sub(r"-private-tmp-claude-\d+--Users-[A-Za-z0-9]+-IWE-[A-Za-z0-9\-]*", "<TMP-SLUG>", text)
    text = re.sub(r"/private/tmp/claude-\d+/-Users-[A-Za-z0-9]+-IWE/[^\s\"'`)]*", "<TMP-OTHER>", text)
    text = UUID.sub("<uuid>", text)
    text = EMAIL.sub(lambda m: m.group(0) if m.group(0).lower() in ALLOWED_EMAILS else "<EMAIL>", text)
    text = re.sub(r"/Users/[A-Za-z0-9._-]+", "/Users/<user>", text)
    text = re.sub(r"/var/folders/[A-Za-z0-9_]+/[A-Za-z0-9_]+/", "/var/folders/<id>/", text)
    text = text.replace(user, "<user>")
    text = LONG.sub("<TOKEN>", text)
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def cut(value, limit: int) -> str:
    value = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return value if len(value) <= limit else value[:limit] + f" …[cut, {len(value)} characters in all]"


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
            out.append(f"# Claude Code {event.get('claude_code_version')} · model {event.get('model')} · "
                       f"permission mode {event.get('permissionMode')}")
        elif kind == "system" and event.get("subtype") == "permission_denied":
            out.append("[system] permission request declined: nobody can answer it in a non-interactive run")
        elif kind == "assistant":
            for part in event.get("message", {}).get("content", []):
                if part.get("type") == "text":
                    out.append("AGENT: " + part["text"])
                elif part.get("type") == "tool_use":
                    out.append(f"CALL {part.get('name')}: " + cut(part.get("input"), 900))
        elif kind == "user":
            content = event.get("message", {}).get("content", [])
            if isinstance(content, str):
                continue
            for part in content:
                if isinstance(part, dict) and part.get("type") == "tool_result":
                    flag = "REFUSED/ERROR" if part.get("is_error") else "ANSWER"
                    out.append(f"{flag}: " + cut(result_text(part.get("content")), 1200))
        elif kind == "result":
            denials = [d.get("tool_name", "?") + " " + cut(d.get("tool_input"), 300) for d in event.get("permission_denials", [])]
            out.append(f"# RESULT: {event.get('subtype')} · turns {event.get('num_turns')} · declined calls {len(denials)}")
            out.extend("#   declined: " + d for d in denials)
    return "\n".join(out) + "\n"


text = condense(src) if src.suffix == ".jsonl" else src.read_text(encoding="utf-8", errors="replace")
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(clean(text), encoding="utf-8")
print(dst.name, dst.stat().st_size)
