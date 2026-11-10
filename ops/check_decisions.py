#!/usr/bin/env python3
"""Mechanical check of a release's candidates and decisions (WP-529 Ф250/Ф252).

The release reviewer (an AI agent) judges candidates; this script does the part
that must not depend on judgement:

1. Every record of ops/developer-handoff.yaml has what the Release Lead needs:
   what the user gets, how to check, a rollback unit with commits, risk and
   recommendation.
2. releases/<N>/decisions.md names only known keys, never both takes and defers
   the same key, and never splits a group marked "separable: нет" (one merge
   whose records can only be taken or deferred together).

Fields of the CHANGELOG entries themselves are checked in the template by
scripts/check-changelog-fields.py; this script does not repeat it.

Usage: python3 ops/check_decisions.py [--repo PATH] [--release N]
Exit: 0 - no problems; 1 - problems listed on stdout; 2 - files unreadable.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

KEY = re.compile(r"\bU-[0-9a-f]{6}\b")
TAKEN_ROW = "Состав: что взято"
DEFERRED_ROW = "Состав: что отложено"
REQUIRED_TEXT = {
    "user_gets": "что получит пользователь",
    "how_to_check": "как проверить",
    "risk": "риск",
    "recommendation": "рекомендация",
}


def record_problems(key: str, record: dict) -> list[str]:
    problems = [
        f"{key}: пусто поле «{name}» ({field})"
        for field, name in REQUIRED_TEXT.items()
        if not str(record.get(field) or "").strip()
    ]
    if not str(record.get("rollback_unit") or "").strip():
        problems.append(f"{key}: нет слияния для отката (rollback_unit)")
    if not record.get("commits"):
        problems.append(f"{key}: нет коммитов для отката (commits)")
    return problems


class DecisionsFormError(ValueError):
    """decisions.md lacks a row the check relies on, so it cannot be read."""


def decision_keys(decisions: str, row: str) -> tuple[set[str], int]:
    """Keys from the value cells of the table rows that start with `row`, and the row count.

    A missing row is a broken form, not an empty decision: reading it as "nothing
    taken" would let the check report OK on a form it never parsed.
    """
    keys: set[str] = set()
    rows = 0
    for line in decisions.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0].startswith(row):
            rows += 1
            keys |= set(KEY.findall(cells[1]))
    if not rows:
        raise DecisionsFormError(f"в decisions.md нет строки «{row}»")
    return keys, rows


def inseparable_groups(handoff: dict) -> dict[str, list[str]]:
    """Merge id -> record keys, only for groups marked separable: нет."""
    units = {
        unit
        for unit, group in (handoff.get("groups") or {}).items()
        if str((group or {}).get("separable", "")).strip().lower() == "нет"
    }
    members: dict[str, list[str]] = {unit: [] for unit in units}
    for key, record in (handoff.get("records") or {}).items():
        unit = str((record or {}).get("rollback_unit") or "")
        if unit in members:
            members[unit].append(key)
    return members


def decision_problems(handoff: dict, decisions: str) -> list[str]:
    known = set((handoff.get("records") or {}).keys())
    taken, taken_rows = decision_keys(decisions, TAKEN_ROW)
    deferred, deferred_rows = decision_keys(decisions, DEFERRED_ROW)
    problems = [
        f"строка «{row}» в decisions.md повторяется {count} раза — оставить одну"
        for row, count in ((TAKEN_ROW, taken_rows), (DEFERRED_ROW, deferred_rows))
        if count > 1
    ]
    problems += [f"{key}: в решениях, но нет среди кандидатов" for key in sorted((taken | deferred) - known)]
    problems += [f"{key}: одновременно «взято» и «отложено»" for key in sorted(taken & deferred)]
    for unit, keys in sorted(inseparable_groups(handoff).items()):
        in_taken = sorted(k for k in keys if k in taken)
        in_deferred = sorted(k for k in keys if k in deferred)
        unnamed = sorted(set(keys) - set(in_taken) - set(in_deferred))
        if in_taken and in_deferred:
            problems.append(
                f"группа {unit} неразделима, но разорвана: взято {', '.join(in_taken)}, "
                f"отложено {', '.join(in_deferred)}"
            )
        elif (in_taken or in_deferred) and unnamed:
            verb, named = ("взято", in_taken) if in_taken else ("отложено", in_deferred)
            problems.append(f"группа {unit} неразделима: {verb} {', '.join(named)}, не названо {', '.join(unnamed)}")
    return problems


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--release", default=None, help="release number; default — `release` from developer-handoff.yaml")
    args = parser.parse_args(argv)

    try:
        handoff = yaml.safe_load((args.repo / "ops" / "developer-handoff.yaml").read_text(encoding="utf-8")) or {}
        release = args.release or str(handoff.get("release") or "")
        decisions = (args.repo / "releases" / release / "decisions.md").read_text(encoding="utf-8")
        records = handoff.get("records") or {}
        problems: list[str] = []
        for key, record in records.items():
            problems += record_problems(key, record or {})
        problems += decision_problems(handoff, decisions)
    except (OSError, yaml.YAMLError, DecisionsFormError) as error:
        print(f"check_decisions: {error}", file=sys.stderr)
        return 2

    for problem in problems:
        print(f"FAIL: {problem}")
    if problems:
        print(f"Выпуск {release}: замечаний {len(problems)} (кандидатов {len(records)})")
        return 1
    print(f"OK: выпуск {release}, кандидатов {len(records)}, замечаний нет")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
