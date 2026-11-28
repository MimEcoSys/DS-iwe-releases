#!/usr/bin/env python3
"""Mechanical check of a release's candidates and decisions (WP-529 Ф250/Ф252).

The release reviewer (an AI agent) judges candidates; this script does the part
that must not depend on judgement:

1. Every record of releases/developer-handoff.yaml has what the Release Lead needs:
   what the user gets, how to check, a rollback unit with commits, risk and
   recommendation.
2. releases/<first number>.N/<N>/decisions.md names only known keys, never both takes and defers
   the same key, and never splits a group marked "separable: нет" (one merge
   whose records can only be taken or deferred together). Before the cut the
   composition may be recorded in words while the row of the cut version is
   empty: the keys come with the cut (keys_pending), and --require-final refuses it.

3. With --require-final (run by the Release Lead right before merging the release
   PR, WP-529 Ф261): the rows the release hangs on are filled, and the newest
   candidate has an independent red team verdict in releases/<first number>.N/<N>/tests/rc.<K>/<platform>-<tester>.yaml
   (`red_team:` block in any marks file of the newest rc.<K>/ folder, every such block is checked; BLOCKED fails, CAUTION needs the Release Lead's acceptance,
   `--rc-tree` ties the verdict to the tree of the candidate the PR will release).
   Without the flag an unfilled form is only reported as a note: a form still being
   filled is normal before the candidate, but it must not read as "all clear".

4. With --after-release --template-changelog PATH (run right after the release PR is merged,
   WP-529 Ф282): every record the Release Lead deferred by key is back in the "Unreleased"
   section of the template main CHANGELOG, and the form names how it was returned. A deferral
   is a `git revert` on the release branch; merging that branch into main brings the revert
   along, so without this step the deferred change silently disappears from main.

Fields of the CHANGELOG entries themselves are checked in the template by
scripts/check-changelog-fields.py; this script does not repeat it.

Usage: python3 tools/check_decisions.py [--repo PATH] [--release N] [--require-final] [--rc-tree SHA]
       [--after-release --template-changelog PATH]
Exit: 0 - no problems; 1 - problems listed on stdout; 2 - files unreadable.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout  # noqa: E402
from changelog import changelog_sections  # noqa: E402

KEY = re.compile(r"\bU-[0-9a-f]{6}\b")
TAKEN_ROW = "Состав: что взято"
DEFERRED_ROW = "Состав: что отложено"
CUT_ROW = "Версия основной ветки шаблона"
RETURN_ROW = "После выхода: отложенное возвращено в основную ветку"
FINAL_ROWS = (
    TAKEN_ROW,
    "Какие строки проверки сборки блокируют выпуск",
    "Кто исполняет роли",
    "Итог: выпускаем / откладываем",
)
# The verdict words of the template skill iwe-platform-redteam (Verdict Contract), not a local scale.
RED_TEAM_VERDICTS = ("GO", "CAUTION", "BLOCKED")
SHA1 = re.compile(r"^[0-9a-f]{40}$")
ALL_CUT_RECORDS = "всё, что влито в основную ветку шаблона после 0.41.11 и до снимка (решение 10.11.2026)"
RC_DIR = re.compile(r"^rc\.(\d+)$")
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


def keys_pending(decisions: str) -> bool:
    """The composition is decided in words and its keys wait for the cut (WP-529, 28.11.2026).

    candidates.md is built from the handoff before the Release Lead says "режем", so the form cannot
    name the keys yet. This is true only while the form HAS the row of the cut version and that row
    holds no full commit; a form without the row, with the version named, or with the all-at-cut
    wording is read as before: words without keys fail, so a misspelled composition is never read
    as an empty selection. The final check (--require-final) refuses this state.
    """
    taken, rows = decision_keys(decisions, TAKEN_ROW)
    if taken or rows != 1:
        return False
    values = row_values(decisions)
    wording = next(value for name, value in values.items() if name.startswith(TAKEN_ROW))
    if not wording or wording in ("ничего", ALL_CUT_RECORDS):
        return False
    cut = next((value for name, value in values.items() if name.startswith(CUT_ROW)), None)
    return cut is not None and not re.search(r"[0-9a-f]{40}", cut)


def selected_record_keys(handoff: dict, decisions: str, snapshot_commit: str | None = None) -> tuple[set[str], int]:
    """Resolve the Release Lead's explicit keys or the recorded all-at-cut decision."""
    taken, rows = decision_keys(decisions, TAKEN_ROW)
    if rows != 1:
        return taken, rows
    values = row_values(decisions)
    wording = next(value for name, value in values.items() if name.startswith(TAKEN_ROW))
    if wording == ALL_CUT_RECORDS:
        if not snapshot_commit:
            raise DecisionsFormError("для решения «всё до снимка» нужен снимок с версией шаблона")
        cut = next((value for name, value in values.items() if name.startswith(CUT_ROW)), "")
        match = re.search(r"[0-9a-f]{40}", cut)
        if not match or len(snapshot_commit) < 10 or not match.group().startswith(snapshot_commit):
            raise DecisionsFormError("снимок табло и версия в решении о составе выпуска различаются")
        deferred = next((value for name, value in values.items() if name.startswith(DEFERRED_ROW)), "")
        if deferred != "ничего":
            raise DecisionsFormError("решение «всё до снимка» требует явного «ничего» в отложенном")
        return set(handoff.get("records") or {}), rows
    if wording and not taken and wording != "ничего" and not keys_pending(decisions):
        raise DecisionsFormError("строка «Состав: что взято» не содержит кодов кандидатов")
    return taken, rows


def decision_problems(handoff: dict, decisions: str, snapshot_commit: str | None = None) -> list[str]:
    known = set((handoff.get("records") or {}).keys())
    taken, taken_rows = selected_record_keys(handoff, decisions, snapshot_commit)
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


def row_values(decisions: str) -> dict[str, str]:
    """Value cell of every two-column table row, keyed by the full first cell."""
    values: dict[str, str] = {}
    for line in decisions.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and line.strip().startswith("|"):
            values[cells[0]] = cells[1]
    return values


def unfilled_rows(decisions: str) -> list[str]:
    """FINAL_ROWS that are missing from the form or have an empty value cell."""
    values = row_values(decisions)
    unfilled = []
    for row in FINAL_ROWS:
        cell = next((value for name, value in values.items() if name.startswith(row)), None)
        if not (cell or "").strip():
            unfilled.append(row)
    return unfilled


def return_problems(decisions: str, changelog: str, release: str) -> list[str]:
    """Deferred records that did not come back to "Unreleased" of template main after the release merge.

    Keys are computed by the board's own parser, so a record returned with its first line
    unchanged has the same key it had among the candidates.
    """
    deferred, _ = decision_keys(decisions, DEFERRED_ROW)
    if not deferred:
        return []
    back = {entry["key"] for entry in changelog_sections(changelog).get("Unreleased", [])}
    problems = [
        f"{key}: отложено в {release}, но в «Ещё не выпущено» основной ветки шаблона записи нет — "
        "вернуть правку (откат отката) и её запись в этот раздел"
        for key in sorted(deferred - back)
    ]
    returned = next((value for name, value in row_values(decisions).items() if name.startswith(RETURN_ROW)), "")
    if not returned.strip():
        problems.append(f"в decisions.md не заполнена строка «{RETURN_ROW}»: каким запросом в шаблоне возвращено отложенное")
    return problems


def deferred_without_keys(decisions: str) -> bool:
    """The deferred row names something in words only: nothing to verify, but worth a note."""
    value = next((v for name, v in row_values(decisions).items() if name.startswith(DEFERRED_ROW)), "").strip()
    return bool(value) and value != "ничего" and not KEY.search(value)


def latest_rc_dir(tests_dir: Path) -> Path | None:
    """The rc.<K>/ folder with the largest K: one folder per candidate, a new candidate starts a new folder."""
    candidates = [(int(m.group(1)), path) for path in tests_dir.glob("rc.*") if path.is_dir() and (m := RC_DIR.match(path.name))]
    return max(candidates, key=lambda item: item[0])[1] if candidates else None


def block_problems(name: str, block: dict, rc_tree: str | None) -> list[str]:
    problems = []
    verdict = str(block.get("verdict") or "").strip()
    if verdict == "cannot_verify":
        problems.append(f"{name}: атака не смогла проверить кандидата (cannot_verify) — строка 13 не пройдена")
    elif verdict not in RED_TEAM_VERDICTS:
        problems.append(f"{name}: red_team.verdict должен быть одним из {', '.join(RED_TEAM_VERDICTS)}, а не «{verdict}»")
    for field in ("checker", "report"):
        if not str(block.get(field) or "").strip():
            problems.append(f"{name}: пусто red_team.{field}")
    tree = str(block.get("tree") or "").strip()
    if not SHA1.match(tree):
        problems.append(f"{name}: red_team.tree — не полный SHA дерева кандидата (40 символов)")
    elif rc_tree and tree != rc_tree:
        problems.append(f"{name}: вердикт относится к дереву {tree}, а выпускается {rc_tree} — атаку повторить на новом кандидате")
    if verdict == "BLOCKED":
        problems.append(f"{name}: вердикт BLOCKED — не сливать")
    if verdict == "CAUTION" and not str(block.get("accepted_by") or "").strip():
        problems.append(f"{name}: вердикт CAUTION без red_team.accepted_by — оговорки не приняты Выпускающим")
    return problems


def red_team_problems(tests_dir: Path, rc_tree: str | None) -> list[str]:
    """The newest candidate has a verdict of an independent attack recorded outside the template tree.

    The verdict cannot live in docs/release-audit-log.md of the template: that file is part of the
    release branch tree and a write after the rc stops the release (finding 1 of the 10.11 review).
    Several testers may record an attack on the same candidate; every recorded verdict must pass.
    """
    latest = latest_rc_dir(tests_dir)
    if latest is None:
        return [f"нет папки отметок rc.<K>/ в {tests_dir.name}/ — вердикта независимой атаки нет"]
    blocks = []
    for path in sorted(latest.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        block = data.get("red_team") if isinstance(data, dict) else None
        if isinstance(block, dict) and block:
            blocks.append((f"{latest.name}/{path.name}", block))
    if not blocks:
        return [f"{latest.name}/: ни в одном файле отметок нет блока red_team — независимая атака на последнем кандидате не записана"]
    return [problem for name, block in blocks for problem in block_problems(name, block, rc_tree)]


FROZEN_STAMP = re.compile(r"^> Собрано \S+ по шаблону ([0-9a-f]{10,40})\.", re.MULTILINE)


def is_released(repo: Path, release: str) -> bool:
    index = repo / layout.CATALOG
    versions = (yaml.safe_load(index.read_text(encoding="utf-8")) or {}).get("versions", []) if index.exists() else []
    return any(str(v.get("version")) == release and v.get("state") == "released" for v in versions)


def decision_snapshot_commit(repo: Path, release: str) -> str | None:
    """Template version of the board snapshot the composition decision was taken on.

    Before the release is out it is the live board snapshot. After it the board moves on
    (WP-529 F274: the 16.11 rebuild broke this check), so the witness is the frozen
    candidates page of that release, written from the snapshot at the cut.
    """
    if is_released(repo, release):
        candidates = repo / layout.release_dir(release) / "candidates.md"
        match = FROZEN_STAMP.search(candidates.read_text(encoding="utf-8")) if candidates.exists() else None
        if not match:
            raise DecisionsFormError(f"выпуск {release} вышел, но в его candidates.md нет версии шаблона снимка")
        return match.group(1)
    snapshot_path = repo / layout.SNAPSHOT
    snapshot = yaml.safe_load(snapshot_path.read_text()) if snapshot_path.exists() else {}
    return (snapshot or {}).get("snapshot", {}).get("template_commit")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--release", default=None, help="release number; default — `release` from developer-handoff.yaml")
    parser.add_argument("--require-final", action="store_true", help="before merge: form rows filled and red team verdict recorded")
    parser.add_argument("--rc-tree", default=None, help="tree SHA of the candidate the PR releases (from the next-rc comment)")
    parser.add_argument("--after-release", action="store_true", help="after the release merge: deferred records are back in template main")
    parser.add_argument("--template-changelog", type=Path, default=None, help="CHANGELOG.md of template main, read after the release merge")
    args = parser.parse_args(argv)
    if args.after_release and args.template_changelog is None:
        parser.error("--after-release требует --template-changelog: без журнала основной ветки возврат не проверить")

    try:
        handoff = yaml.safe_load((args.repo / layout.HANDOFF).read_text(encoding="utf-8")) or {}
        release = args.release or str(handoff.get("release") or "")
        decisions = (args.repo / layout.release_dir(release) / "decisions.md").read_text(encoding="utf-8")
        # The handoff lists candidates of one release only. For any other release its keys
        # say nothing about the composition: the row is then checked for being filled
        # (--require-final), not against foreign keys (found 20.11.2026 on 0.42.1, which
        # had no candidate list of its own and failed on "no candidate codes").
        handoff_release = str(handoff.get("release") or "")
        own_candidates = release == handoff_release
        records = (handoff.get("records") or {}) if own_candidates else {}
        problems: list[str] = []
        for key, record in records.items():
            problems += record_problems(key, record or {})
        if own_candidates:
            problems += decision_problems(handoff, decisions, decision_snapshot_commit(args.repo, release))
        unfilled = unfilled_rows(decisions)
        words_only = own_candidates and keys_pending(decisions)
        if args.require_final:
            problems += [f"в decisions.md не заполнена строка «{row}»" for row in unfilled]
            if words_only:
                problems.append(
                    "в строке «Состав: что взято» нет ключей кандидатов U-…: до нарезки состав записан словами, "
                    "перед слиянием нужны ключи или формула «всё до снимка» и версия основной ветки в момент «режем»"
                )
            if not args.rc_tree:
                problems.append("--require-final требует --rc-tree: без дерева кандидата вердикт можно принять за вердикт чужой сборки")
            problems += red_team_problems(args.repo / layout.release_dir(release) / "tests", args.rc_tree)
        if args.after_release:
            changelog = args.template_changelog.read_text(encoding="utf-8")
            if "Unreleased" not in changelog_sections(changelog):
                raise DecisionsFormError(f"в {args.template_changelog} нет раздела «## [Unreleased]» — это не журнал основной ветки шаблона")
            problems += return_problems(decisions, changelog, release)
    except (OSError, yaml.YAMLError, DecisionsFormError) as error:
        print(f"check_decisions: {error}", file=sys.stderr)
        return 2

    for problem in problems:
        print(f"FAIL: {problem}")
    if problems:
        print(f"Выпуск {release}: замечаний {len(problems)} (кандидатов {len(records)})")
        return 1
    print(f"OK: выпуск {release}, кандидатов {len(records)}, замечаний нет")
    if not own_candidates:
        print(f"ЗАМЕТКА: список кандидатов Разработчика ведётся для выпуска {handoff_release}; состав выпуска {release} сверен только на заполненность строки")
    if args.after_release and deferred_without_keys(decisions):
        print("ЗАМЕТКА: отложенное названо словами, без ключей записей U-… — возврат в основную ветку не проверен; "
              "если отложенное было в основной ветке на момент нарезки, назовите его ключи")
    if words_only:
        print("ЗАМЕТКА: состав записан словами, ключи кандидатов Выпускающий называет при нарезке; до этого сверка по ключам "
              "(неизвестные ключи, неразделимые группы) не выполнялась — это не «всё чисто»")
    if unfilled and not args.require_final:
        print(f"ЗАМЕТКА: форма решений заполнена не до конца ({'; '.join(unfilled)}) — это не «всё чисто»; перед слиянием запустить с --require-final")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
