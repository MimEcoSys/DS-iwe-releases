#!/usr/bin/env python3
"""Build the release board from its sources (WP-529).

Reads source snapshots from --src and writes board/snapshot.yaml, board/README.md, board/*.md,
NOW.md (current state, rewritten on every run), releases/<first number>.N/<N>/candidates.md and
releases/<first number>.N/<N>/shipped.md into --repo. Every item of every source must land on the board or in an
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout  # noqa: E402
import iwe_stats  # noqa: E402
import release_catalog  # noqa: E402
from check_decisions import decision_problems, selected_record_keys  # noqa: E402

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
SOURCE_GROUPS = (
    ("1. План", "план"),
    ("2. В работе", "в работе"),
    ("3. Сделано", "сделано"),
    ("4. Отложено", "отложено"),
)
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
        cells = table_cells(line)
        code, goal, who, what, where, stage = cells[:6]
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
                "system": cells[7],
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


# Released ranges of the board: name -> highest version in it. A changelog section newer than the
# last range stops the build until the range is added (WP-529 F274: 0.42 released 16.11.2026;
# F276: 0.42.1 released 20.11.2026 gets its own range, so 0.42.0 and 0.42.1 records are not mixed).
RELEASED_RANGES = {"0.36": (0, 36, 99), "0.41.11": (0, 41, 11), "0.42": (0, 42, 0), "0.42.1": (0, 42, 1)}
RELEASED_TITLES = {
    "0.36": "Выпуски до 0.36 включительно",
    "0.41.11": "Выпуски 0.37–0.41.11: что добавилось к 0.36",
    "0.42": "Выпуск 0.42: что добавилось к 0.41.11",
    "0.42.1": "Выпуск 0.42.1: что добавилось к 0.42",
}
RANGE_PLACES = {
    "0.36": "released-0.36", "0.41.11": "released-0.37-0.41.11", "0.42": "released-0.42", "0.42.1": "released-0.42.1",
}
RELEASED_041 = "выпущено в 0.37–0.41.11"
RELEASED_042 = "выпущено в 0.42"
RELEASED_0421 = "выпущено в 0.42.1"
PLACE_TO_STATUS = {
    "released-0.36": "выпущено в 0.36",
    "released-0.37-0.41.11": RELEASED_041,
    "released-0.42": RELEASED_042,
    "released-0.42.1": RELEASED_0421,
    "author-only": "у автора",
    "not-template": "работает вне выпуска шаблона",
}


def released_range(ver: str) -> str:
    """The board range a released changelog section belongs to."""
    key = version_key(ver)
    for name, limit in RELEASED_RANGES.items():
        if key <= limit:
            return name
    raise SystemExit(f"released version {ver} is newer than {list(RELEASED_RANGES)[-1]}; extend the board ranges")


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


def apply_links(
    results: list[dict], unreleased_links: list[dict], released_042_keys: set, staging: list[dict], links_file: Path,
    released_0421_keys: frozenset = frozenset(),
) -> None:
    """Apply the Developer's links: records and staging entries -> results, done results -> where they are.

    The section released_0_42 links the records of 0.42.0 and 0.42.1 (released_042_keys); the 0.42.1
    ones are released_0421_keys. A done result whose every linked record is out becomes «выпущено в 0.42.1»
    when one of them came out in 0.42.1, «выпущено в 0.42» otherwise; one with a record merged after
    the release is «готово для передачи». Records only reach a result through these links.
    """
    declared = yaml.safe_load(links_file.read_text())
    by_code = {r["code"]: r for r in results}
    check_keys("links", declared["links"], {u["key"] for u in unreleased_links})
    check_keys("released_0_42", declared["released_0_42"], released_042_keys)
    testing = [s for s in staging if s["staging_status"] == "testing"]
    check_keys("staging", declared["staging"], {s["id"] for s in testing})

    for u in unreleased_links:
        u.update(declared["links"][u["key"]])
        check_link(u["key"], u, by_code)
        for code in u.get("result", []):
            by_code[code]["merged_unreleased"] = True
    for key, link in declared["released_0_42"].items():
        check_link(key, link, by_code)
        for code in link.get("result", []):
            by_code[code]["released_042"] = True
            if key in released_0421_keys:
                by_code[code]["released_0421"] = True
    linked = ("merged_unreleased", "released_042")
    done_unmerged = {
        r["code"] for r in results if r["status"] == "сделано, не сверено" and not any(r.get(k) for k in linked)
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
        if r["status"] != "сделано, не сверено":
            continue
        # Done, with a record merged after 0.42 that no release holds yet.
        if r.get("merged_unreleased"):
            r["status"] = "готово для передачи"
        elif r.get("released_042"):
            r["status"] = RELEASED_0421 if r.get("released_0421") else RELEASED_042
    for r in results:
        if r["status"] == "план" and any(r.get(k) for k in ("on_staging", *linked)):
            r["mismatch"] = "расходится: в карточке «план», но часть уже на обкатке, влита в шаблон или вышла"
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
    ("**1. План**", "plan.md", ("план",)),
    (
        "**2. В работе**",
        None,
        ("в работе", "возвращено из 0.42", "у автора", "готово для передачи", "взято в 0.42"),
    ),
    ("2.1 Разрабатывается", "in-work.md", ("в работе", "возвращено из 0.42")),
    ("2.2 Проверяется Разработчиком", "at-developer.md", ("у автора",)),
    ("2.3 Готово для передачи Выпускающему", "ready.md", ("готово для передачи",)),
    ("2.4 Взято Выпускающим", "taken.md", ("взято в 0.42",)),
    ("**3. Сделано**", "done.md", ("выпущено в 0.36", RELEASED_041, RELEASED_042, RELEASED_0421)),
    ("**4. Отложено**", "deferred.md", ("отложено",)),
)
OUTSIDE = ("Вне выпуска шаблона", "outside-template.md", ("работает вне выпуска шаблона",))
# Lists inside «Сделано», like OUTSIDE; the frozen releases/0.N/0.42/README.md and
# releases/index.yaml link to the 0.37-0.41.11 page.
RELEASED_PAGES = (
    ("Вышло в 0.37–0.41.11", "released-0.37-0.41.11.md", (RELEASED_041,)),
    ("Вышло в 0.42", "released-0.42.md", (RELEASED_042,)),
    ("Вышло в 0.42.1", "released-0.42.1.md", (RELEASED_0421,)),
)
DONE_SUBSETS = (OUTSIDE, *RELEASED_PAGES)
WORK_STAGES = tuple(row for row in STAGES if row[0].startswith(("2.1 ", "2.2 ", "2.3 ", "2.4 ")))
STATUS_TO_STAGE = {
    status: stage
    for label, stage in SOURCE_GROUPS
    for name, _, statuses in STAGES if name == f"**{label}**"
    for status in statuses
}
STATUS_TO_STAGE.update({"сделано": "сделано", "работает вне выпуска шаблона": "сделано"})


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


def stage_notes(results, released, released_counts, taken_records=0, released_042_links=None) -> dict[str, tuple[str, str]]:
    """Per board row: a one-line note for the board and a fuller explanation for the list page."""
    in_work = [r for r in results if r["status"] == "в работе"]
    plan_mismatch = sum(1 for r in results if r["status"] == "план" and r.get("mismatch"))
    released_part = sum(1 for r in in_work if r.get("released_041_records") or r.get("released_042"))
    merged_part = sum(1 for r in in_work if r.get("merged_unreleased"))
    staging_part = sum(1 for r in in_work if r.get("on_staging"))
    rec_041 = sum(len(e) for e in released["0.41.11"].values())
    rec_042 = sum(len(e) for e in released["0.42"].values())
    # Per record, like the journal count: a text repeated inside 0.42.1 is two records with one key.
    links_0421 = [(released_042_links or {}).get(e["key"], {}) for entries in released["0.42.1"].values() for e in entries]
    rec_0421 = len(links_0421)
    kinds_0421 = {kind: sum(1 for link in links_0421 if link.get(kind)) for kind in LINK_KINDS}
    c = released_counts
    linked_041 = {r["code"] for r in results if r.get("released_041_records")}
    plan = "работа не начата" + (f"; у {plan_mismatch} — расходится" if plan_mismatch else "")
    in_work_note = (
        f"у {released_part} часть правок уже вышла (0.37–0.42.1), у {merged_part} — влита после 0.42, "
        f"у {staging_part} — на обкатке; остальное ещё в разработке"
    )
    return {
        "**1. План**": (
            plan,
            "Все результаты со стадией «план», независимо от направления и системы."
            + (
                f" У {plan_mismatch} — расходится: часть их правок уже на обкатке, влита или вышла."
                if plan_mismatch
                else ""
            ),
        ),
        "**2. В работе**": ("сумма 2.1–2.4", ""),
        "2.1 Разрабатывается": (
            in_work_note,
            f"Здесь все результаты со стадией «в работе» без подтверждённого перехода на 2.2–2.4. "
            f"По результатам с подробным учётом выпуска: в плане недели — {sum(1 for r in in_work if r['in_week_plan'])}. "
            f"Результат достигается несколькими "
            f"правками: {in_work_note}. Поэтому результат целиком остаётся здесь, а не в 2.2 или 2.3.",
        ),
        "2.2 Проверяется Разработчиком": (
            "работают только в IWE Разработчика",
            "Сделаны и работают только в IWE Разработчика; ещё проверяются перед передачей. "
            "Первый опрос запланирован по всем результатам этого этапа: выбрать кандидатов для перехода в 2.3. "
            "Опрос ещё не запущен; голоса помогают выбрать, готовность подтверждается отдельно. "
            "Также предусмотрены опросы для переходов 1 → 2.1 и 2.1 → 2.2.",
        ),
        "2.3 Готово для передачи Выпускающему": (
            "влито в шаблон после 0.42, ещё не выпущено; отсюда Выпускающий берёт в выпуск",
            "Сделано целиком и влито в шаблон после выхода 0.42, готово для передачи Выпускающему. "
            "Расхождения в строках показывают, что нужно сверить. "
            "Полный журнал невыпущенных правок приведён отдельно под спойлером; его число не равно числу результатов.",
        ),
        "2.4 Взято Выпускающим": (
            f"принятых правок: {taken_records}; считаются только готовые результаты с прямой связью"
            if taken_records else "отобрано Выпускающим в следующий выпуск",
            f"Правок в принятом составе: {taken_records}. Здесь только готовые результаты, все связанные правки "
            "которых взяты; частично готовые остаются в 2.1. Готовые результаты без подтверждённой связи "
            "остаются в 2.3." if taken_records else "Отобрано Выпускающим в следующий выпуск; после выхода 0.42 отбор ещё не начат.",
        ),
        "Вышло в 0.37–0.41.11": (
            "вышло пользователям в 0.37–0.41.11",
            f"Эти результаты вышли пользователям в выпусках 0.37–0.41.11 и вошли в 0.42; на общем табло они "
            f"учитываются в [пункте 3 «Сделано»](done.md). До выхода 0.42 здесь был этап 2.3.1.\n\n"
            f"Справка по всему журналу 0.37–0.41.11, а не только по результатам этого списка "
            f"([состав](../releases/0.N/0.41.11/shipped.md)): {rec_041} строк, "
            f"{c['records']} разных записей ({c['repeated']} повторяются в двух версиях). Связь записей с "
            f"результатами предварительная, до приёмки Разработчиком: по номеру коммита или запроса на слияние — "
            f"{c['result_by_ref']}, по совпавшему чтению двух разметчиков — {c['result_by_reading']}; они служат "
            f"{len(linked_041)} результатам. Разметчики разошлись — {c['contested']}; у РП нет "
            f"единственного подходящего результата — {c['none']}; служебные — {c['service']}; у РП записи нет "
            f"результатов на табло — {c['rp_no_board_results']}; без номера РП — {c['no_rp']}.",
        ),
        "Вышло в 0.42": (
            "вышло пользователям в 0.42",
            f"Сделанные результаты, все правки которых вошли в выпуск 0.42.0, и результаты, которые Разработчик "
            f"отнёс к 0.42 вручную. На общем табло они учитываются в [пункте 3 «Сделано»](done.md). "
            f"Журнал выпуска 0.42.0 — {rec_042} записей ([состав](../releases/0.N/0.42/shipped.md)); "
            "запись служит результату только по связи из файла Разработчика. "
            "Записи исправительного выпуска 0.42.1 сюда не входят: они на странице [Вышло в 0.42.1](released-0.42.1.md).",
        ),
        "Вышло в 0.42.1": (
            "вышло пользователям в 0.42.1",
            f"Сделанные результаты, все правки которых вышли, и хотя бы одна из них — в исправительном выпуске 0.42.1. "
            f"На общем табло они учитываются в [пункте 3 «Сделано»](done.md). "
            f"Журнал выпуска 0.42.1 — {rec_0421} записей ([состав](../releases/0.N/0.42.1/shipped.md)): "
            f"служат записанным результатам — {kinds_0421['result']}, новым предложенным результатам — "
            f"{kinds_0421['proposed']}, служебные правки без видимого результата — {kinds_0421['service']}. "
            "Запись служит результату только по связи из файла Разработчика.",
        ),
        "**3. Сделано**": (
            "сделано; незавершённых этапов 2.1–2.4 не зафиксировано",
            "Все результаты со стадией «сделано», для которых не зафиксирован незавершённый этап 2.1–2.4. "
            "Основание отметки указано в состоянии: выпуск шаблона, поставка через отдельный сервис или исходный документ. "
            "Отметка «сделано» в источнике сама по себе не подтверждает выпуск шаблона.",
        ),
        "**4. Отложено**": ("работа отложена", "Все результаты со стадией «отложено». Основание — исходный документ или подробный учёт работы."),
        OUTSIDE[0]: (
            "сделано вне выпуска шаблона",
            "В исходном документе у этих результатов стадия «сделано». Они поставлены вне файлов шаблона: "
            "в плагине, сервисе или отдельном расширении. "
            "Место реализации указано в подтверждении Разработчика; канал, где человек видит результат, "
            "показан отдельно. Все эти результаты уже учтены в [пункте 3 «Сделано»](done.md) "
            "и в общем итоге; повторно прибавлять их не нужно. "
            "Список служит для сверки отбора, а не для подсчёта всех результатов других систем.",
        ),
    }


def count_statuses(results, statuses) -> int:
    return sum(1 for r in results if r["status"] in statuses)


def source_result_codes(text: str) -> set[str]:
    codes = re.findall(r"^\| (Ц\d+-\d+) \|", text, re.MULTILINE)
    if len(codes) != len(set(codes)):
        raise SystemExit("duplicate result codes in state-by-goals source")
    return set(codes)


def pinned_input_url(repo: Path, name: str, source_text: str) -> str | None:
    """Link to the exact source revision only when its recorded hash matches this build.

    The pages are public, so only an input declared `public: true` in the manifest gets a link;
    a private or undeclared source is shown as plain text (readers would get 404 otherwise).
    """
    manifest = repo / layout.DEVELOPER_SOURCES
    if not manifest.exists():
        return None
    doc = yaml.safe_load(manifest.read_text())
    entry = next((item for item in doc.get("inputs", []) if item.get("name") == name), None)
    if not entry or entry.get("public") is not True:
        return None
    if entry.get("sha256") != hashlib.sha256(source_text.encode()).hexdigest():
        return None
    source_repo = entry.get("repo", "").removesuffix(".git")
    revision, path = entry.get("revision", ""), entry.get("path", "")
    if not source_repo.startswith("https://github.com/") or not re.fullmatch(r"[0-9a-f]{40}", revision) or not path:
        return None
    return f"{source_repo}/blob/{revision}/{quote(path, safe='/')}"


def source_stages_for_codes(source_text: str, codes: set[str]) -> dict[str, int]:
    counts = dict.fromkeys(STAGE_TO_STATUS, 0)
    for line in source_text.splitlines():
        if not re.match(r"^\| Ц\d+-\d+ \|", line):
            continue
        cells = table_cells(line)
        if cells[0] not in codes:
            continue
        stage = cells[5]
        if stage not in counts:
            raise SystemExit(f"unknown source stage {stage!r} in {cells[0]}")
        counts[stage] += 1
    if sum(counts.values()) != len(codes):
        raise SystemExit("source stage counts do not cover the requested result codes")
    return counts


def general_result_states(source_text: str, results: list[dict]) -> dict[str, dict]:
    """Use every source row and refine its stage with the existing delivery workflow."""
    source_codes = source_result_codes(source_text)
    source_stages_for_codes(source_text, source_codes)
    by_code = {result["code"]: result for result in results}
    if len(by_code) != len(results):
        raise SystemExit("duplicate result codes in workflow input")
    foreign = set(by_code) - source_codes
    if foreign:
        raise SystemExit(f"workflow results absent from source: {sorted(foreign)}")
    states = {}
    for number, line in enumerate(source_text.splitlines(), 1):
        if not re.match(r"^\| Ц\d+-\d+ \|", line):
            continue
        cells = table_cells(line)
        code, source_stage = cells[0], cells[5]
        status = by_code[code]["status"] if code in by_code else source_stage
        if status not in STATUS_TO_STAGE:
            raise SystemExit(f"unknown board status {status!r} in {code}")
        states[code] = {"source_stage": source_stage, "stage": STATUS_TO_STAGE[status],
                        "status": status, "line": number, "system": cells[7] if len(cells) > 7 else "—"}
    return states


def board_stage_counts(states: dict[str, dict]) -> dict[str, int]:
    return {stage: sum(row["stage"] == stage for row in states.values()) for _, stage in SOURCE_GROUPS}


def source_code_link(code: str, row: dict, source_url: str | None) -> str:
    return f"[{code}]({source_url}#L{row['line']})" if source_url else code


def stage_page_codes(states: dict[str, dict]) -> dict[str, set[str]]:
    """The leaf pages partition the full board; the DONE_SUBSETS pages are lists inside «Сделано»."""
    stages = {f"**{label}**": stage for label, stage in SOURCE_GROUPS}
    subsets = {page for _, page, _ in DONE_SUBSETS}
    pages = {}
    for name, page, statuses in (*STAGES, *DONE_SUBSETS):
        if page:
            pages[page] = {code for code, row in states.items()
                           if (row["stage"] == stages[name] if name in stages else row["status"] in statuses)}
    leaves = [code for page, codes in pages.items() if page not in subsets for code in codes]
    if len(leaves) != len(set(leaves)) or set(leaves) != set(states):
        raise SystemExit("stage pages must partition all source results exactly once")
    for page in subsets:
        if not pages[page] <= pages["done.md"]:
            raise SystemExit(f"{page}: its results must be counted as done")
    return pages


def stage_result_lines(codes: set[str], states: dict[str, dict], by_code: dict[str, dict],
                       source_url: str | None, stage_name: str) -> list[str]:
    """Keep source descriptions at source; retain existing working notes only for item 2."""
    detailed = stage_name.startswith("2.")
    out = ["| Код | Система | Состояние | Источник |" + (" Что получает |" if detailed else ""),
           "|---|---|---|---|" + ("---|" if detailed else "")]
    for code in sorted(codes):
        row, result = states[code], by_code.get(code, {})
        status = "сделано — отметка источника" if row["status"] == "сделано" else row["status"]
        note = "; ".join(filter(None, (status, result.get("mismatch"), result.get("evidence"))))
        line = f"| {code} | {cell(row['system'])} | {cell(note)} | {source_code_link(code, row, source_url)} |"
        if detailed:
            line += f" {cell(result.get('what', 'Описание в источнике'))} |"
        out.append(line)
    return out + [""]


def check_stage_pages(repo: Path, states: dict[str, dict]) -> None:
    for page, expected in stage_page_codes(states).items():
        text = (repo / layout.BOARD_DIR / page).read_text()
        codes = re.findall(r"^\| (Ц\d+-\d+) \|", text, re.MULTILINE)
        if set(codes) != expected or len(codes) != len(expected):
            raise SystemExit(f"{page}: result rows differ from the general board")
        if not re.search(rf"^# .+: {len(expected)}$", text, re.MULTILINE):
            raise SystemExit(f"{page}: heading count differs from result rows")


def result_inventory_lines(source_codes: set[str], source_text: str, source_url: str | None, results: list[dict]) -> list[str]:
    source_stages = source_stages_for_codes(source_text, source_codes)
    states = general_result_states(source_text, results)
    stages = board_stage_counts(states)
    comparison_rows = []
    for name, stage in SOURCE_GROUPS:
        delta = stages[stage] - source_stages[stage]
        difference = f"{delta:+d}" if delta else "0"
        comparison_rows.append(f"| {name} | {source_stages[stage]} | {stages[stage]} | {difference} |")
    source_title = (
        f'<a href="{source_url}">{len(source_codes)} в исходном документе</a>'
        if source_url else f"{len(source_codes)} в исходном документе"
    )
    lines = [
        "<details>",
        f"<summary>1. Результаты — {source_title}</summary>",
        "",
        "| Стадия | В исходном документе | На табло | Разница |",
        "|---|---:|---:|---:|",
        *comparison_rows,
        f"| **Всего** | **{len(source_codes)}** | **{len(states)}** | **0** |",
        "",
        f"Исходный документ: **{len(source_codes)} = " + " + ".join(str(source_stages[stage]) for _, stage in SOURCE_GROUPS) + "**.",
        f"Табло: **{len(states)} = " + " + ".join(str(stages[stage]) for _, stage in SOURCE_GROUPS) + "**. "
        "Все слагаемые — результаты; каждый код источника учтён один раз. "
        "«Отложено» остаётся отдельной стадией.",
        "",
    ]
    changed = {code: row for code, row in states.items() if row["stage"] != row["source_stage"]}
    if changed:
        lines += ["**Почему стадии различаются.** Исходные отметки сохранены. На табло используется более "
                  "подробный статус подготовки выпуска, когда он есть. Поэтому отметка источника «сделано» "
                  "сама по себе не означает завершения проверки, передачи и принятия в выпуск. "
                  "Каждый код учитывается на табло один раз. Ниже — все отличия, с кодами для сверки.", ""]
        for source_stage, stage in sorted({(r["source_stage"], r["stage"]) for r in changed.values()}):
            codes = [code for code, row in changed.items() if (row["source_stage"], row["stage"]) == (source_stage, stage)]
            links = ", ".join(source_code_link(code, states[code], source_url) for code in codes)
            lines += [f"- «{source_stage}» в источнике → «{stage}» на табло: **{len(codes)}** — {links}."]
        lines += [""]
    return lines + ["</details>", ""]


def record_inventory_lines(staging: list[dict], unreleased_links: list[dict], released: dict, results: list[dict], taken_records: int) -> list[str]:
    old = sum(map(len, released["0.36"].values()))
    recent = sum(map(len, released["0.41.11"].values()))
    last = sum(map(len, released["0.42"].values()))
    fix = sum(map(len, released["0.42.1"].values()))
    unreleased = len(unreleased_links)
    total = old + recent + last + fix + unreleased
    staging_counts = {status: sum(s["staging_status"] == status for s in staging) for status in STAGING_TO_STATUS}
    testing = [s for s in staging if s["staging_status"] == "testing"]
    proposed_testing = {
        (s["link"]["proposed"]["goal"], s["link"]["proposed"]["what"])
        for s in testing if s.get("link", {}).get("proposed")
    }
    proposed_unreleased = {
        (u["proposed"]["goal"], u["proposed"]["what"])
        for u in unreleased_links if u.get("proposed")
    }
    shared = len(proposed_testing & proposed_unreleased)
    proposed_total = len(proposed_testing | proposed_unreleased)
    taken_results = count_statuses(results, ("взято в 0.42",))
    return [
        "<details>",
        f"<summary>2. Записи правок и обкатки — {total} и {len(staging)}</summary>",
        "",
        f"**{total} = {old} + {recent} + {last} + {fix} + {unreleased}** записей журнала изменений шаблона: "
        f"[до 0.36](../releases/0.N/0.36/shipped.md), [0.37–0.41.11](../releases/0.N/0.41.11/shipped.md), "
        "[0.42](../releases/0.N/0.42/shipped.md), [0.42.1](../releases/0.N/0.42.1/shipped.md) "
        "и [ещё не выпущенные](ready.md). "
        "Одна запись описывает правку, а не целый результат; несколько записей могут служить одному результату.",
        f"Невыпущенных записей: {unreleased}; Выпускающий взял: {taken_records}; "
        f"[полностью подтверждённых результатов в стадии 2.4: {taken_results}](taken.md). "
        "Это разные единицы счёта.",
        "",
        f"**{len(staging)} = {staging_counts['testing']} + {staging_counts['promoted']} + "
        f"{staging_counts['rejected']}** записей обкатки: проверяются, перенесены в шаблон, отклонены. "
        "Это отдельный журнал; его записи нельзя прибавлять к записям изменений или к результатам.",
        f"[Предложений новых результатов: {proposed_total}](proposed.md) = "
        f"{len(proposed_testing)} из обкатки + {len(proposed_unreleased)} из невыпущенных правок "
        f"− {shared}, встречающихся в обоих источниках. Предложение пока не является строкой результата "
        "в исходном документе и не прибавляется к его итогу.",
        "",
        "</details>",
        "",
    ]


def code_inventory_lines(source_codes: set[str], result_codes_text: str) -> list[str]:
    indexed = set(re.findall(r"^\| (Ц\d+-\d+) \|", result_codes_text, re.MULTILINE))
    current = indexed & source_codes
    retained = indexed - source_codes
    missing = source_codes - indexed
    return [
        "<details>",
        f"<summary>3. Коды — {len(indexed)} в указателе</summary>",
        "",
        f"Уникальных кодов в указателе: **{len(indexed)} = {len(current)} + {len(retained)}**. "
        "Слагаемые — коды результатов и сохранённые коды других записей.",
        f"Строк результатов в исходном документе: {len(source_codes)}; у каждой — один уникальный код. "
        f"Кодов результатов, отсутствующих в указателе: **{len(missing)}**.",
        "Код сохраняется при переносе записи в другую таблицу или документ, поэтому число кодов "
        "не обязано совпадать с числом результатов. Исходные ревизии обоих документов — "
        "в [описании сборки](developer-sources.yaml).",
        "",
        "</details>",
        "",
    ]


def work_detail_groups(source_text: str, results: list[dict]) -> tuple[list[dict], dict[str, int]]:
    """Partition the board's in-work stage, using the same effective states as its summary."""
    states = general_result_states(source_text, results)
    work_lines = {code: row["line"] for code, row in states.items() if row["stage"] == "в работе"}
    groups = []
    assigned = set()
    for name, _, statuses in WORK_STAGES:
        codes = {
            code for code in work_lines
            if states[code]["status"] in statuses
        }
        if assigned & codes:
            raise SystemExit("work detail stages overlap")
        assigned.update(codes)
        groups.append({"name": name, "anchor": f"work-step-{len(groups) + 1}", "codes": codes})
    if assigned != set(work_lines):
        raise SystemExit(f"work detail does not cover the board in-work stage: {sorted(set(work_lines) - assigned)}")
    return groups, work_lines


def work_detail_inventory_lines(source_text: str, results: list[dict], source_url: str | None) -> list[str]:
    groups, work_lines = work_detail_groups(source_text, results)
    lines = ["<details open>", f"<summary>5. Строки пункта 2 «В работе» — {len(work_lines)}</summary>", "",
             "Каждый код ниже учтён в пункте 2 табло и указан ровно в одной группе. "
             "Ссылка на код ведёт к строке исходного документа; описания результатов здесь не копируются.", ""]
    for group in groups:
        lines += [f'<a id="{group["anchor"]}"></a>', f'### {group["name"]} — {len(group["codes"])}', ""]
        codes = sorted(group["codes"], key=work_lines.get)
        links = [f"[{code}]({source_url}#L{work_lines[code]})" if source_url else code for code in codes]
        lines += [", ".join(links) if links else "Нет результатов на этом этапе.", ""]
    return lines + ["</details>", ""]


def board_lines(source_date: str, source_text: str, results: list[dict], source_url: str | None) -> list[str]:
    """One effective-state hierarchy; every child count is a subset of its parent."""
    states = general_result_states(source_text, results)
    counts = board_stage_counts(states)
    groups, work_lines = work_detail_groups(source_text, results)
    if len(work_lines) != counts["в работе"]:
        raise SystemExit("work detail total differs from the summary")
    source_label = (
        f"[«Состояние по целям»]({source_url})" if source_url else "«Состояние по целям»"
    )
    out = [
        f"> Состояние результатов на {source_date}.",
        "",
        "# Табло результатов",
        "",
        f"Все **{len(states)}** результатов из документа {source_label}. "
        "Стадии учитывают подробные статусы подготовки выпуска. «В работе» охватывает разработку, "
        "проверку и передачу; «Сделано» — отмеченные как сделанные результаты без незавершённого этапа в учёте выпуска. "
        "Подробные описания остаются в исходном документе.",
        "",
        "| Стадия | Результатов |",
        "|---|---:|",
        *[f"| {name} | {counts[stage]} |" for name, stage in SOURCE_GROUPS],
        f"| **Всего** | **{len(states)}** |",
        "",
        "Каждый результат учтён ровно в одной стадии. "
        "Разница с исходными отметками показана в [сверке](completeness.md). "
        "Числа обновляются после получения новых исходных данных и пересборки.",
        "",
        "<details>",
        f"<summary>2. В работе — детализация {len(work_lines)} результатов</summary>",
        "",
        "Все результаты пункта 2 распределены по этапам 2.1–2.4 без пересечений. "
        "Исходная отметка «в работе» соответствует 2.1; подтверждённые статусы проверки, передачи "
        "и принятия в выпуск определяют этапы 2.2–2.4.",
        "",
        "| Этап | Результатов |",
        "|---|---:|",
    ]
    for group in groups:
        count = len(group["codes"])
        number = f'[{count}](completeness.md#{group["anchor"]})' if count else "0"
        out.append(f'| {group["name"]} | {number} |')
    out += [f"| **Итого пункт 2** | **{len(work_lines)}** |", "",
            f"**{len(work_lines)} = " + " + ".join(str(len(group["codes"])) for group in groups) + "**.", "",
            "Этап 2.3 — результаты, все правки которых [влиты в шаблон после выхода 0.42](ready.md). "
            "Вышедшее учитывается в пункте 3 «Сделано»: [в 0.37–0.41.11](released-0.37-0.41.11.md)"
            ", [в 0.42](released-0.42.md) и [в 0.42.1](released-0.42.1.md).",
            "", "</details>", ""]
    out += ["[Сверка полноты](completeness.md) · [результаты и статистика IWE](stats.md).", ""]
    return out


def outside_result_rows(rows: list[dict], states: dict[str, dict] | None = None, source_url: str | None = None) -> list[str]:
    return [
        f"| {r['code']} | {cell(r['where'])} | {cell(r['evidence'])} | {cell(r['what'])} |"
        + (f" {source_code_link(r['code'], states[r['code']], source_url)} |" if states is not None else "")
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
    if page == "at-developer.md":
        testing = [s for s in staging if s["staging_status"] == "testing"]
        moved = [s for s in staging if s["staging_status"] == "promoted"]
        kept = [s for s in staging if s["staging_status"] == "rejected"]
        out = [
            "<details>",
            "<summary>Справка: весь журнал обкатки и замер файлов Разработчика</summary>",
            "",
            "Здесь считаются записи правок и файлы, а не результаты этапа 2.2. "
            f"На обкатке {len(testing)} записей: {record_split([s['link'] for s in testing])}.",
            "",
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
        return out + [f"| {s['id']} | {cell(s['title'])} | {s['status']} | {s.get('mismatch', '')} |" for s in moved + kept] + ["", "</details>", ""]
    if page == "ready.md":
        link_of = {u["key"]: link_label(u) for u in unreleased_links}
        out = [
            "<details>",
            "<summary>Справка: весь журнал невыпущенных правок</summary>",
            "",
            "Записи этого журнала служат результатам разных этапов и новым предложениям. "
            f"Это не число результатов этапа 2.3. Всего {len(unreleased_links)} записей: {record_split(unreleased_links)}.",
            "",
            f"## Записи раздела «Ещё не выпущено»: {len(unreleased)}",
            "",
            "| Ключ | Вид | Что | Код результата |",
            "|---|---|---|---|",
        ]
        return out + [f"| {u['key']} | {u['tag']} | {cell(short(u['text'], 200))} | {link_of[u['key']]} |" for u in unreleased] + ["", "</details>", ""]
    return []


def write_views(
    repo: Path, stamp: str, results, staging, unreleased, unreleased_links, released, author_ahead, released_links, released_counts,
    released_042_links: dict,
    fmt_sha: str,
    source_date: str,
    source_text: str,
    source_url: str | None,
    taken_records: int = 0,
) -> None:
    lists = repo / layout.BOARD_DIR
    lists.mkdir(parents=True, exist_ok=True)
    testing = [s for s in staging if s["staging_status"] == "testing"]
    notes = stage_notes(results, released, released_counts, taken_records, released_042_links)
    proposed = sorted(
        {
            (link["proposed"]["goal"], link["proposed"]["what"])
            for link in [*unreleased_links, *(s["link"] for s in testing)]
            if link.get("proposed")
        }
    )
    (repo / layout.BOARD_PAGE).write_text("\n".join(board_lines(source_date, source_text, results, source_url)))
    states = general_result_states(source_text, results)
    pages = stage_page_codes(states)
    by_code = {r["code"]: r for r in results}

    for name, page, statuses in (*STAGES, *DONE_SUBSETS):
        if not page:
            continue
        codes = pages[page]
        rows = [by_code[code] for code in sorted(codes) if code in by_code]
        title = name.strip("*")
        return_to, return_label = {
            OUTSIDE[1]: ("completeness.md", "сверка полноты"),
            **{p: ("done.md", "сделано") for _, p, _ in RELEASED_PAGES},
        }.get(page, ("README.md", "общее табло"))
        out = [stamp, "", f"# {title}: {len(codes)}", "", f"[← {return_label}]({return_to})", ""]
        if page != OUTSIDE[1]:
            out += [
                "Число и коды согласованы с общим табло. Полные описания открываются по ссылкам на исходный документ. "
                "Ссылки закреплены за снимком источника; новые изменения появятся после пересборки.",
                "",
            ]
        out += [notes[name][1], ""]
        if page == "done.md":
            out += ["Вышедшее по выпускам: " + ", ".join(
                f"[{n} — {len(pages[p])}]({p})" for n, p, _ in RELEASED_PAGES) + ".", ""]
            counts = {status: sum(states[code]["status"] == status for code in codes)
                      for status in sorted({states[code]["status"] for code in codes})}
            out += [f"- {'сделано — отметка источника' if status == 'сделано' else status}: **{count}**."
                    for status, count in counts.items()] + [""]
        if page == OUTSIDE[1]:
            out += [
                "| Код | Где пользователь видит | Реализация и подтверждение | Что получает | Источник |",
                "|---|---|---|---|---|",
                *outside_result_rows(rows, states, source_url),
                "",
            ]
        else:
            out += stage_result_lines(codes, states, by_code, source_url, title)
        out += stage_extra(page, staging, unreleased, unreleased_links, author_ahead, fmt_sha)
        (lists / page).write_text("\n".join(out))
    check_stage_pages(repo, states)
    out = [
        stamp,
        "",
        f"# Предложено новых результатов: {len(proposed)}",
        "",
        "[← сверка полноты](completeness.md)",
        "",
        "Невыпущенные записи и записи обкатки, для которых результата в «Состоянии по целям» нет. "
        "Список нужен для сверки записей шаблона. Это предложения без строки и кода результата в источнике; "
        f"к {len(states)} результатам общего табло они пока не прибавляются. "
        "После проработки и внесения в источник результат учитывается на подходящей стадии. "
        "Этот список не является итогом пользовательского опроса; первый опрос планируется по "
        "[результатам этапа 2.2](at-developer.md).",
        "",
    ]
    (lists / "proposed.md").write_text("\n".join(out + [f"- цель {goal}: {what}" for goal, what in proposed] + [""]))

    write_shipped(repo, stamp, released, {
        "0.41.11": {key: released_label(link) for key, link in released_links.items()},
        "0.42": {key: link_label(link) for key, link in released_042_links.items()},
        "0.42.1": {key: link_label(link) for key, link in released_042_links.items()},
    })


def write_shipped(repo: Path, stamp: str, released: dict, labels: dict[str, dict[str, str]]) -> None:
    """releases/<first number>.N/<N>/shipped.md is written once: after a release is out its page does not change."""
    for name, versions in released.items():
        path = repo / layout.release_dir(name) / "shipped.md"
        if path.exists():
            continue
        lines = [
            stamp,
            "",
            f"# {RELEASED_TITLES[name]}",
            "",
            "Короткая выжимка записей списка изменений шаблона; полный текст — в CHANGELOG.md шаблона.",
            "",
        ]
        marks = labels.get(name, {})
        for ver, entries in versions.items():
            lines += [f"## {ver} — записей: {len(entries)}", ""]
            lines += [
                f"- [{e['tag'] or '—'}] {short(e['text'], 200)}"
                + (f" — **{marks[e['key']]}**" if e["key"] in marks else "")
                for e in entries
            ]
            lines += [""]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines))


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


def load_handoff(path: Path, unreleased: list[dict], released_versions: set[str]) -> dict | None:
    """Developer's draft fields for every pending record.

    None when the file is not there yet or still describes a release that is already out:
    that release's candidates page is frozen, and the next handoff starts with the next release.
    """
    if not path.exists():
        return None
    declared = yaml.safe_load(path.read_text())
    if str(declared["release"]) in released_versions:
        return None
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
        "Собрано программой из файла Разработчика (`releases/developer-handoff.yaml`); руками не править. "
        "Решения Выпускающего — в [decisions.md](decisions.md), порядок чтения и словарь — в [README](README.md).",
        "",
        f"**Кандидатов — {len(unreleased)}** правок, влитых в шаблон после прошлого выпуска: "
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
    (repo / layout.release_dir(release) / "candidates.md").write_text("\n".join(out))


# Every page a reader opens; candidate test folders (logs and probes) are evidence, not pages.
LINK_CHECKED_GLOBS = ("*.md", "method/*.md", "team/**/*.md", "board/*.md", "releases/*.md", "releases/*.N/*/*.md",
                      "releases/*.N/*/tests/README.md")


def link_checked_files(repo: Path) -> list[str]:
    return sorted({path.relative_to(repo).as_posix() for pattern in LINK_CHECKED_GLOBS for path in repo.glob(pattern)})


RELEASED_GROUPS = ("Вышло и доступно",)
GROUP_LABELS = {"Вышло и доступно": "Результаты, которые уже можно получить"}
WORK_GROUPS = ("В работе", "Рассматриваем", "Приостановлено")
PUBLIC_GROUPS = RELEASED_GROUPS + WORK_GROUPS
PUBLIC_FIELDS = {
    "code", "show", "title", "updated_at",
    "vote_candidate", "selection_url", "pause_reason", "pause_source_url",
}
PUBLIC_STAGE_GROUPS = {
    **{page: "Вышло и доступно" for _, page, _ in RELEASED_PAGES},
    "done.md": "Вышло и доступно",
    "in-work.md": "В работе",
    "plan.md": "Рассматриваем",
    "deferred.md": "Приостановлено",
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
    if result.get("status") == RELEASED_042 and result.get("released_042"):
        return "0.42.0"  # derived from the 0.42 changelog records, not from a manual placement
    if result.get("status") == RELEASED_0421 and result.get("released_0421"):
        return "0.42.1"
    placements = declared.get("placement")
    if not isinstance(placements, dict) or not isinstance(placements.get(code), dict):
        public_error(f"{code}: released result needs a placement mapping")
    placement = placements[code]
    expected = {status: place for place, status in PLACE_TO_STATUS.items()}[result["status"]]
    version = placement.get("version")
    if (placement.get("place") != expected or not isinstance(version, str)
            or not re.fullmatch(r"\d+\.\d+\.\d+", version)
            or not placement.get("evidence") or not result.get("evidence")):
        public_error(f"{code}: released result needs matching stable placement and evidence")
    if PLACE_TO_STATUS[RANGE_PLACES[released_range(version)]] != result["status"]:
        public_error(f"{code}: version is outside the released range")
    if placement["evidence"] != result["evidence"]:
        public_error(f"{code}: release evidence differs between placement and snapshot")
    return version


def public_row(entry: dict, result: dict, declared: dict) -> dict:
    code = entry["code"]
    if result.get("mismatch"):
        public_error(f"{code}: source has an unresolved mismatch")
    status = result.get("status")
    # A release page is more precise than «Сделано», so it is looked up first.
    page = next((page for _, page, states in (*RELEASED_PAGES, *STAGES)
                 if page in PUBLIC_STAGE_GROUPS and status in states), None)
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


def public_group_tables(rows: list[dict], groups: tuple[str, ...]) -> list[str]:
    lines: list[str] = []
    for group in groups:
        selected = [row for row in rows if row["group"] == group]
        if not selected:
            continue
        lines.extend([f"**{GROUP_LABELS.get(group, group)}**", "", "| Что меняется для вас | Подробности | Дата текста |", "|---|---|---|"])
        for row in selected:
            detail = f"{row['detail']} · " if row["detail"] else ""
            lines.append(f"| {row['title']} | {detail}[{row['code']}]({row['source_url']}) | {row['updated_at']} |")
        lines.append("")
    return lines


def public_board_lines(snapshot: dict, declared: dict, entries: list[dict], counts: dict[str, int]) -> list[str]:
    collected, rows = public_rows(snapshot, declared)
    coming = [entry for entry in entries if entry["state"] != "released"]
    released = [entry for entry in entries if entry["state"] == "released"]
    lines = [
        "# Что сейчас: выпуски шаблона IWE", "",
        "Собирает программа; руками не править. Что сделано — [вышедшие выпуски](releases/HISTORY.md), "
        "что будет — [выпуски в проверке и в плане](releases/NEXT.md), все версии — [каталог выпусков](releases/INDEX.md).", "",
        "## Над чем идёт работа", "",
        *release_catalog.testing_line(entries), "",
    ]
    if coming:
        lines.extend([*release_catalog.version_table_lines(coming), ""])
    else:
        lines.extend(["Выпусков в проверке или в плане нет.", ""])
    lines.extend([
        f"Состояния результатов по данным на {collected}; позже они могли измениться. "
        "Работы не обещаны к определённой дате или выпуску.", "",
        *public_group_tables(rows, WORK_GROUPS),
        "## Что вышло и доступно", "",
        *release_catalog.released_line(entries), "",
        *release_catalog.version_table_lines(released), "",
        *public_group_tables(rows, RELEASED_GROUPS),
        "## Как читать состояния", "",
        release_catalog.legend_line(), "",
        release_catalog.counts_line(counts), "",
        "Вопрос о записи — [команде выпуска](team/README.md#роли). "
        "[Как устроены состояния](method/board-rules.md#пользовательский-вид-табло)", "",
    ])
    return lines


def read_now_page(repo: Path) -> str | None:
    path = repo / layout.NOW_PAGE
    if not path.is_file():
        return None
    with path.open(encoding="utf-8", newline="") as stream:
        return stream.read()


def now_page_text(repo: Path, snapshot: dict, declared: dict) -> str:
    entries = release_catalog.load_catalog(repo)
    return "\n".join(public_board_lines(snapshot, declared, entries, release_catalog.board_counts(repo))) + "\n"


def write_now_page(repo: Path, text: str) -> None:
    """Replace NOW.md atomically: a reader never sees half a page."""
    path = repo / layout.NOW_PAGE
    if read_now_page(repo) == text:
        return
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=repo, prefix=".now-", delete=False) as temporary:
            temp_path = Path(temporary.name)
            temporary.write(text)
            temporary.flush()
            os.fsync(temporary.fileno())
        temp_path.replace(path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def expected_now_page(repo: Path) -> str:
    snapshot = yaml.safe_load((repo / layout.SNAPSHOT).read_text())
    declared = yaml.safe_load((repo / layout.DEVELOPER_LINKS).read_text())
    if not isinstance(snapshot, dict) or not isinstance(declared, dict):
        public_error("snapshot and developer links must be mappings")
    check_public_source_pages(repo, snapshot, declared)
    return now_page_text(repo, snapshot, declared)


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


def write_stats(repo: Path, src: Path, stamp: str, today: str, fmt_sha: str, released_records: int) -> None:
    """board/stats.md: big numbers; the template tag and history inputs are optional."""
    optional = {name: (src / name).read_text() if (src / name).exists() else None
                for name in ("fmt-tags.txt", "fmt-history.txt")}
    lines = iwe_stats.stats_lines(stamp, today, fmt_sha, release_catalog.board_counts(repo), released_records,
                                  optional["fmt-tags.txt"], optional["fmt-history.txt"])
    (repo / layout.STATS_PAGE).write_text("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--src", type=Path)
    mode.add_argument("--user-board-only", action="store_true")
    mode.add_argument("--check-user-board", action="store_true")
    mode.add_argument("--check-links", action="store_true", help="relative links and anchors of the public pages")
    ap.add_argument("--source-date", help="date when the pinned inputs were collected (YYYY-MM-DD)")
    ap.add_argument("--repo", type=Path, required=True)
    args = ap.parse_args()
    if args.check_links:
        broken = release_catalog.broken_links(args.repo, link_checked_files(args.repo))
        if broken:
            print("links: broken:\n" + "\n".join(broken), file=sys.stderr)
        return 1 if broken else 0
    if args.user_board_only or args.check_user_board:
        now_page = expected_now_page(args.repo)
        entries = release_catalog.load_catalog(args.repo)
        if args.check_user_board:
            stale = [str(layout.NOW_PAGE)] if read_now_page(args.repo) != now_page else []
            stale += release_catalog.stale_outputs(args.repo, entries)
            if stale:
                print(f"public_board: stale {', '.join(stale)}; run --user-board-only", file=sys.stderr)
                return 1
        else:
            write_now_page(args.repo, now_page)
            release_catalog.write_outputs(args.repo, entries)
        return 0
    src = args.src

    fmt_sha = (src / "fmt-sha").read_text().strip()
    fmt_files = (src / "fmt-files.txt").read_text().split()
    goals = selected_goals((src / "map005.md").read_text())
    sbg_text = (src / "sbg.md").read_text()
    source_url = pinned_input_url(args.repo, "sbg.md", sbg_text)
    result_codes_text = (src / "result-codes.md").read_text()
    results = results_for(sbg_text, goals)
    attach_works(results, result_codes_text, (src / "weekplan.md").read_text())
    staging = staging_entries((src / "staging.md").read_text(), fmt_files)
    sections = changelog_sections((src / "changelog.md").read_text())
    unreleased = sections.pop("Unreleased")
    released = {name: {} for name in RELEASED_RANGES}
    for ver, entries in sections.items():
        released[released_range(ver)][ver] = entries
    # released_0_42 of the links file covers both 0.42.0 and 0.42.1 records.
    released_0421_keys = frozenset(e["key"] for entries in released["0.42.1"].values() for e in entries)
    released_042_keys = {e["key"] for entries in released["0.42"].values() for e in entries} | released_0421_keys
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
    links_file = args.repo / layout.DEVELOPER_LINKS
    apply_links(results, developer["unreleased_links"], released_042_keys, staging, links_file, released_0421_keys)
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
    handoff_path = args.repo / layout.HANDOFF
    released_versions = {
        e["version"] for e in release_catalog.load_catalog(args.repo) if e["state"] == "released"
    } if handoff_path.exists() else set()
    handoff = load_handoff(handoff_path, unreleased, released_versions)
    taken_records = 0
    if handoff:
        decisions_path = args.repo / layout.release_dir(str(handoff["release"])) / "decisions.md"
        decisions = decisions_path.read_text()
        problems = decision_problems(handoff, decisions, fmt_sha)
        if problems:
            raise SystemExit("release decisions: " + "; ".join(problems))
        taken, _ = selected_record_keys(handoff, decisions, fmt_sha)
        taken_records = len(taken)
        apply_taken_results(results, developer["unreleased_links"], taken)
    has_public_board = "public_board" in declared
    header = (
        "# Снимок источников: результаты и их заявленные статусы из карточек работ.\n"
        "# Собирает tools/build_board.py при каждом запуске; руками не править.\n"
    )
    (args.repo / layout.SNAPSHOT).write_text(
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
        declared["released_0_42"],
        fmt_sha,
        today,
        sbg_text,
        source_url,
        taken_records,
    )

    # Completeness: every source item is on the board, linked or explicitly not linked.
    # Each board count is compared with an independent raw count of the source text.
    source_codes = source_result_codes(sbg_text)
    source_raw = sum(1 for line in sbg_text.splitlines() if re.match(r"^\| Ц\d+-\d+ \|", line))
    sbg_raw = sum(
        1
        for line in sbg_text.splitlines()
        if (m := re.match(r"^\| Ц(\d+)-\d+ \|", line)) and int(m.group(1)) in goals
    )
    staging_raw = sum(1 for line in (src / "staging.md").read_text().splitlines() if line.startswith("| S-"))
    changelog_raw = sum(1 for line in (src / "changelog.md").read_text().splitlines() if line.startswith("- "))
    on_board_released = sum(len(e) for part in released.values() for e in part.values())
    checks = [
        ("Все результаты исходного документа", source_raw, len(source_codes)),
        ("Результаты выбранных целей (документ 4)", sbg_raw, len(results)),
        ("Записи обкатки STAGING.md", staging_raw, len(staging)),
        (
            "Все записи списка изменений (ещё не выпущено + выпущено)",
            changelog_raw,
            len(developer["unreleased_links"]) + on_board_released,
        ),
    ]
    if author_ahead["present"] and author_ahead["complete"]:
        page = (args.repo / layout.BOARD_DIR / "at-developer.md").read_text()
        checks.append(("Файлы замера Разработчик ↔ шаблон", len(author_ahead["files"]), count_measured_rows(page)))
    staging_ids = [s["id"] for s in staging]
    duplicates = sorted({i for i in staging_ids if staging_ids.count(i) > 1})
    lines = [
        stamp,
        "",
        "# Сверка полноты",
        "",
        "Все числа относятся к дате снимка выше. При новой сборке они пересчитываются из "
        "[закреплённых источников](developer-sources.yaml). "
        "Результаты, записи правок и коды — разные единицы счёта; их итоги не складываются друг с другом.",
        "",
    ]
    lines += result_inventory_lines(source_codes, sbg_text, source_url, results)
    lines += record_inventory_lines(staging, developer["unreleased_links"], released, results, taken_records)
    lines += code_inventory_lines(source_codes, result_codes_text)
    lines += [
        "<details>",
        "<summary>4. Проверка источников и связей</summary>",
        "",
        "Все результаты исходного документа учтены на общем табло. Остальные строки ниже "
        "проверяют только материалы подготовки выпуска шаблона.",
        "",
        "| Источник | В источнике | Учтено в сборке |",
        "|---|---|---|",
    ]
    lines += [f"| {name} | {a} | {b} |" for name, a, b in checks]
    unlinked = sum(
        1 for u in developer["unreleased_links"] if not (u.get("result") or u.get("proposed") or u.get("service"))
    )
    lines += [
        "",
        "Отбор целей для подготовки выпуска не определяет путь поставки каждого результата. "
        "На общем табло и страницах стадий учтены все результаты. "
        "Сборка сверяет коды и числа каждой страницы, отсутствие пересечений и полный охват источника. "
        "Список поставленного вне шаблона показывает повторно только соответствующие результаты пункта 3.",
        "",
        (
            f"Не привязано к коду результата: записей «Ещё не выпущено» — {unlinked}, "
            f"записей обкатки на обкатке — {sum(1 for s in staging if s['staging_status'] == 'testing' and 'link' not in s)} "
            "(у завершённых записей обкатки связь не ведётся)."
        ),
        f"Повторяющиеся номера записей обкатки: {', '.join(duplicates) or 'нет'}.",
        f"Связи файлов, которых нет в последнем полном замере: {', '.join(stale_file_links) or 'нет'}.",
        "",
        "</details>",
        "",
    ]
    lines += work_detail_inventory_lines(sbg_text, results, source_url)
    (args.repo / layout.BOARD_DIR / "completeness.md").write_text("\n".join(lines))
    lost = [name for name, a, b in checks if a != b]
    if lost:
        print("completeness check failed: " + ", ".join(lost), file=sys.stderr)
        return 1
    write_stats(args.repo, src, stamp, today, fmt_sha, on_board_released)
    if has_public_board:
        # board/README.md is rewritten above; NOW.md reads its counts, so build the view only now.
        check_public_source_pages(args.repo, developer, declared)
        write_now_page(args.repo, now_page_text(args.repo, developer, declared))
        release_catalog.write_outputs(args.repo, release_catalog.load_catalog(args.repo))
    print(
        f"goals={len(goals)} results={len(results)} staging={len(staging)} unreleased={len(unreleased)} "
        f"released={on_board_released}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
