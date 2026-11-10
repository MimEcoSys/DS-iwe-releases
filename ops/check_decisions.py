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


def decision_keys(decisions: str, row: str) -> set[str]:
    """Keys from the value cell of the decisions table row that starts with `row`."""
    for line in decisions.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0].startswith(row):
            return set(KEY.findall(cells[1]))
    return set()


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
    taken = decision_keys(decisions, TAKEN_ROW)
    deferred = decision_keys(decisions, DEFERRED_ROW)
    problems = [f"{key}: в решениях, но нет среди кандидатов" for key in sorted((taken | deferred) - known)]
    problems += [f"{key}: одновременно «взято» и «отложено»" for key in sorted(taken & deferred)]
    for unit, keys in sorted(inseparable_groups(handoff).items()):
        in_taken = sorted(k for k in keys if k in taken)
        in_deferred = sorted(k for k in keys if k in deferred)
        if in_taken and in_deferred:
            problems.append(
                f"группа {unit} неразделима, но разорвана: взято {', '.join(in_taken)}, "
                f"отложено {', '.join(in_deferred)}"
            )
        elif in_taken and len(in_taken) < len(keys):
            missing = sorted(set(keys) - set(in_taken))
            problems.append(f"группа {unit} неразделима: взято {', '.join(in_taken)}, не названо {', '.join(missing)}")
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
    except (OSError, yaml.YAMLError) as error:
        print(f"check_decisions: {error}", file=sys.stderr)
        return 2

    records = handoff.get("records") or {}
    problems: list[str] = []
    for key, record in records.items():
        problems += record_problems(key, record or {})
    problems += decision_problems(handoff, decisions)

    for problem in problems:
        print(f"FAIL: {problem}")
    if problems:
        print(f"Выпуск {release}: замечаний {len(problems)} (кандидатов {len(records)})")
        return 1
    print(f"OK: выпуск {release}, кандидатов {len(records)}, замечаний нет")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
