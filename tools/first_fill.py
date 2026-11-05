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
  result-codes.md  result code -> work card (RP), working records of document 4
  weekplan.md    the Developer's current week plan
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
OPEN_PLACEMENT = "Open"  # matches Open, Open Aisystant, Open МИМ
OWN_IWE_BLOCK = "И"
LIBRARY_FUNCTION = "Библиотека методов"
CONTOURS = ("шаблон IWE", "Open", "Библиотека методов")
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


def selected_goals(map005: str) -> dict[int, list[str]]:
    """Goal number -> release contours it belongs to, by the board's selection rule."""
    goals: dict[int, list[str]] = {}
    block = ""
    for line in map005.splitlines():
        head = re.match(r"^## (\w)\. ", line)
        if head:
            block = head.group(1)
            continue
        if line.startswith("## "):
            block = ""
        if line.startswith(f"| {LIBRARY_FUNCTION}"):
            for number in re.findall(r"\d+", table_cells(line)[-1]):
                goals.setdefault(int(number), []).append(LIBRARY_FUNCTION)
            continue
        if not re.match(r"^\| *\d+ *\|", line) or not block:
            continue
        cells = table_cells(line)
        placement = cells[-1]
        number = int(cells[0])
        if block == OWN_IWE_BLOCK or any(p in placement for p in TEMPLATE_PLACEMENTS):
            goals.setdefault(number, []).append("шаблон IWE")
        if OPEN_PLACEMENT in placement:
            goals.setdefault(number, []).append("Open")
    if not any(LIBRARY_FUNCTION in c for c in goals.values()):
        raise SystemExit(f"row «{LIBRARY_FUNCTION}» not found in the missing-functions table")
    return {n: sorted(set(c), key=CONTOURS.index) for n, c in goals.items()}


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
                "contours": goals[int(goal)],
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


def attach_works(results: list[dict], result_codes: str, week_plan: str) -> None:
    """Add the work cards (RP) of each result and whether one of them is in the week plan."""
    works = {}
    for line in result_codes.splitlines():
        m = re.match(r"^\| (Ц\d+-\d+) \|.*\| (РП-\d+[^|]*)\|\s*$", line)
        if m:
            works[m.group(1)] = sorted(set(re.findall(r"РП-(\d+)", m.group(2))), key=int)
    in_week = set(re.findall(r"(?:РП-?|WP-)(\d+)", week_plan))
    for r in results:
        if r["code"] not in works:
            raise SystemExit(f"result {r['code']} has no work card in result-codes.md")
        r["works"] = [f"РП-{n}" for n in works[r["code"]]]
        r["in_week_plan"] = bool(set(works[r["code"]]) & in_week)


PLACE_TO_STATUS = {
    "released-0.36": "выпущено в 0.36",
    "released-0.37-0.41.11": "в разнице 0.36–0.41.11",
    "merged-after-0.41.11": "готово для передачи",
    "author-only": "у автора",
    "not-template": "работает вне выпуска шаблона",
}


def check_keys(name: str, declared: dict, expected: set) -> None:
    if set(declared) != expected:
        raise SystemExit(
            f"{name}: missing {sorted(expected - set(declared))}, extra {sorted(set(declared) - expected)}"
        )


def check_codes(name: str, link: dict, by_code: dict) -> None:
    for code in link.get("result", []):
        if code not in by_code:
            raise SystemExit(f"{name}: result {code} is not on the board")


def apply_links(results: list[dict], unreleased_links: list[dict], staging: list[dict], links_file: Path) -> None:
    """Apply the Developer's links: records and staging entries -> results, done results -> where they are."""
    declared = yaml.safe_load(links_file.read_text())
    by_code = {r["code"]: r for r in results}
    check_keys("links", declared["links"], {u["key"] for u in unreleased_links})
    testing = [s for s in staging if s["staging_status"] == "testing"]
    check_keys("staging", declared["staging"], {s["id"] for s in testing})

    for u in unreleased_links:
        u.update(declared["links"][u["key"]])
        check_codes(u["key"], u, by_code)
        for code in u.get("result", []):
            by_code[code]["merged_after_0_41_11"] = True
    done_unmerged = {
        r["code"] for r in results if r["status"] == "сделано, не сверено" and not r.get("merged_after_0_41_11")
    }
    check_keys("placement", declared["placement"], done_unmerged)
    for s in testing:
        s["link"] = declared["staging"][s["id"]]
        check_codes(s["id"], s["link"], by_code)
        for code in s["link"].get("result", []):
            by_code[code]["on_staging"] = True
    for code, place in declared["placement"].items():
        by_code[code]["status"] = PLACE_TO_STATUS[place["place"]]
        by_code[code]["evidence"] = place["evidence"]
    for r in results:
        # A done result whose records were merged after 0.41.11 and that no release holds yet.
        if r["status"] == "сделано, не сверено" and r.get("merged_after_0_41_11"):
            r["status"] = "готово для передачи"
    left = [r["code"] for r in results if r["status"] == "сделано, не сверено"]
    if left:
        raise SystemExit(f"done results without placement: {left}")


def summary_lines(results, staging, unreleased_links, released) -> list[str]:
    """Board summary: four stages; results counted, records shown in brackets for reference."""

    def count(*statuses: str) -> int:
        return sum(1 for r in results if r["status"] in statuses)

    in_work = [r for r in results if r["status"] == "в работе"]
    testing = [s for s in staging if s["staging_status"] == "testing"]
    rec_036 = sum(len(e) for e in released["0.36"].values())
    rec_041 = sum(len(e) for e in released["0.41.11"].values())

    def record_split(links: list[dict]) -> str:
        existing = {code for link in links for code in link.get("result", [])}
        proposed = {link["proposed"]["what"] for link in links if link.get("proposed")}
        service = sum(1 for link in links if link.get("service"))
        with_existing = sum(1 for link in links if link.get("result"))
        return (
            f"{with_existing} из них служат {len(existing)} уже записанным результатам, "
            f"{len(links) - with_existing - service} — {len(proposed)} новым предложенным результатам (список ниже), "
            f"{service} — служебные правки без видимого результата"
        )

    stage2 = (
        "в работе",
        "возвращено из 0.42",
        "у автора",
        "в обкатке",
        "в разнице 0.36–0.41.11",
        "готово для передачи",
        "взято в 0.42",
    )
    stage3 = ("выпущено в 0.36",)
    outside = "работает вне выпуска шаблона"
    on_board = len(results) - count(outside)
    rows = [
        ("**1. План**", count("план"), "результаты активных РП, работа не начата"),
        ("**2. В работе**", count(*stage2), ""),
        (
            "2.1 разрабатывается",
            count("в работе", "возвращено из 0.42"),
            (
                f"в том числе в плане недели — {sum(1 for r in in_work if r['in_week_plan'])}. "
                f"У {sum(1 for r in in_work if r.get('merged_after_0_41_11'))} результатов часть правок уже влита "
                f"после 0.41.11, у {sum(1 for r in in_work if r.get('on_staging'))} часть на обкатке, но целиком "
                "они не готовы — поэтому остаются здесь, а не в 2.2 или 2.3"
            ),
        ),
        (
            "2.2 тестируется Разработчиком",
            count("у автора", "в обкатке"),
            (
                f"сделаны и работают только в IWE Разработчика. На обкатке {len(testing)} записей: "
                f"{record_split([s['link'] for s in testing])}"
            ),
        ),
        (
            "2.3 готово для передачи Выпускающему",
            count("в разнице 0.36–0.41.11", "готово для передачи"),
            "сумма 2.3.1 и 2.3.2",
        ),
        (
            "2.3.1 разница 0.36 и 0.41.11 у Выпускающего (временный пункт до выпуска 0.42)",
            count("в разнице 0.36–0.41.11"),
            (
                f"вышло в выпусках 0.37–0.41.11 ({rec_041} записей); из этого Выпускающий определяет, что взять в "
                "работу. Пока связаны с результатами только сделанные результаты открытых РП (фаза Ф255)"
            ),
        ),
        (
            "2.3.2 вливается Разработчиком после 0.41.11",
            count("готово для передачи"),
            (
                f"результат сделан целиком и влит в шаблон после 0.41.11. Всего {len(unreleased_links)} записей: "
                f"{record_split(unreleased_links)}"
            ),
        ),
        ("2.4 взято Выпускающим в работу", count("взято в 0.42"), "берётся из 2.3"),
        ("**3. Сделано**", count(*stage3), ""),
        (
            "по итогам стабильного выпуска 0.36",
            count("выпущено в 0.36"),
            (
                f"вышло в выпусках до 0.36 включительно ({rec_036} записей); пока связаны с результатами только "
                "сделанные результаты открытых РП (фаза Ф256)"
            ),
        ),
        ("**4. Отложено**", count("отложено"), ""),
        ("**Итого по IWE**", on_board, ""),
        (
            "не входят: сделаны в сервисах платформы",
            count(outside),
            (
                "результаты тех же целей, сделанные на сайте, в боте, на MCP-сервере, в каталоге ChatGPT; "
                "учитываются в результатах платформы"
            ),
        ),
        ("**Всего по этим целям** (= «Состояние по целям»)", len(results), ""),
    ]
    stages = [res for name, res, _ in rows if name.startswith("**") and name[2].isdigit()]
    if sum(stages) != on_board or on_board + count(outside) != len(results):
        raise SystemExit("stages do not add up to the total")
    lines = [
        "## Сводка",
        "",
        (
            "Единица счёта — обещанный результат (код «Ц<цель>-<номер>»). Где результат сейчас, определяют его записи "
            "в списке изменений шаблона: в какой выпуск или ветку они вошли. Число записей указано в пояснениях для "
            "справки; к результатам оно не прибавляется."
        ),
        "",
        "| Стадия | Результатов | Пояснения |",
        "|---|---|---|",
    ]
    lines += [f"| {name} | {f'**{res}**' if name.startswith('**') else res} | {note} |" for name, res, note in rows]
    proposed = sorted(
        {
            (link["proposed"]["goal"], link["proposed"]["what"])
            for link in [*unreleased_links, *(s["link"] for s in testing)]
            if link.get("proposed")
        }
    )
    lines += [
        "",
        (
            f"**Предложено записать в «Состояние по целям» новых результатов: {len(proposed)}** — записи после 0.41.11 "
            "и записи обкатки, для которых результата в документе нет. Войдут в итог, когда документ присвоит им коды:"
        ),
        "",
    ]
    lines += [f"- цель {goal}: {what}" for goal, what in proposed]
    lines += [
        "",
        (
            "**Версия IWE Разработчика (Церен)** = 2.3.2 готовое + выпуск 0.41.11 + 2.2 тестируемое + личное "
            "(то, что в шаблон не идёт)."
        ),
        "",
        "**По частям выпуска** (результат может относиться сразу к двум частям):",
        "",
        "| Стадия | " + " | ".join(CONTOURS) + " |",
        "|---|" + "---|" * len(CONTOURS),
    ]
    for name, statuses in (
        ("1. План", ("план",)),
        ("2. В работе", stage2),
        ("3. Сделано", stage3),
        ("4. Отложено", ("отложено",)),
    ):
        counts = [sum(1 for r in results if r["status"] in statuses and c in r["contours"]) for c in CONTOURS]
        lines += [f"| {name} | " + " | ".join(map(str, counts)) + " |"]
    return lines + [""]


def link_label(link: dict) -> str:
    if link.get("result"):
        return ", ".join(link["result"])
    if link.get("proposed"):
        return f"новый результат цели {link['proposed']['goal']}"
    if link.get("service"):
        return "служебное"
    return "не привязано"


def write_views(repo: Path, stamp: str, results, staging, unreleased, unreleased_links, released, author_ahead) -> None:
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
    out += summary_lines(results, staging, unreleased_links, released)
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
    link_of = {u["key"]: link_label(u) for u in unreleased_links}
    out += [f"| {u['key']} | {u['tag']} | {cell(short(u['text'], 200))} | {link_of[u['key']]} |" for u in unreleased]
    out += ["", "## 3. Результаты по статусам", ""]
    for status in (
        "план",
        "в работе",
        "у автора",
        "готово для передачи",
        "в разнице 0.36–0.41.11",
        "выпущено в 0.36",
        "работает вне выпуска шаблона",
        "отложено",
    ):
        rows = by_status.get(status, [])
        out += [
            f"### {status}: {len(rows)}",
            "",
            "| Код | Часть выпуска | РП | Кто | Что получает |",
            "|---|---|---|---|---|",
        ]
        out += [
            f"| {r['code']} | {', '.join(r['contours'])} | {', '.join(r['works'])} | {r['who']} | {cell(r['what'])} |"
            for r in rows
        ]
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
    attach_works(results, (src / "result-codes.md").read_text(), (src / "weekplan.md").read_text())
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
            "rule": "результаты целей с размещением «шаблон IWE», «Staging» или Open, все цели блока «И. Своя IWE» "
            "и цели функции «Библиотека методов»",
            "goals": sorted(goals),
        },
        "results": results,
        "staging": staging,
        "author_ahead": author_ahead,
        "unreleased_links": [
            {"key": u["key"], "tag": u["tag"], "first_words": short(u["text"], 80)} for u in unreleased
        ],
    }
    apply_links(results, developer["unreleased_links"], staging, args.repo / "board" / "developer-links.yaml")
    board = args.repo / "board"
    board.mkdir(exist_ok=True)
    header = (
        "# Файл Разработчика. Правит только команда iwe-developers через запрос на слияние.\n"
        "# Первое заполнение собрано tools/first_fill.py; статусы — заявленные, из карточек работ.\n"
    )
    (board / "developer.yaml").write_text(
        header + yaml.safe_dump(developer, allow_unicode=True, sort_keys=False, width=1000)
    )
    write_views(args.repo, stamp, results, staging, unreleased, developer["unreleased_links"], released, author_ahead)

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
    unlinked = sum(
        1 for u in developer["unreleased_links"] if not (u.get("result") or u.get("proposed") or u.get("service"))
    )
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
