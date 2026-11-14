#!/usr/bin/env python3
"""Build the release board from its sources (WP-529).

Reads source snapshots from --src and writes ops/snapshot.yaml, BOARD.md, board/*.md
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
  author-ahead.yaml  (optional) author <-> template measurement, written by
                 DS-ai-systems/setup/scripts/wp529-drift-inventory.py --yaml-out
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote, urlsplit

import yaml

from check_decisions import decision_problems, selected_record_keys

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
TEMPLATE_BLOB = "https://github.com/TserenTserenov/FMT-exocortex-template/blob/main/"
ORG_BLOB = "https://github.com/MimEcoSys/{repo}/blob/main/{path}"
LOCAL_LINK = re.compile(r"\]\((?!https?:|#)([^)\s]+)\)")


def table_cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def template_link(match: re.Match) -> str:
    """Changelog links are relative to the template root; ../<repo>/ points to a sibling MimEcoSys repo."""
    target = match.group(1)
    if target.startswith("../"):
        repo, path = target[3:].split("/", 1)
        return f"]({ORG_BLOB.format(repo=repo, path=path)})"
    return f"]({TEMPLATE_BLOB}{target})"


def short(text: str, limit: int = 160) -> str:
    text = re.sub(r"\s+", " ", text.replace("**", "")).strip()
    text = LOCAL_LINK.sub(template_link, text)
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


AUTHOR_AHEAD_CATEGORIES = {
    # category of wp529-drift-inventory.py -> (group on the 2.2 page, what it means)
    "would_update": ("sync", "синхронизация перенесёт версию Разработчика в шаблон"),
    "template_has_foreign_edits": ("both", "в шаблоне есть свои правки; нужна сверка версий"),
    "accepted_base_unproven": ("unproven", "принятая версия не прошла проверку перед доставкой"),
}
AUTHOR_AHEAD_GROUPS = (
    ("sync", "Уйдёт в шаблон при синхронизации"),
    ("both", "Расходится с шаблоном — сверить вручную"),
    ("unproven", "Не доказано — нужна проверка Разработчика"),
)
AUTHOR_AHEAD_HEADING = "## Версия файла у Разработчика отличается от шаблона"
REQUIRED_MEASUREMENT_FIELDS = ("measured_at", "template_commit", "duration_s", "complete", "incomplete_reasons", "files")


def load_author_ahead(path: Path) -> dict:
    """The author <-> template measurement; a missing file differs from a broken one.

    The measurement runs on the Developer's host (it compares the Developer's IWE
    with the template), so the Developer puts its YAML into --src. Missing file:
    the 2.2 page says so. Broken file: the run stops, so a damaged measurement is
    never shown as a current one.
    """
    if not path.exists():
        return {"present": False, "files": []}
    doc = yaml.safe_load(path.read_text())
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        raise SystemExit(f"{path.name}: expected schema_version 1")
    missing = [k for k in REQUIRED_MEASUREMENT_FIELDS if k not in doc]
    if missing:
        raise SystemExit(f"{path.name}: missing {missing}")
    if not isinstance(doc["complete"], bool) or not isinstance(doc["files"], list):
        raise SystemExit(f"{path.name}: complete must be true/false and files a list")
    if doc["complete"] and (doc["incomplete_reasons"] or not doc["template_commit"]):
        raise SystemExit(f"{path.name}: complete measurement needs template_commit and no incomplete_reasons")
    seen = set()
    for f in doc["files"]:
        if not isinstance(f, dict) or not isinstance(f.get("path"), str):
            raise SystemExit(f"{path.name}: file entry {f!r} needs a path")
        if "|" in f["path"] or "`" in f["path"]:
            raise SystemExit(f"{path.name}: {f['path']}: path with | or ` breaks the board table")
        if f.get("category") not in AUTHOR_AHEAD_CATEGORIES:
            raise SystemExit(f"{path.name}: {f.get('path')}: unknown category {f.get('category')!r}")
        if f["path"] in seen:
            raise SystemExit(f"{path.name}: {f['path']} listed twice")
        seen.add(f["path"])
    if not doc["complete"] and not doc.get("incomplete_reasons"):
        raise SystemExit(f"{path.name}: incomplete measurement without incomplete_reasons")
    return {"present": True, **doc}


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


def stage_notes(results, staging, unreleased_links, released, released_counts, taken_records=0) -> dict[str, tuple[str, str]]:
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
            f"Вышло в выпусках 0.37–0.41.11 ([состав](../releases/0.41.11/shipped.md)): {rec_041} строк, "
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
        "2.4 Взято Выпускающим": (
            f"принятых правок: {taken_records}; считаются только готовые результаты с прямой связью"
            if taken_records else "отобрано Выпускающим в 0.42",
            f"Правок в принятом составе: {taken_records}. Здесь только готовые результаты, все связанные правки "
            "которых взяты; частично готовые остаются в 2.1. Готовые результаты без подтверждённой связи "
            "остаются в 2.3.2." if taken_records else "Отобрано Выпускающим в выпуск 0.42.",
        ),
        "**3. Сделано**": (
            "вышло в стабильном 0.36; пока только результаты открытых РП",
            f"Вышло в выпусках до 0.36 включительно ([состав](../releases/0.36/shipped.md), {rec_036} записей). "
            "С результатами пока связаны только сделанные результаты открытых РП; результаты закрытых работ — "
            "следующая очередь.",
        ),
        "**4. Отложено**": ("отложил Разработчик", "Разработчик отложил работу: в карточке РП фаза перенесена на потом."),
        OUTSIDE[0]: (
            "сделано в сервисах платформы; входит в общий итог результатов",
            "Результат той же цели сделан не в шаблоне, а в сервисе платформы (сайт, бот, MCP-сервер). Через выпуск "
            "шаблона он не проходит, поэтому не стоит в стадиях 1–4, но входит в общий итог результатов.",
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
        "Единица счёта — обещанный результат. Стадии и статусы описаны в [README](README.md#стадии-и-статусы); "
        "число ведёт к списку результатов.",
        "",
        "| Стадия | Результатов | Пояснения |",
        "|---|---|---|",
    ]
    for name, page, statuses in STAGES:
        n = count_statuses(results, statuses)
        num = f"[{n}](board/{page})" if page else str(n)
        out += [f"| {name} | {f'**{num}**' if name.startswith('**') else num} | {notes[name][0]} |"]
    outside_n = count_statuses(results, OUTSIDE[2])
    out += [
        f"| **В стадиях 1–4** | **{on_board}** | результаты в стадиях выпуска |",
        "",
        f"**Всего учтённых результатов: {len(results)} = {on_board} в стадиях 1–4 + "
        f"{outside_n} [в сервисах платформы](board/{OUTSIDE[1]}).** "
        "Результаты в сервисах доступны без выпуска шаблона.",
        "",
        f"Отдельно — [предложения новых результатов](board/proposed.md): {proposed_count}. "
        "Им ещё не присвоены коды результатов, поэтому в общий итог они не входят.",
        "",
        "Что вошло в выпуски: [до 0.36](releases/0.36/shipped.md), [0.37–0.41.11](releases/0.41.11/shipped.md). "
        "[Сверка полноты](board/completeness.md).",
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


def author_ahead_lines(author_ahead: dict, fmt_sha: str) -> list[str]:
    """2.2 page block: files whose Developer version differs from the template.

    The files do not move results between stages and are not counted as
    results; each is shown once, with the result the Developer links it to.
    """
    out = ["", AUTHOR_AHEAD_HEADING, ""]
    if not author_ahead["present"]:
        return out + ["Замер расхождений Разработчика и шаблона не приложен к сборке.", ""]
    commit = str(author_ahead["template_commit"] or "—")
    out.append(f"Замер {author_ahead['measured_at']} по шаблону {commit[:10]}, шёл {author_ahead['duration_s']} с.")
    if author_ahead["template_commit"] and not fmt_sha.startswith(commit[:10]):
        out += ["", f"**Замер сделан по другой версии шаблона, чем табло ({fmt_sha[:10]}).**"]
    if not author_ahead["complete"]:
        reasons = "; ".join(author_ahead["incomplete_reasons"])
        return out + ["", f"**Замер неполный, файлы не показаны:** {cell(reasons)}", ""]
    groups = {key: [] for key, _ in AUTHOR_AHEAD_GROUPS}
    for f in author_ahead["files"]:
        groups[AUTHOR_AHEAD_CATEGORIES[f["category"]][0]].append(f)
    for key, title in AUTHOR_AHEAD_GROUPS:
        out += ["", f"### {title}: {len(groups[key])}", ""]
        if groups[key]:
            out += ["| Файл | Что | Результат |", "|---|---|---|"]
            out += [
                f"| `{f['path']}` | {AUTHOR_AHEAD_CATEGORIES[f['category']][1]} | {link_label(f['link'])} |"
                for f in groups[key]
            ]
    return out + [""]


def count_measured_rows(page: str) -> int:
    """File rows actually written under the measurement heading of the 2.2 page."""
    if AUTHOR_AHEAD_HEADING not in page:
        return 0
    block = page.split(AUTHOR_AHEAD_HEADING, 1)[1].split("\n## ", 1)[0]
    return sum(1 for line in block.splitlines() if line.startswith("| `"))


def apply_file_links(author_ahead: dict, declared_files, by_code: dict) -> list[str]:
    """Attach the Developer's file -> result links; return links to files the measurement no longer lists."""
    declared_files = declared_files or {}
    if not isinstance(declared_files, dict):
        raise SystemExit("developer-links.yaml: files must be a mapping path -> link")
    for path, link in declared_files.items():
        check_link(f"files: {path}", link, by_code)
    for f in author_ahead["files"]:
        f["link"] = declared_files.get(f["path"], {})
    if not author_ahead["present"] or not author_ahead["complete"]:
        return []
    measured = {f["path"] for f in author_ahead["files"]}
    return sorted(set(declared_files) - measured)


def stage_extra(page, staging, unreleased, unreleased_links, author_ahead, fmt_sha) -> list[str]:
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
        out += author_ahead_lines(author_ahead, fmt_sha)
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
    repo: Path, stamp: str, results, staging, unreleased, unreleased_links, released, author_ahead, released_links, released_counts,
    fmt_sha: str,
    taken_records: int = 0,
) -> None:
    lists = repo / "board"
    lists.mkdir(parents=True, exist_ok=True)
    testing = [s for s in staging if s["staging_status"] == "testing"]
    notes = stage_notes(results, staging, unreleased_links, released, released_counts, taken_records)
    proposed = sorted(
        {
            (link["proposed"]["goal"], link["proposed"]["what"])
            for link in [*unreleased_links, *(s["link"] for s in testing)]
            if link.get("proposed")
        }
    )
    (repo / "BOARD.md").write_text("\n".join(board_lines(stamp, results, notes, len(proposed))))

    for name, page, statuses in (*STAGES, OUTSIDE):
        if not page:
            continue
        rows = [r for r in results if r["status"] in statuses]
        title = name.strip("*")
        out = [stamp, "", f"# {title}: {len(rows)}", "", "[← табло](../BOARD.md)", "", notes[name][1], ""]
        out += RESULT_HEADER + result_rows(rows) + [""]
        out += stage_extra(page, staging, unreleased, unreleased_links, author_ahead, fmt_sha)
        (lists / page).write_text("\n".join(out))
    out = [
        stamp,
        "",
        f"# Предложено новых результатов: {len(proposed)}",
        "",
        "[← табло](../BOARD.md)",
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


HANDOFF_FIELDS = ("rollback_unit", "commits", "user_gets", "how_to_check", "risk", "recommendation", "depends_on")
RISKS = ("высокий", "средний", "низкий")
RECOMMENDATIONS = ("взять", "отложить", "решить Выпускающему")
SEPARABLE = ("да", "нет")
TAG_LABELS = {"behavior": "поведение", "optional": "по желанию", "security": "безопасность", "docs": "документация"}
ROLLBACK_RULES = [
    "## Как откатывать",
    "",
    "- Откатывают на ветке выпуска **до метки сборки-кандидата**: если ветка изменится после метки, программа выпуска "
    "увидит, что выпускаемое не совпадает с проверенным кандидатом, и остановит выпуск.",
    "- Коммиты одной правки откатывают **от нового к старому** — в том порядке, в каком они указаны ниже; "
    "обратный порядок даёт лишние конфликты.",
    "- Почти каждый откат конфликтует в списке изменений (`CHANGELOG.md`) и в манифесте обновления "
    "(`update-manifest.json`): после отката сведите `CHANGELOG.md` вручную и пересоберите манифест "
    "командой `bash generate-manifest.sh`, иначе проверка шаблона упадёт.",
    "- Ветка выпуска потом вливается в основную ветку, поэтому отложенное исчезнет и оттуда. Чтобы вернуть его "
    "в следующий выпуск, нужно откатить сам откат.",
    "",
]


def first_word(text: str, choices: tuple) -> str:
    """The leading choice of a field like «средний — трогает хуки»; fails on anything outside the closed list."""
    for choice in choices:
        if text.startswith(choice):
            return choice
    raise SystemExit(f"field must start with one of {choices}: {text[:60]!r}")


def handoff_groups(records: dict) -> dict[str, list[str]]:
    """Rollback units shared by several records, in record order."""
    units: dict[str, list[str]] = {}
    for key, rec in records.items():
        units.setdefault(rec["rollback_unit"], []).append(key)
    return {unit: keys for unit, keys in units.items() if len(keys) > 1}


def load_handoff(path: Path, unreleased: list[dict]) -> dict | None:
    """Developer's draft fields for every pending record; None when the file is not there yet."""
    if not path.exists():
        return None
    declared = yaml.safe_load(path.read_text())
    records = declared["records"]
    check_keys("handoff", records, {u["key"] for u in unreleased})
    for key, rec in records.items():
        missing = [f for f in HANDOFF_FIELDS if f not in rec]
        if missing:
            raise SystemExit(f"handoff {key}: missing fields {missing}")
        if not rec["commits"]:
            raise SystemExit(f"handoff {key}: no commits, rollback cannot be built")
        first_word(rec["risk"], RISKS)
        first_word(rec["recommendation"], RECOMMENDATIONS)
        unknown = (set(rec["depends_on"]) | set(rec.get("revert_first", []))) - set(records)
        if unknown:
            raise SystemExit(f"handoff {key}: unknown keys in depends_on or revert_first {sorted(unknown)}")
        one_way = [k for k in rec["depends_on"] if key not in records[k]["depends_on"]]
        if one_way:
            raise SystemExit(f"handoff {key}: depends_on must be mutual, missing back-links from {one_way}")
    groups = handoff_groups(records)
    check_keys("handoff groups", declared["groups"], set(groups))
    for unit, keys in groups.items():
        separable = declared["groups"][unit]["separable"]
        if separable not in SEPARABLE:
            raise SystemExit(f"handoff group {unit}: separable must be one of {SEPARABLE}")
        choices = {first_word(records[k]["recommendation"], RECOMMENDATIONS) for k in keys}
        if separable == "нет" and len(choices) > 1:
            raise SystemExit(f"handoff group {unit} is not separable but has different recommendations {sorted(choices)}")
    return declared


def rollback_text(key: str, rec: dict, groups: dict, group_info: dict) -> str:
    """How to undo one record, built from its rollback unit and commits."""
    unit = rec["rollback_unit"]
    sha = unit.split()[0]
    others = [k for k in groups.get(unit, []) if k != key]
    if others and group_info[unit]["separable"] == "да":
        text = f"`git revert --no-edit {' '.join(rec['commits'])}` — только коммиты этой правки"
    elif "(прямой коммит)" in unit:
        text = f"`git revert --no-edit {sha}`"
    else:
        text = f"`git revert --no-edit -m 1 {sha}` — всё слияние {unit}"
        if others:
            text += f"; вместе с ним снимаются {', '.join(f'[{k}](#{k.lower()})' for k in others)}"
    if rec.get("revert_first"):
        text = f"сначала откатить {', '.join(f'[{k}](#{k.lower()})' for k in rec['revert_first'])}, затем " + text
    if rec.get("off_switch"):
        text += f". Без отката: {rec['off_switch']}"
    return text


def write_candidates(repo: Path, stamp: str, handoff: dict, unreleased: list[dict], unreleased_links: list[dict]) -> None:
    """Release-lead brief: every pending record with its four fields and the Developer's recommendation."""
    release = handoff["release"]
    records = handoff["records"]
    group_info = handoff["groups"]
    link_of = {u["key"]: link_label(u) for u in unreleased_links}
    risk = {k: first_word(r["risk"], RISKS) for k, r in records.items()}
    rec = {k: first_word(r["recommendation"], RECOMMENDATIONS) for k, r in records.items()}
    order = sorted(unreleased, key=lambda u: (RECOMMENDATIONS.index(rec[u["key"]]), RISKS.index(risk[u["key"]])))
    groups = handoff_groups({u["key"]: records[u["key"]] for u in order})
    by_tag = {t: sum(1 for u in unreleased if u["tag"] == t) for t in TAG_LABELS}
    out = [
        stamp,
        "",
        f"# Выпуск {release}: что можно взять",
        "",
        "Собрано программой из файла Разработчика (`ops/developer-handoff.yaml`); руками не править. "
        "Решения Выпускающего — в [decisions.md](decisions.md), порядок чтения и словарь — в [README](README.md).",
        "",
        f"**Кандидатов — {len(unreleased)}** правок, влитых в шаблон после 0.41.11: "
        + ", ".join(f"{TAG_LABELS[t]} — {n}" for t, n in by_tag.items() if n)
        + ".",
        "",
        "| Рекомендация Разработчика | высокий риск | средний | низкий | всего |",
        "|---|---|---|---|---|",
    ]
    for choice in RECOMMENDATIONS:
        row = [sum(1 for k in records if rec[k] == choice and risk[k] == r) for r in RISKS]
        out += [f"| {choice} | " + " | ".join(map(str, row)) + f" | {sum(row)} |"]
    out += [
        "",
        "## Все кандидаты",
        "",
        "Сначала «взять», потом «отложить», потом «решить Выпускающему»; внутри — от высокого риска к низкому.",
        "",
        "| Ключ | Вид | Что получит пользователь | Результат | Риск | Рекомендация |",
        "|---|---|---|---|---|---|",
    ]
    out += [
        f"| [{u['key']}](#{u['key'].lower()}) | {TAG_LABELS[u['tag']]} | {cell(records[u['key']]['user_gets'])} "
        f"| {link_of[u['key']]} | {risk[u['key']]} | {rec[u['key']]} |"
        for u in order
    ]
    out += [
        "",
        "## Группы: несколько правок в одном слиянии",
        "",
        "Неразделимую группу берут или откладывают целиком: решение одно на все её записи.",
        "",
        "| Слияние | Записи | Можно снять одну | Почему |",
        "|---|---|---|---|",
    ]
    out += [
        f"| {unit} | {', '.join(f'[{k}](#{k.lower()})' for k in keys)} | {group_info[unit]['separable']} "
        f"| {group_info[unit]['note']} |"
        for unit, keys in groups.items()
    ]
    out += [""] + ROLLBACK_RULES + ["## По каждому кандидату", ""]
    for u in order:
        r = records[u["key"]]
        out += [
            f"### {u['key']}",
            "",
            f"**{TAG_LABELS[u['tag']]}** · результат: {link_of[u['key']]} · слияние: {r['rollback_unit']}",
            "",
            f"> {short(u['text'], 400)}",
            "",
            f"- **Что получит пользователь:** {r['user_gets']}",
            f"- **Как проверить:** {r['how_to_check']}",
            f"- **Как откатить:** {rollback_text(u['key'], r, groups, group_info)}",
            f"- **Риск:** {r['risk']}",
            f"- **Рекомендация Разработчика:** {r['recommendation']}",
            f"- **Делит файлы или зависит от:** {', '.join(f'[{k}](#{k.lower()})' for k in r['depends_on']) or 'ни от чего'}",
            "",
        ]
    (repo / "releases" / release / "candidates.md").write_text("\n".join(out))


PUBLIC_START = "<!-- USER-BOARD:START -->"
PUBLIC_END = "<!-- USER-BOARD:END -->"
PUBLIC_GROUPS = ("Вышло и доступно", "В работе", "Рассматриваем", "Приостановлено")
PUBLIC_FIELDS = {
    "code", "show", "title", "updated_at",
    "vote_candidate", "selection_url", "pause_reason", "pause_source_url",
}
PUBLIC_STAGE_GROUPS = {
    "3-done.md": "Вышло и доступно",
    "2.3.1-released-0.37-0.41.11.md": "Вышло и доступно",
    "2.1-in-work.md": "В работе",
    "1-plan.md": "Рассматриваем",
    "4-deferred.md": "Приостановлено",
}


def public_error(message: str) -> None:
    raise SystemExit(f"public_board: {message}")


def public_date(value, name: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        public_error(f"{name}: expected YYYY-MM-DD string")
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError:
        public_error(f"{name}: invalid date")
    if parsed > dt.date.today():
        public_error(f"{name}: future date")
    return value


def public_text(value, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        public_error(f"{name}: expected nonempty text")
    clean = html.escape(" ".join(value.split()))
    return re.sub(r"([\\`*_\[\]{}()|])", r"\\\1", clean)


def public_url(value, name: str) -> str:
    if not isinstance(value, str):
        public_error(f"{name}: expected public GitHub URL")
    url = urlsplit(value)
    if (url.scheme != "https" or url.netloc != "github.com" or url.query
            or not url.path.strip("/") or any(c.isspace() for c in value)):
        public_error(f"{name}: expected public GitHub URL without query or credentials")
    return quote(value, safe="/:#?&=%@+;,~!$'-._")


def public_release(code: str, result: dict, declared: dict) -> str:
    placements = declared.get("placement")
    if not isinstance(placements, dict) or not isinstance(placements.get(code), dict):
        public_error(f"{code}: released result needs a placement mapping")
    placement = placements[code]
    expected = {
        "выпущено в 0.36": "released-0.36",
        "в разнице 0.36–0.41.11": "released-0.37-0.41.11",
    }[result["status"]]
    version = placement.get("version")
    if (placement.get("place") != expected or not isinstance(version, str)
            or not re.fullmatch(r"\d+\.\d+\.\d+", version)
            or not placement.get("evidence") or not result.get("evidence")):
        public_error(f"{code}: released result needs matching stable placement and evidence")
    key = version_key(version)
    if ((expected == "released-0.36" and key > (0, 36, 99))
            or (expected == "released-0.37-0.41.11" and not (0, 36, 99) < key <= (0, 41, 11))):
        public_error(f"{code}: version is outside the released range")
    if placement["evidence"] != result["evidence"]:
        public_error(f"{code}: release evidence differs between placement and snapshot")
    return version


def public_row(entry: dict, result: dict, declared: dict) -> dict:
    code = entry["code"]
    if result.get("mismatch"):
        public_error(f"{code}: source has an unresolved mismatch")
    status = result.get("status")
    page = next((page for _, page, states in STAGES if page in PUBLIC_STAGE_GROUPS and status in states), None)
    if page is None:
        public_error(f"{code}: status is not eligible for the public board: {status}")
    group = PUBLIC_STAGE_GROUPS[page]
    row = {
        "code": code,
        "group": group,
        "title": public_text(entry.get("title"), f"{code}.title"),
        "updated_at": public_date(entry.get("updated_at"), f"{code}.updated_at"),
        "source_url": f"board/{page}",
        "detail": "",
    }
    vote = entry.get("vote_candidate", False)
    if type(vote) is not bool:
        public_error(f"{code}.vote_candidate: expected boolean")
    if vote and status != "план":
        public_error(f"{code}: only planned results can be vote candidates")
    if status == "план":
        if not vote:
            public_error(f"{code}: planned result has not been selected for voting")
        selection = public_url(entry.get("selection_url"), f"{code}.selection_url")
        row["detail"] = f"[Отобрано для обсуждения]({selection}); выпуск не назначен"
    if group == "Вышло и доступно":
        row["detail"] = f"Доступно с {public_release(code, result, declared)}"
    pause = entry.get("pause_reason")
    if pause is not None or status == "отложено":
        if status not in ("в работе", "возвращено из 0.42", "отложено"):
            public_error(f"{code}: pause cannot override this source status")
        reason = public_text(pause, f"{code}.pause_reason")
        source = public_url(entry.get("pause_source_url"), f"{code}.pause_source_url")
        row.update(group="Приостановлено", detail=f"{reason} ([почему]({source}))")
    return row


def public_rows(snapshot: dict, declared: dict) -> tuple[str, list[dict]]:
    config = declared.get("public_board")
    if (not isinstance(config, dict) or set(config) != {"schema_version", "entries"}
            or type(config["schema_version"]) is not int or config["schema_version"] != 1):
        public_error("expected schema_version 1 and entries")
    entries = config["entries"]
    if not isinstance(entries, list):
        public_error("entries must be a list")
    header = snapshot.get("snapshot")
    if not isinstance(header, dict):
        public_error("snapshot metadata must be a mapping")
    collected = public_date(header.get("collected_at"), "snapshot.collected_at")
    results = snapshot.get("results")
    if not isinstance(results, list):
        public_error("snapshot.results must be a list")
    by_code = {}
    for result in results:
        if not isinstance(result, dict) or not isinstance(result.get("code"), str):
            public_error("source result needs a code")
        code = result["code"]
        if not re.fullmatch(r"Ц\d+-\d+", code):
            public_error(f"invalid source code: {code}")
        if code in by_code:
            public_error(f"duplicate source code: {code}")
        by_code[code] = result
    seen, rows = set(), []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) - PUBLIC_FIELDS:
            public_error("unknown entry fields")
        code = entry.get("code")
        if not isinstance(code, str) or code not in by_code:
            public_error(f"unknown result code: {code}")
        if code in seen:
            public_error(f"duplicate public code: {code}")
        seen.add(code)
        if type(entry.get("show", False)) is not bool:
            public_error(f"{code}.show: expected boolean")
        if entry.get("show", False):
            rows.append(public_row(entry, by_code[code], declared))
    return collected, sorted(rows, key=lambda row: row["code"])


def public_board_lines(snapshot: dict, declared: dict) -> list[str]:
    collected, rows = public_rows(snapshot, declared)
    lines = [
        PUBLIC_START, "## Табло будущих изменений", "",
        "Здесь — выбранные улучшения для пользователей IWE: доступные возможности и дальнейшая работа.", "",
        f"**Состояния по данным на {collected}. После этой даты они могли измениться.** "
        "Дата текста у строки показывает обновление её описания, а не повторную проверку состояния.", "",
        "Работы ниже не обещаны к определённой дате или выпуску. "
        "[Текущая проверка 0.42](releases/0.42/README.md) идёт отдельно. "
        "Голосование пока не запущено; число голосов не подсчитано.", "",
    ]
    for group in PUBLIC_GROUPS:
        lines.extend([f"### {group}", ""])
        selected = [row for row in rows if row["group"] == group]
        if not selected:
            lines.extend(["Пока нет опубликованных записей.", ""])
            continue
        lines.extend(["| Что меняется для вас | Подробности | Дата текста |", "|---|---|---|"])
        for row in selected:
            detail = f"{row['detail']} · " if row["detail"] else ""
            lines.append(f"| {row['title']} | {detail}[{row['code']}]({row['source_url']}) | {row['updated_at']} |")
        lines.append("")
    lines.extend(["Вопрос о записи — [команде выпуска](#роли). [Полное табло](BOARD.md) · [Как устроены состояния](#пользовательский-вид-табло)", "", PUBLIC_END])
    return lines


def read_public_readme(repo: Path) -> str:
    with (repo / "README.md").open(encoding="utf-8", newline="") as stream:
        return stream.read()


def prepare_public_readme(repo: Path, snapshot: dict, declared: dict) -> str:
    block = "\n".join(public_board_lines(snapshot, declared))
    readme = read_public_readme(repo)
    counts = (readme.count(PUBLIC_START), readme.count(PUBLIC_END))
    if counts == (0, 0):
        first, separator, rest = readme.partition("\n")
        if not separator or not first.startswith("# "):
            public_error("README needs a first-level heading before inserting the view")
        return first + "\n\n" + block + "\n" + rest
    if counts != (1, 1) or readme.index(PUBLIC_START) > readme.index(PUBLIC_END):
        public_error("README has missing, duplicate or reversed public markers")
    start = readme.index(PUBLIC_START)
    end = readme.index(PUBLIC_END) + len(PUBLIC_END)
    return readme[:start] + block + readme[end:]


def write_public_readme(repo: Path, text: str) -> None:
    path = repo / "README.md"
    if read_public_readme(repo) == text:
        return
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent, prefix=".user-board-", delete=False) as temporary:
            temp_path = Path(temporary.name)
            temporary.write(text)
            temporary.flush()
            os.fsync(temporary.fileno())
        temp_path.chmod(path.stat().st_mode)
        temp_path.replace(path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def existing_public_readme(repo: Path) -> str:
    snapshot = yaml.safe_load((repo / "ops" / "snapshot.yaml").read_text())
    declared = yaml.safe_load((repo / "ops" / "developer-links.yaml").read_text())
    if not isinstance(snapshot, dict) or not isinstance(declared, dict):
        public_error("snapshot and developer links must be mappings")
    check_public_source_pages(repo, snapshot, declared)
    return prepare_public_readme(repo, snapshot, declared)


def check_public_source_pages(repo: Path, snapshot: dict, declared: dict) -> None:
    _, rows = public_rows(snapshot, declared)
    for row in rows:
        path = repo / row["source_url"]
        if not path.is_file() or not re.search(r"^\| " + re.escape(row["code"]) + r" \|", path.read_text(), re.MULTILINE):
            public_error(f"{row['code']}: missing from source page {row['source_url']}")


def apply_taken_results(results: list[dict], links: list[dict], taken: set[str]) -> None:
    """Move only fully ready results whose every linked record was selected."""
    records_by_code: dict[str, set[str]] = {}
    for link in links:
        for code in link.get("result", []):
            records_by_code.setdefault(code, set()).add(link["key"])
    for result in results:
        if result["status"] != "готово для передачи":
            continue
        linked = records_by_code.get(result["code"], set())
        if linked and linked <= taken:
            result["status"] = "взято в 0.42"
        elif not linked and taken:
            result["mismatch"] = "нет прямой связи результата с принятой записью; сверить код"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--src", type=Path)
    mode.add_argument("--user-board-only", action="store_true")
    mode.add_argument("--check-user-board", action="store_true")
    ap.add_argument("--source-date", help="date when the pinned inputs were collected (YYYY-MM-DD)")
    ap.add_argument("--repo", type=Path, required=True)
    args = ap.parse_args()
    if args.user_board_only or args.check_user_board:
        readme = existing_public_readme(args.repo)
        if args.check_user_board:
            if read_public_readme(args.repo) != readme:
                print("public_board: README is stale; run --user-board-only", file=sys.stderr)
                return 1
        else:
            write_public_readme(args.repo, readme)
        return 0
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
    author_ahead = load_author_ahead(src / "author-ahead.yaml")

    if args.source_date:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.source_date):
            ap.error("--source-date must be YYYY-MM-DD")
        try:
            dt.date.fromisoformat(args.source_date)
        except ValueError:
            ap.error("--source-date is not a calendar date")
    today = args.source_date or dt.date.today().isoformat()
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
        # An incomplete measurement keeps its reasons, not its partial file list.
        "author_ahead": author_ahead if author_ahead.get("complete") else {**author_ahead, "files": []},
        "unreleased_links": [
            {"key": u["key"], "tag": u["tag"], "first_words": short(u["text"], 80)} for u in unreleased
        ],
    }
    links_file = args.repo / "ops" / "developer-links.yaml"
    apply_links(results, developer["unreleased_links"], staging, links_file)
    declared = yaml.safe_load(links_file.read_text())
    stale_file_links = apply_file_links(
        author_ahead, declared.get("files", {}), {r["code"]: r for r in results}
    )
    released_counts = apply_released_links(
        results,
        released["0.41.11"],
        {u["key"] for u in unreleased},
        declared["released_0_41_11"],
        declared["placement"],
    )
    handoff = load_handoff(args.repo / "ops" / "developer-handoff.yaml", unreleased)
    taken_records = 0
    if handoff:
        decisions_path = args.repo / "releases" / str(handoff["release"]) / "decisions.md"
        decisions = decisions_path.read_text()
        problems = decision_problems(handoff, decisions, fmt_sha)
        if problems:
            raise SystemExit("release decisions: " + "; ".join(problems))
        taken, _ = selected_record_keys(handoff, decisions, fmt_sha)
        taken_records = len(taken)
        apply_taken_results(results, developer["unreleased_links"], taken)
    public_readme = (
        prepare_public_readme(args.repo, developer, declared) if "public_board" in declared else None
    )
    ops = args.repo / "ops"
    ops.mkdir(exist_ok=True)
    header = (
        "# Снимок источников: результаты и их заявленные статусы из карточек работ.\n"
        "# Собирает ops/build_board.py при каждом запуске; руками не править.\n"
    )
    (ops / "snapshot.yaml").write_text(
        header + yaml.safe_dump(developer, allow_unicode=True, sort_keys=False, width=1000)
    )
    if handoff:
        write_candidates(args.repo, stamp, handoff, unreleased, developer["unreleased_links"])
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
        fmt_sha,
        taken_records,
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
    if author_ahead["present"] and author_ahead["complete"]:
        page = (args.repo / "board" / "2.2-at-developer.md").read_text()
        checks.append(("Файлы замера Разработчик ↔ шаблон", len(author_ahead["files"]), count_measured_rows(page)))
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
        f"Связи файлов, которых нет в последнем полном замере: {', '.join(stale_file_links) or 'нет'}.",
        "",
        (
            f"Сверка с «Состоянием по целям»: всего результатов {sbg_total} = на табло IWE {iwe_total} "
            f"+ результаты платформы {sbg_total - iwe_total} (из них {platform_built} — результаты целей табло, "
            "сделанные в сервисах платформы)."
        ),
        "",
    ]
    (args.repo / "board" / "completeness.md").write_text("\n".join(lines))
    lost = [name for name, a, b in checks if a != b]
    if lost:
        print("completeness check failed: " + ", ".join(lost), file=sys.stderr)
        return 1
    if public_readme is not None:
        check_public_source_pages(args.repo, developer, declared)
        write_public_readme(args.repo, public_readme)
    print(
        f"goals={len(goals)} results={len(results)} staging={len(staging)} unreleased={len(unreleased)} "
        f"released={on_board_released}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
