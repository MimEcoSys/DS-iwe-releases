#!/usr/bin/env python3
"""Build the release board from its sources (WP-529).

Reads source snapshots from --src and writes roles/developer.yaml, now/*.md
(current state, rewritten on every run) and releases/<N>/shipped.md into --repo. Every item of every source must land on the board or in an
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


def results_for(sbg: str, goals: dict[int, list[str]]) -> list[dict]:
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


LINK_KINDS = ("result", "proposed", "service")


def check_link(name: str, link: dict, by_code: dict) -> None:
    """A link has exactly one kind, and its result codes are on the board."""
    kinds = [k for k in LINK_KINDS if link.get(k)]
    if len(kinds) != 1:
        raise SystemExit(f"{name}: expected exactly one of {LINK_KINDS}, got {kinds or 'none'}")
    check_codes(name, link, by_code)


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
        check_link(u["key"], u, by_code)
        for code in u.get("result", []):
            by_code[code]["merged_after_0_41_11"] = True
    done_unmerged = {
        r["code"] for r in results if r["status"] == "сделано, не сверено" and not r.get("merged_after_0_41_11")
    }
    check_keys("placement", declared["placement"], done_unmerged)
    for s in testing:
        s["link"] = declared["staging"][s["id"]]
        check_link(s["id"], s["link"], by_code)
        for code in s["link"].get("result", []):
            by_code[code]["on_staging"] = True
    for code, place in declared["placement"].items():
        by_code[code]["status"] = PLACE_TO_STATUS[place["place"]]
        by_code[code]["evidence"] = place["evidence"]
    for r in results:
        # A done result whose records were merged after 0.41.11 and that no release holds yet.
        if r["status"] == "сделано, не сверено" and r.get("merged_after_0_41_11"):
            r["status"] = "готово для передачи"
    for r in results:
        if r["status"] == "план" and (r.get("on_staging") or r.get("merged_after_0_41_11")):
            r["mismatch"] = "расходится: в карточке «план», но часть уже на обкатке или влита в шаблон"
    left = [r["code"] for r in results if r["status"] == "сделано, не сверено"]
    if left:
        raise SystemExit(f"done results without placement: {left}")


RELEASED_KINDS = (
    "result_by_ref",
    "no_rp",
    "rp_no_board_results",
    "result_by_reading",
    "contested",
    "service",
    "none",
)
WP_NUMBER = re.compile(r"(?:WP|РП)-?\s?(\d{1,3})(?!\d)")
REF_FORMAT = re.compile(r"[0-9a-f]{7,40}|#\d+")
RELEASED_FIELDS = {
    "result_by_ref": {"code", "ref"},
    "result_by_reading": {"code"},
    "contested": {"readings"},
}
READING_WORDS = ("none", "service")


def check_released_fields(key: str, link: dict) -> None:
    required = RELEASED_FIELDS.get(link["kind"], set())
    present = set(link) - {"kind", "commit_wp"}
    if present != required:
        raise SystemExit(f"{key}: kind {link['kind']} needs fields {sorted(required)}, got {sorted(present)}")


def contains_ref(text: str, ref: str) -> bool:
    """The reference stands in the text as a whole token, not as a prefix of a longer number or hash."""
    return re.search(re.escape(ref) + r"(?![\w])", text) is not None


def released_kind_expected(entry: dict, link: dict, candidates: set) -> str | None:
    """The kind the mechanical rules force for this record, or None when it is the readers' call."""
    if link["kind"] == "result_by_ref":
        return None
    if not entry["wp"]:
        return "no_rp"
    if not candidates:
        return "rp_no_board_results"
    return None


def apply_released_links(results: list[dict], released_041: dict, unreleased_keys: set, declared: dict, placement: dict) -> dict:
    """Check the links of records released in 0.37-0.41.11 and mark the results they serve (WP-529 F255).

    The universe is the set of distinct record keys; repeated records (same text in two versions)
    share one key and are counted once. Returns the count of each kind.
    """
    entries: dict[str, dict] = {}
    for ver, items in released_041.items():
        for e in items:
            entries.setdefault(e["key"], {"text": e["text"], "versions": []})["versions"].append(ver)
    check_keys("released_0_41_11", declared, set(entries))
    overlap = set(entries) & unreleased_keys
    if overlap:
        raise SystemExit(f"released_0_41_11: keys also in Unreleased: {sorted(overlap)}")

    by_code = {r["code"]: r for r in results}
    counts = dict.fromkeys(RELEASED_KINDS, 0)
    for key, link in declared.items():
        kind = link.get("kind")
        if kind not in RELEASED_KINDS:
            raise SystemExit(f"{key}: unknown kind {kind!r}")
        check_released_fields(key, link)
        entry = entries[key]
        wps = {int(n) for n in WP_NUMBER.findall(entry["text"])} | set(link.get("commit_wp", []))
        entry["wp"] = wps
        candidates = {r["code"] for r in results if wps & {int(w[3:]) for w in r["works"]}}
        expected = released_kind_expected(entry, link, candidates)
        if expected and kind != expected:
            raise SystemExit(f"{key}: kind {kind} contradicts the record, expected {expected}")
        if not expected and kind in ("no_rp", "rp_no_board_results"):
            raise SystemExit(f"{key}: kind {kind} but the record has a work number with results on the board")
        if kind == "result_by_ref":
            place = placement.get(link["code"], {})
            if place.get("place") != "released-0.37-0.41.11":
                raise SystemExit(f"{key}: {link['code']} is not placed in released-0.37-0.41.11")
            if not REF_FORMAT.fullmatch(link["ref"]):
                raise SystemExit(f"{key}: ref {link['ref']!r} must be a commit hash of 7+ characters or #number")
            if not (contains_ref(entry["text"], link["ref"]) and contains_ref(place["evidence"], link["ref"])):
                raise SystemExit(f"{key}: ref {link['ref']} must appear in the record and in the placement evidence")
        if kind == "result_by_reading" and link["code"] not in candidates:
            raise SystemExit(f"{key}: {link['code']} is not a result of the record's work {sorted(wps)}")
        if kind == "contested":
            readings = link["readings"]
            if len(set(readings.values())) < 2:
                raise SystemExit(f"{key}: contested but the readings agree")
            wrong = [v for v in readings.values() if v not in READING_WORDS and v not in candidates]
            if wrong:
                raise SystemExit(f"{key}: readings {wrong} are not results of the record's work {sorted(wps)}")
        if kind in ("result_by_ref", "result_by_reading"):
            by_code[link["code"]].setdefault("released_041_records", []).append(key)
        counts[kind] += 1
    if sum(counts.values()) != len(entries):
        raise SystemExit("released_0_41_11: kinds do not add up to the number of records")
    # Links are preliminary until the Developer accepts them, so only a "plan" result is flagged;
    # results already placed (for example in 0.36) are not touched.
    for r in results:
        if r.get("released_041_records") and r["status"] == "план" and not r.get("mismatch"):
            r["mismatch"] = "расходится: в карточке «план», но часть уже вышла в 0.37–0.41.11"
    counts["records"] = len(entries)
    counts["repeated"] = sum(len(e["versions"]) - 1 for e in entries.values())
    return counts


# Board rows: (row name, list file or None for a sum row, statuses). Bold rows are the four stages.
STAGES = (
    ("**1. План**", "1-plan.md", ("план",)),
    (
        "**2. В работе**",
        None,
        ("в работе", "возвращено из 0.42", "у автора", "в разнице 0.36–0.41.11", "готово для передачи", "взято в 0.42"),
    ),
    ("2.1 Разрабатывается", "2.1-in-work.md", ("в работе", "возвращено из 0.42")),
    ("2.2 Проверяется Разработчиком", "2.2-at-developer.md", ("у автора",)),
    ("2.3 Готово для передачи Выпускающему", None, ("в разнице 0.36–0.41.11", "готово для передачи")),
    ("2.3.1 Вышло в 0.37–0.41.11", "2.3.1-released-0.37-0.41.11.md", ("в разнице 0.36–0.41.11",)),
    ("2.3.2 Влито после 0.41.11", "2.3.2-merged-after-0.41.11.md", ("готово для передачи",)),
    ("2.4 Взято Выпускающим", "2.4-taken.md", ("взято в 0.42",)),
    ("**3. Сделано**", "3-done.md", ("выпущено в 0.36",)),
    ("**4. Отложено**", "4-deferred.md", ("отложено",)),
)
OUTSIDE = ("Вне выпуска шаблона", "outside-template.md", ("работает вне выпуска шаблона",))


def record_split(links: list[dict]) -> str:
    existing = {code for link in links for code in link.get("result", [])}
    proposed = {link["proposed"]["what"] for link in links if link.get("proposed")}
    service = sum(1 for link in links if link.get("service"))
    with_existing = sum(1 for link in links if link.get("result"))
    return (
        f"{with_existing} из них служат {len(existing)} уже записанным результатам, "
        f"{len(links) - with_existing - service} — {len(proposed)} новым предложенным результатам "
        f"([список](proposed.md)), {service} — служебные правки без видимого результата"
    )


def stage_notes(results, staging, unreleased_links, released, released_counts) -> dict[str, tuple[str, str]]:
    """Per board row: a one-line note for the board and a fuller explanation for the list page."""
    in_work = [r for r in results if r["status"] == "в работе"]
    testing = [s for s in staging if s["staging_status"] == "testing"]
    plan_mismatch = sum(1 for r in results if r["status"] == "план" and r.get("mismatch"))
    released_part = sum(1 for r in in_work if r.get("released_041_records"))
    merged_part = sum(1 for r in in_work if r.get("merged_after_0_41_11"))
    staging_part = sum(1 for r in in_work if r.get("on_staging"))
    rec_036 = sum(len(e) for e in released["0.36"].values())
    rec_041 = sum(len(e) for e in released["0.41.11"].values())
    c = released_counts
    linked_041 = {r["code"] for r in results if r.get("released_041_records")}
    plan = "работа не начата" + (f"; у {plan_mismatch} — расходится" if plan_mismatch else "")
    in_work_note = (
        f"у {released_part} часть правок уже вышла в 0.37–0.41.11, у {merged_part} — влита после 0.41.11, "
        f"у {staging_part} — на обкатке; остальное ещё в разработке"
    )
    return {
        "**1. План**": (
            plan,
            "Результаты активных РП, работа по которым не начата."
            + (
                f" У {plan_mismatch} — расходится: часть их правок уже на обкатке, влита или вышла."
                if plan_mismatch
                else ""
            ),
        ),
        "**2. В работе**": ("сумма 2.1–2.4", ""),
        "2.1 Разрабатывается": (
            in_work_note,
            f"В плане недели — {sum(1 for r in in_work if r['in_week_plan'])}. Результат складывается из нескольких "
            f"правок: {in_work_note}. Поэтому результат целиком остаётся здесь, а не в 2.2 или 2.3.",
        ),
        "2.2 Проверяется Разработчиком": (
            "работают только в IWE Разработчика",
            f"Сделаны и работают только в IWE Разработчика. На обкатке {len(testing)} записей: "
            f"{record_split([s['link'] for s in testing])}.",
        ),
        "2.3 Готово для передачи Выпускающему": ("сумма 2.3.1 и 2.3.2; отсюда Выпускающий берёт в выпуск", ""),
        "2.3.1 Вышло в 0.37–0.41.11": (
            "вышло пользователям после 0.36; Выпускающий решает, что принять в 0.42",
            f"Вышло в выпусках 0.37–0.41.11 ([состав](../../releases/0.41.11/shipped.md)): {rec_041} строк, "
            f"{c['records']} разных записей ({c['repeated']} повторяются в двух версиях). Связь записей с "
            f"результатами предварительная, до приёмки Разработчиком: по номеру коммита или запроса на слияние — "
            f"{c['result_by_ref']}, по совпавшему чтению двух разметчиков — {c['result_by_reading']}; они служат "
            f"{len(linked_041)} результатам. Разметчики разошлись — {c['contested']}; у РП нет "
            f"единственного подходящего результата — {c['none']}; служебные — {c['service']}; у РП записи нет "
            f"результатов на табло — {c['rp_no_board_results']}; без номера РП — {c['no_rp']}.",
        ),
        "2.3.2 Влито после 0.41.11": (
            "влито в шаблон после 0.41.11, ещё не выпущено",
            f"Сделано целиком и влито в шаблон после 0.41.11, но ещё не выпущено. Всего {len(unreleased_links)} "
            f"записей: {record_split(unreleased_links)}.",
        ),
        "2.4 Взято Выпускающим": ("отобрано Выпускающим в 0.42", "Отобрано Выпускающим в выпуск 0.42."),
        "**3. Сделано**": (
            "вышло в стабильном 0.36; пока только результаты открытых РП",
            f"Вышло в выпусках до 0.36 включительно ([состав](../../releases/0.36/shipped.md), {rec_036} записей). "
            "С результатами пока связаны только сделанные результаты открытых РП; результаты закрытых работ — "
            "следующая очередь.",
        ),
        "**4. Отложено**": ("отложил Разработчик", "Разработчик отложил работу: в карточке РП фаза перенесена на потом."),
        OUTSIDE[0]: (
            "сделано в сервисах платформы; в итог не входит",
            "Результат той же цели сделан не в шаблоне, а в сервисе платформы (сайт, бот, MCP-сервер). Через выпуск "
            "шаблона он не проходит, поэтому в «Итого по IWE» не входит.",
        ),
    }


def count_statuses(results, statuses) -> int:
    return sum(1 for r in results if r["status"] in statuses)


def board_lines(stamp, results, notes, proposed_count) -> list[str]:
    """The board page: numbers only, each linked to its list."""
    on_board = len(results) - count_statuses(results, OUTSIDE[2])
    stages = [count_statuses(results, st) for name, _, st in STAGES if name.startswith("**")]
    if sum(stages) != on_board:
        raise SystemExit("stages do not add up to the total")
    out = [
        stamp,
        "",
        "# Табло выпуска шаблона IWE",
        "",
        "Единица счёта — обещанный результат. Стадии и статусы описаны в [README](../README.md#стадии-и-статусы); "
        "число ведёт к списку результатов.",
        "",
        "| Стадия | Результатов | Пояснения |",
        "|---|---|---|",
    ]
    for name, page, statuses in STAGES:
        n = count_statuses(results, statuses)
        num = f"[{n}](lists/{page})" if page else str(n)
        out += [f"| {name} | {f'**{num}**' if name.startswith('**') else num} | {notes[name][0]} |"]
    outside_n = count_statuses(results, OUTSIDE[2])
    out += [
        f"| **Итого по IWE** | **{on_board}** | сумма стадий 1–4 |",
        f"| {OUTSIDE[0]} | [{outside_n}](lists/{OUTSIDE[1]}) | {notes[OUTSIDE[0]][0]} |",
        f"| Предложено новых результатов | [{proposed_count}](lists/proposed.md) | ждут кода в «Состоянии по целям»; в итог не входят |",
        "",
        "Что вошло в выпуски: [до 0.36](../releases/0.36/shipped.md), [0.37–0.41.11](../releases/0.41.11/shipped.md). "
        "[Сверка полноты](completeness.md).",
        "",
    ]
    return out


RESULT_HEADER = ["| Код | Часть выпуска | РП | Кто | Что получает | Расхождение |", "|---|---|---|---|---|---|"]


def result_rows(rows: list[dict]) -> list[str]:
    return [
        f"| {r['code']} | {', '.join(r['contours'])} | {', '.join(r['works'])} | {r['who']} | {cell(r['what'])} | {r.get('mismatch', '')} |"
        for r in rows
    ]


RELEASED_LABELS = {
    "no_rp": "без номера РП",
    "rp_no_board_results": "у РП нет результатов на табло",
    "contested": "разметчики разошлись",
    "service": "служебное",
    "none": "нет единственного результата",
}


def released_label(link: dict) -> str:
    if link["kind"] == "result_by_ref":
        return f"{link['code']} (по {link['ref']})"
    if link["kind"] == "result_by_reading":
        return f"{link['code']} (по чтению)"
    return RELEASED_LABELS[link["kind"]]


def link_label(link: dict) -> str:
    if link.get("result"):
        return ", ".join(link["result"])
    if link.get("proposed"):
        return f"новый результат цели {link['proposed']['goal']}"
    if link.get("service"):
        return "служебное"
    return "не привязано"


def stage_extra(page, staging, unreleased, unreleased_links, author_ahead) -> list[str]:
    """Record-level tables that belong to one list page."""
    if page == "2.2-at-developer.md":
        testing = [s for s in staging if s["staging_status"] == "testing"]
        moved = [s for s in staging if s["staging_status"] == "promoted"]
        kept = [s for s in staging if s["staging_status"] == "rejected"]
        out = [
            f"## На обкатке — записи `STAGING.md` Разработчика: {len(testing)}",
            "",
            "| Запись | Что | С | Расхождение |",
            "|---|---|---|---|",
        ]
        out += [f"| {s['id']} | {cell(s['title'])} | {s['date']} | {s.get('mismatch', '')} |" for s in testing]
        out += ["", "## Версия файла у Разработчика опережает шаблон", ""]
        if author_ahead["files"]:
            out += [f"- `{f['path']}`" for f in author_ahead["files"]]
        else:
            out += [f"- {author_ahead.get('note', 'расхождений нет')}"]
        out += [
            "",
            f"## Обкатка завершена: перенесено в шаблон {len(moved)}, остаётся только у Разработчика {len(kept)}",
            "",
            "| Запись | Что | Статус | Расхождение |",
            "|---|---|---|---|",
        ]
        return out + [f"| {s['id']} | {cell(s['title'])} | {s['status']} | {s.get('mismatch', '')} |" for s in moved + kept] + [""]
    if page == "2.3.2-merged-after-0.41.11.md":
        link_of = {u["key"]: link_label(u) for u in unreleased_links}
        out = [
            f"## Записи раздела «Ещё не выпущено»: {len(unreleased)}",
            "",
            "| Ключ | Вид | Что | Код результата |",
            "|---|---|---|---|",
        ]
        return out + [f"| {u['key']} | {u['tag']} | {cell(short(u['text'], 200))} | {link_of[u['key']]} |" for u in unreleased] + [""]
    return []


def write_views(
    repo: Path, stamp: str, results, staging, unreleased, unreleased_links, released, author_ahead, released_links, released_counts
) -> None:
    now = repo / "now"
    lists = now / "lists"
    lists.mkdir(parents=True, exist_ok=True)
    testing = [s for s in staging if s["staging_status"] == "testing"]
    notes = stage_notes(results, staging, unreleased_links, released, released_counts)
    proposed = sorted(
        {
            (link["proposed"]["goal"], link["proposed"]["what"])
            for link in [*unreleased_links, *(s["link"] for s in testing)]
            if link.get("proposed")
        }
    )
    (now / "board.md").write_text("\n".join(board_lines(stamp, results, notes, len(proposed))))

    for name, page, statuses in (*STAGES, OUTSIDE):
        if not page:
            continue
        rows = [r for r in results if r["status"] in statuses]
        title = name.strip("*")
        out = [stamp, "", f"# {title}: {len(rows)}", "", "[← табло](../board.md)", "", notes[name][1], ""]
        out += RESULT_HEADER + result_rows(rows) + [""]
        out += stage_extra(page, staging, unreleased, unreleased_links, author_ahead)
        (lists / page).write_text("\n".join(out))
    out = [
        stamp,
        "",
        f"# Предложено новых результатов: {len(proposed)}",
        "",
        "[← табло](../board.md)",
        "",
        "Записи после 0.41.11 и записи обкатки, для которых результата в «Состоянии по целям» нет. Войдут в итог, "
        "когда документ присвоит им коды.",
        "",
    ]
    (lists / "proposed.md").write_text("\n".join(out + [f"- цель {goal}: {what}" for goal, what in proposed] + [""]))

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
        labels = released_links if name == "0.41.11" else {}
        for ver, entries in versions.items():
            lines += [f"## {ver} — записей: {len(entries)}", ""]
            lines += [
                f"- [{e['tag'] or '—'}] {short(e['text'], 200)}"
                + (f" — **{released_label(labels[e['key']])}**" if e["key"] in labels else "")
                for e in entries
            ]
            lines += [""]
        (repo / "releases" / name / "shipped.md").write_text("\n".join(lines))


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
    links_file = args.repo / "roles" / "developer-links.yaml"
    apply_links(results, developer["unreleased_links"], staging, links_file)
    declared = yaml.safe_load(links_file.read_text())
    released_counts = apply_released_links(
        results,
        released["0.41.11"],
        {u["key"] for u in unreleased},
        declared["released_0_41_11"],
        declared["placement"],
    )
    board = args.repo / "roles"
    board.mkdir(exist_ok=True)
    header = (
        "# Файл Разработчика. Правит только команда iwe-developers через запрос на слияние.\n"
        "# Собрано tools/build_board.py; статусы — заявленные, из карточек работ.\n"
    )
    (board / "developer.yaml").write_text(
        header + yaml.safe_dump(developer, allow_unicode=True, sort_keys=False, width=1000)
    )
    write_views(
        args.repo,
        stamp,
        results,
        staging,
        unreleased,
        developer["unreleased_links"],
        released,
        author_ahead,
        declared["released_0_41_11"],
        released_counts,
    )

    # Completeness: every source item is on the board, linked or explicitly not linked.
    # Each board count is compared with an independent raw count of the source text.
    sbg_total = sum(1 for line in (src / "sbg.md").read_text().splitlines() if re.match(r"^\| Ц\d+-\d+ \|", line))
    platform_built = sum(1 for r in results if r["status"] == "работает вне выпуска шаблона")
    iwe_total = len(results) - platform_built
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
            f"записей обкатки на обкатке — {sum(1 for s in staging if s['staging_status'] == 'testing' and 'link' not in s)} "
            "(у завершённых записей обкатки связь не ведётся)."
        ),
        f"Повторяющиеся номера записей обкатки: {', '.join(duplicates) or 'нет'}.",
        "",
        (
            f"Сверка с «Состоянием по целям»: всего результатов {sbg_total} = на табло IWE {iwe_total} "
            f"+ результаты платформы {sbg_total - iwe_total} (из них {platform_built} — результаты целей табло, "
            "сделанные в сервисах платформы)."
        ),
        "",
    ]
    (args.repo / "now" / "completeness.md").write_text("\n".join(lines))
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
