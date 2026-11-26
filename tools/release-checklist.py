#!/usr/bin/env python3
"""Consolidated checklist for one release: every protocol line, who marked it and when,
the latest attack verdict and the Release Lead's final decision — one view instead of
opening every tests/rc.<K>/*.yaml file and decisions.md by hand (WP-529, found 15.11.2026:
the pilot asked who confirmed each checklist item and when, and there was no single place
that answered it).

With --closure it is a gate for the "After release" actions 17а-28 of the general checklist
(WP-529: on 0.42.2 and 0.42.1 the lines 25-28 stayed "нет" after the release was announced, and
nothing said the release was not closed). It reads releases/<X>.N/<N>/checklist.md and lists
every such row whose state is not "да" or "не нужно" (so "нет", "частично", "идёт", empty and a
missing row all count as open).

Usage: python3 tools/release-checklist.py [--repo PATH] [--release N] [--closure]
Exit: report mode — 0 always (this is a report, the gate is check_decisions.py);
      --closure — 0 when every row 17а-28 is closed, 1 while some are open, 2 when the checklist is unreadable.
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


# Actions after the release (step 8 of the general checklist). Action 17 (merge and tag) is
# the release itself, so it is not part of "closing"; numbers keep the Cyrillic letters of the checklist.
AFTER_RELEASE_ACTIONS = ("17а", "17б") + tuple(str(n) for n in range(18, 29))
CLOSED_STATE = re.compile(r"^(да|не нужно)(?![\w])", re.IGNORECASE)
CHECKLIST_ROW = re.compile(r"^\|\s*(\d+[а-я]?)\s*\|")


def closure_open_rows(checklist_md: str) -> list[tuple[str, str]]:
    """Rows 17а-28 whose state is not "да" / "не нужно": (number, state as written; empty when missing)."""
    states: dict[str, str] = {}
    for row in checklist_md.splitlines():
        row = row.strip()
        if not CHECKLIST_ROW.match(row):
            continue
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) >= 3:
            states.setdefault(cells[0], cells[2])
    return [(n, states.get(n, "")) for n in AFTER_RELEASE_ACTIONS if not CLOSED_STATE.match(states.get(n, ""))]


def closure_report(release: str, open_rows: list[tuple[str, str]]) -> str:
    if not open_rows:
        return f"Выпуск {release} закрыт: все строки 17а–28 чек-листа отмечены «да» или «не нужно»."
    lines = [f"Выпуск {release} не закрыт: открыты строки {', '.join(n for n, _ in open_rows)}"]
    for number, state in open_rows:
        shown = (state[:90] + "…") if len(state) > 90 else state
        lines.append(f"  {number}: {shown or 'нет строки или пусто'}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--release", default="0.42")
    parser.add_argument("--closure", action="store_true",
                        help="list rows 17а-28 of the release checklist that are not closed; exit 1 while any is open")
    args = parser.parse_args(argv)

    release_dir = args.repo / layout.release_dir(args.release)
    if args.closure:
        try:
            checklist_md = (release_dir / "checklist.md").read_text(encoding="utf-8")
        except OSError as error:
            print(f"Не удалось прочитать чек-лист выпуска {args.release}: {error}", file=sys.stderr)
            return 2
        open_rows = closure_open_rows(checklist_md)
        print(closure_report(args.release, open_rows))
        return 1 if open_rows else 0
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
