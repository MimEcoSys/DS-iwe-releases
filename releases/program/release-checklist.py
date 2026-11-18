#!/usr/bin/env python3
"""Consolidated checklist for one release: every protocol line, who marked it and when,
the latest attack verdict and the Release Lead's final decision — one view instead of
opening every tests/rc.<K>/*.yaml file and decisions.md by hand (WP-529, found 15.11.2026:
the pilot asked who confirmed each checklist item and when, and there was no single place
that answered it).

Usage: python3 releases/program/release-checklist.py [--repo PATH] [--release N]
Exit: 0 always — this is a report, not a gate (the gate is check_decisions.py).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout  # noqa: E402

PROTOCOL_ROW = re.compile(r"^\|\s*(\d+)\s*\|(.+)\|(.+)\|(.+)\|(.+)\|(.+)\|$")
RC_DIR = re.compile(r"^rc\.(\d+)$")


def protocol_lines(protocol_md: str) -> dict[int, str]:
    lines: dict[int, str] = {}
    for row in protocol_md.splitlines():
        m = PROTOCOL_ROW.match(row.strip())
        if m:
            lines[int(m.group(1))] = m.group(2).strip()
    return lines


def latest_rc_dir(tests_dir: Path) -> Path | None:
    candidates = [(int(m.group(1)), path) for path in tests_dir.glob("rc.*") if path.is_dir() and (m := RC_DIR.match(path.name))]
    return max(candidates, key=lambda item: item[0])[1] if candidates else None


def decision_value(decisions_md: str, row: str) -> str:
    for line in decisions_md.splitlines():
        if line.strip().startswith(f"| {row}"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            return cells[1] if len(cells) > 1 else ""
    return ""


# Steps 7-9 of "Порядок" in protocol.md happen after the release, so no rc.<K>/*.yaml mark can
# hold them (WP-529 F276 item 2, 17.11.2026: the checklist showed only the build-check lines and
# the after-release steps were silently skipped on 0.42). Each step is answered by one row of the
# decisions form; a missing row is shown as a gap, never as done.
POST_RELEASE_ROWS = (
    ("7. Проверка опубликованного, окно наблюдения", "Итог окна наблюдения"),
    ("8. Исправления сведены в рабочую копию Разработчика", "Свод исправлений в рабочую копию Разработчика"),
    ("9. Табло пересобрано после выхода", "Табло пересобрано после выхода"),
)


def post_release_lines(decisions_md: str) -> list[str]:
    lines = []
    for title, row in POST_RELEASE_ROWS:
        value = decision_value(decisions_md, row) or "— не заполнено —"
        lines.append(f"  {title}\n      {value}")
    return lines


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--release", default="0.42")
    args = parser.parse_args(argv)

    release_dir = args.repo / layout.release_dir(args.release)
    protocol_md = (release_dir / "protocol.md").read_text(encoding="utf-8")
    decisions_md = (release_dir / "decisions.md").read_text(encoding="utf-8")
    tests_dir = release_dir / "tests"
    rc_dir = latest_rc_dir(tests_dir)

    rows = protocol_lines(protocol_md)
    marks: dict[int, list[str]] = {n: [] for n in rows}
    red_team: list[str] = []
    if rc_dir is not None:
        for mark_file in sorted(rc_dir.glob("*.yaml")):
            data = yaml.safe_load(mark_file.read_text(encoding="utf-8")) or {}
            for mark in data.get("marks") or []:
                entry = f"{mark.get('result', '?')} — {mark.get('tester', '?')} ({mark_file.name})"
                for raw_n in str(mark.get("line", "")).split(","):
                    try:
                        n = int(raw_n.strip())
                    except ValueError:
                        continue
                    if n in marks:
                        marks[n].append(entry)
            block = data.get("red_team")
            if isinstance(block, dict) and block:
                red_team.append(f"{block.get('verdict', '?')} — {block.get('checker', '?')} ({mark_file.name})")

    print(f"Выпуск {args.release} — последняя сборка: {rc_dir.name if rc_dir else 'нет'}\n")
    for n in sorted(rows):
        entries = marks.get(n) or ["— не отмечено ни в одном файле —"]
        print(f"{n:>2}. {rows[n][:60]}")
        for entry in entries:
            print(f"      {entry}")
    print()
    print("Независимая атака (строка 13):")
    for entry in red_team or ["— нет записанного вердикта —"]:
        print(f"  {entry}")
    print()
    print("После выхода (шаги 7–9 протокола):")
    print("\n".join(post_release_lines(decisions_md)))
    print()
    print(f"Итог Выпускающего: {decision_value(decisions_md, 'Итог: выпускаем / откладываем') or '— не заполнено —'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
