#!/usr/bin/env python3
"""First fill of the release board from its sources (WP-529 F250).

Reads source snapshots from --src and writes board/developer.yaml and view/*.md
into --repo. Every item of every source must land on the board or in an
explicit "not linked" list; the completeness check fails the run otherwise.

Sources expected in --src:
  map005.md      goals and scenarios (DP.MAP.005, PACK-digital-platform)
  sbg.md         state by goals, results with codes (document 4)
  changelog.md   CHANGELOG.md of FMT-exocortex-template
  staging.md     STAGING.md of the author's IWE
  fmt-sha        commit of FMT main the snapshot was taken at
  fmt-files.txt  file list of FMT main at that commit
"""

import argparse
import datetime as dt
import hashlib
import re
import sys
from pathlib import Path

import yaml

TEMPLATE_PLACEMENTS = ("шаблон IWE", "Staging")
OWN_IWE_BLOCK = "И"
STAGE_TO_STATUS = {
    "план": "план",
    "в работе": "в работе",
    "сделано": "сделано, не сверено",
    "отложено": "отложено",
}
STAGING_TO_STATUS = {
    "testing": "в обкатке",
    "promoted": "перенесено в шаблон",
    "rejected": "остаётся только у автора",
}
PATH_TOKEN = re.compile(r"[\w.\-/]+\.(?:md|sh|py|json|yaml|yml|plist)\b|[\w.\-]+/[\w.\-/]*")
VERSION_HEAD = re.compile(r"^## \[(?P<ver>[^\]]+)\]")


def table_cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def short(text: str, limit: int = 160) -> str:
    text = re.sub(r"\s+", " ", text.replace("**", "")).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(",;:—-") + "…"


def selected_goals(map005: str) -> dict[int, str]:
    """Goal number -> block letter, by the board's selection rule."""
    goals, block = {}, ""
    for line in map005.splitlines():
        head = re.match(r"^## (\w)\. ", line)
        if head:
            block = head.group(1)
            continue
        if line.startswith("## "):
            block = ""
        if not re.match(r"^\| *\d+ *\|", line) or not block:
            continue
        cells = table_cells(line)
        placement = cells[-1]
        if block == OWN_IWE_BLOCK or any(p in placement for p in TEMPLATE_PLACEMENTS):
            goals[int(cells[0])] = block
    return goals


def results_for(sbg: str, goals: dict[int, str]) -> list[dict]:
    rows = []
    for line in sbg.splitlines():
        if not re.match(r"^\| Ц\d+-\d+ \|", line):
            continue
        code, goal, who, what, where, stage = table_cells(line)[:6]
        if int(goal) not in goals:
            continue
        if stage not in STAGE_TO_STATUS:
            raise SystemExit(f"unknown stage {stage!r} in {code}")
        rows.append(
            {
                "code": code,
                "goal": int(goal),
                "who": who,
                "what": short(what),
                "where": where,
                "status": STAGE_TO_STATUS[stage],
                "works": [],
            }
        )
    return rows


def template_matches(file_cell: str, fmt_files: list[str]) -> list[str]:
    """Template paths named by a staging row: exact path, then directory, then file name."""
    found = set()
    for token in PATH_TOKEN.findall(file_cell.replace("`", " ")):
        token = re.sub(r"^(\./|FMT-exocortex-template/)", "", token).rstrip("/.,")
        if not token:
            continue
        exact = [p for p in fmt_files if p == token]
        inside = [p for p in fmt_files if p.startswith(token + "/")]
        by_name = [p for p in fmt_files if p.endswith("/" + token)]
        match = exact or inside[:1] or (by_name if len(by_name) == 1 else [])
        found.update(match)
    return sorted(found)


def staging_entries(staging: str, fmt_files: list[str]) -> list[dict]:
    entries = []
    for line in staging.splitlines():
        if not re.match(r"^\| S-\d+ \|", line):
            continue
        cells = table_cells(line)
        # Rule texts may contain "|"; the status is the first cell with a known value.
        idx = next((i for i, c in enumerate(cells) if i >= 2 and c in STAGING_TO_STATUS), None)
        if idx is None:
            raise SystemExit(f"no known status in staging row {cells[0]}")
        rule = " | ".join(cells[1 : idx - 1])
        file_cell = cells[idx - 1]
        in_template = template_matches(file_cell, fmt_files)
        entry = {
            "id": cells[0],
            "title": short(rule),
            "staging_status": cells[idx],
            "status": STAGING_TO_STATUS[cells[idx]],
            "date": cells[idx + 2] if idx + 2 < len(cells) else "",
            "files_in_template": in_template,
            "result": None,
        }
        if cells[idx] == "testing" and in_template:
            entry["mismatch"] = "сверить: файл уже есть в шаблоне, доставлено ли само изменение — не проверено"
        if cells[idx] == "promoted" and not in_template:
            entry["mismatch"] = "расходится: записано «перенесено», но файла по пути из записи в шаблоне нет"
        entries.append(entry)
    return entries


def version_key(ver: str) -> tuple:
    return tuple(int(p) for p in re.findall(r"\d+", ver))


def changelog_sections(changelog: str) -> dict[str, list[dict]]:
    sections, current, group = {}, None, ""
    for line in changelog.splitlines():
        head = VERSION_HEAD.match(line)
        if head:
            current, group = head.group("ver"), ""
            sections[current] = []
            continue
        if current is None:
            continue
        if line.startswith("### "):
            group = line[4:].strip()
        elif line.startswith("- "):
            text = line[2:].strip()
            tag = re.match(r"^\[(\w[\w-]*)\]\s*", text)
            sections[current].append(
                {
                    "key": "U-" + hashlib.sha1(text[:200].encode()).hexdigest()[:6],
                    "group": group,
                    "tag": tag.group(1) if tag else "",
                    "text": text[tag.end() :] if tag else text,
                }
            )
    return sections


def author_ahead_placeholder() -> dict:
    # The drift inventory (F248) runs on the author's host and is not readable here;
    # the Developer fills this block from its report.
    return {
        "measured_at": None,
        "files": [],
        "note": "замер расхождений автор↔шаблон при первом заполнении не получен (сетевой предел замера); "
        "последнее известное число — 14 файлов (04.11.2026, РП-529 Ф248)",
    }


def cell(text: str) -> str:
    return text.replace("|", "\\|")


def write_views(repo: Path, stamp: str, results, staging, unreleased, released, author_ahead) -> None:
    view = repo / "view"
    view.mkdir(exist_ok=True)
    by_status: dict[str, list] = {}
    for r in results:
        by_status.setdefault(r["status"], []).append(r)

    out = [
        stamp,
        "",
        "# Табло релиза шаблона IWE",
        "",
        "Собрано программой из файлов ролей и источников; вручную не править.",
        "",
    ]
    testing = [s for s in staging if s["staging_status"] == "testing"]
    out += [
        "## 1. Работает в моей IWE, в шаблон не доставлено",
        "",
        f"### 1а. На обкатке — записи `STAGING.md` со статусом testing: {len(testing)}",
        "",
        "| Запись | Что | С | Расхождение |",
        "|---|---|---|---|",
    ]
    out += [f"| {s['id']} | {cell(s['title'])} | {s['date']} | {s.get('mismatch', '')} |" for s in testing]
    out += ["", "### 1б. Моя версия файла впереди шаблона (замер расхождений автор↔шаблон)", ""]
    if author_ahead["files"]:
        out += [f"- `{f['path']}`" for f in author_ahead["files"]]
    else:
        out += [f"- {author_ahead.get('note', 'расхождений нет')}"]
    out += [
        "",
        f"## 2. В шаблоне, ждёт выпуска — раздел «Ещё не выпущено»: {len(unreleased)}",
        "",
        "| Ключ | Вид | Что | Код результата |",
        "|---|---|---|---|",
    ]
    out += [f"| {u['key']} | {u['tag']} | {cell(short(u['text'], 200))} | не привязано |" for u in unreleased]
    out += ["", "## 3. Результаты целей шаблона по статусам", ""]
    for status in ("в работе", "план", "сделано, не сверено", "отложено"):
        rows = by_status.get(status, [])
        out += [f"### {status}: {len(rows)}", "", "| Код | Кто | Что получает |", "|---|---|---|"]
        out += [f"| {r['code']} | {r['who']} | {cell(r['what'])} |" for r in rows]
        out += [""]
    moved = [s for s in staging if s["staging_status"] == "promoted"]
    kept = [s for s in staging if s["staging_status"] == "rejected"]
    out += [
        f"## 4. Обкатка завершена: перенесено в шаблон {len(moved)}, остаётся только у автора {len(kept)}",
        "",
        "| Запись | Что | Статус | Расхождение |",
        "|---|---|---|---|",
    ]
    out += [f"| {s['id']} | {cell(s['title'])} | {s['status']} | {s.get('mismatch', '')} |" for s in moved + kept]
    out += [
        "",
        "## 5. Выпущено",
        "",
        f"- до 0.36 включительно — [release-0.36.md](release-0.36.md), записей: {sum(len(v) for v in released['0.36'].values())}",
        f"- 0.37–0.41.11 — [release-0.41.11.md](release-0.41.11.md), записей: {sum(len(v) for v in released['0.41.11'].values())}",
        "",
    ]
    (view / "board.md").write_text("\n".join(out))

    titles = {"0.36": "Выпуски до 0.36 включительно", "0.41.11": "Выпуски 0.37–0.41.11: что добавилось к 0.36"}
    for name, versions in released.items():
        lines = [
            stamp,
            "",
            f"# {titles[name]}",
            "",
            "Короткая выжимка записей списка изменений шаблона; полный текст — в CHANGELOG.md шаблона.",
            "",
        ]
        for ver, entries in versions.items():
            lines += [f"## {ver} — записей: {len(entries)}", ""]
            lines += [f"- [{e['tag'] or '—'}] {short(e['text'], 200)}" for e in entries]
            lines += [""]
        (view / f"release-{name}.md").write_text("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--repo", type=Path, required=True)
    args = ap.parse_args()
    src = args.src

    fmt_sha = (src / "fmt-sha").read_text().strip()
    fmt_files = (src / "fmt-files.txt").read_text().split()
    goals = selected_goals((src / "map005.md").read_text())
    results = results_for((src / "sbg.md").read_text(), goals)
    staging = staging_entries((src / "staging.md").read_text(), fmt_files)
    sections = changelog_sections((src / "changelog.md").read_text())
    unreleased = sections.pop("Unreleased")
    released = {"0.36": {}, "0.41.11": {}}
    for ver, entries in sections.items():
        key = version_key(ver)
        if key <= (0, 36, 99):
            released["0.36"][ver] = entries
        elif key <= (0, 41, 11):
            released["0.41.11"][ver] = entries
        else:
            raise SystemExit(f"released version {ver} is newer than 0.41.11; extend the board ranges")
    author_ahead = author_ahead_placeholder()

    today = dt.date.today().isoformat()
    stamp = f"> Собрано {today} по шаблону {fmt_sha[:10]}."
    developer = {
        "snapshot": {
            "collected_at": today,
            "template_commit": fmt_sha,
            "rule": "результаты целей с размещением «шаблон IWE» или «Staging» и все цели блока «И. Своя IWE»",
            "goals": sorted(goals),
        },
        "results": results,
        "staging": staging,
        "author_ahead": author_ahead,
        "unreleased_links": [
            {"key": u["key"], "tag": u["tag"], "first_words": short(u["text"], 80), "result": None} for u in unreleased
        ],
    }
    board = args.repo / "board"
    board.mkdir(exist_ok=True)
    header = (
        "# Файл Разработчика. Правит только команда iwe-developers через запрос на слияние.\n"
        "# Первое заполнение собрано tools/first_fill.py; статусы — заявленные, из карточек работ.\n"
    )
    (board / "developer.yaml").write_text(
        header + yaml.safe_dump(developer, allow_unicode=True, sort_keys=False, width=1000)
    )
    write_views(args.repo, stamp, results, staging, unreleased, released, author_ahead)

    # Completeness: every source item is on the board, linked or explicitly not linked.
    # Each board count is compared with an independent raw count of the source text.
    sbg_raw = sum(
        1
        for line in (src / "sbg.md").read_text().splitlines()
        if (m := re.match(r"^\| Ц(\d+)-\d+ \|", line)) and int(m.group(1)) in goals
    )
    staging_raw = sum(1 for line in (src / "staging.md").read_text().splitlines() if line.startswith("| S-"))
    changelog_raw = sum(1 for line in (src / "changelog.md").read_text().splitlines() if line.startswith("- "))
    on_board_released = sum(len(e) for part in released.values() for e in part.values())
    checks = [
        ("Результаты выбранных целей (документ 4)", sbg_raw, len(results)),
        ("Записи обкатки STAGING.md", staging_raw, len(staging)),
        (
            "Все записи списка изменений (ещё не выпущено + выпущено)",
            changelog_raw,
            len(developer["unreleased_links"]) + on_board_released,
        ),
    ]
    staging_ids = [s["id"] for s in staging]
    duplicates = sorted({i for i in staging_ids if staging_ids.count(i) > 1})
    lines = [
        stamp,
        "",
        "# Сверка полноты",
        "",
        "Каждая запись каждого источника есть на табло: строкой или в списке «не привязано».",
        "",
        "| Источник | В источнике | На табло |",
        "|---|---|---|",
    ]
    lines += [f"| {name} | {a} | {b} |" for name, a, b in checks]
    unlinked = sum(1 for u in developer["unreleased_links"] if not u["result"])
    lines += [
        "",
        (
            f"Не привязано к коду результата: записей «Ещё не выпущено» — {unlinked}, "
            f"записей обкатки — {sum(1 for s in staging if not s['result'])}."
        ),
        f"Повторяющиеся номера записей обкатки: {', '.join(duplicates) or 'нет'}.",
        "",
    ]
    (args.repo / "view" / "completeness.md").write_text("\n".join(lines))
    lost = [name for name, a, b in checks if a != b]
    if lost:
        print("completeness check failed: " + ", ".join(lost), file=sys.stderr)
        return 1
    print(
        f"goals={len(goals)} results={len(results)} staging={len(staging)} unreleased={len(unreleased)} "
        f"released={on_board_released}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
