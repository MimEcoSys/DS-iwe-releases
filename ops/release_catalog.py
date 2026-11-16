"""Release catalog (WP-529 F273): one hand-kept list of versions, three views.

Input  releases/index.yaml   - the Developer's list: version, state, date of the check, links.
Output releases/catalog.json - for the site, the bot and IWE (machine view, composition derived).
       releases/INDEX.md     - for people.
       version table + current-release lines for the README block (built by build_board.py).

The catalog is a projection, not a second source of statuses: a state is accepted only
together with the evidence in files of this repository (see load_catalog).
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

import yaml

CATALOG_PATH = Path("releases") / "index.yaml"
JSON_PATH = Path("releases") / "catalog.json"
INDEX_PATH = Path("releases") / "INDEX.md"
STATES = ("released", "testing", "planned")
STATE_WORDS = {"released": "вышла", "testing": "проверяется", "planned": "в плане"}
# Neutral wording only: no recommendation, no promise of a date or a composition.
STATE_LEGEND = {
    "released": "опубликована для пользователей, её можно устанавливать",
    "testing": "ещё не опубликована, идёт проверка; срок и состав выпуска не объявлены",
    "planned": "состав и срок не определены",
}
LINK_KEYS = ("release", "decisions", "shipped")
# Versions published before this repository existed carry no pilot decision here; newer ones never do.
HISTORICAL_LIMIT = (0, 41, 11)
UNKNOWN_VERSION = (999999,)
RESULT_CODE_ROW = re.compile(r"^\| (Ц\d+-\d+) \|", re.MULTILINE)
FINAL_ROW = re.compile(r"^\| Итог: выпускаем / откладываем \| (.*?) \|\s*$", re.MULTILINE)
KNOWN_FIELDS = {
    "version", "state", "as_of", "summary", "links", "published_tag", "decision_ref",
    "historical", "candidate", "last_version", "composition_page",
}
COUNT_ROWS = (
    ("план", r"1\. План"), ("в работе", r"2\. В работе"), ("сделано", r"3\. Сделано"),
    ("отложено", r"4\. Отложено"), ("всего", r"\*\*Всего\*\*"),
)


def catalog_error(message: str) -> None:
    raise SystemExit(f"release_catalog: {message}")


def repo_file(repo: Path, relative: object, name: str) -> Path:
    """A path inside the repository that exists; anything else is an error."""
    if not isinstance(relative, str) or not relative or relative.startswith(("/", "http")):
        catalog_error(f"{name}: expected a relative path inside the repository")
    path = (repo / relative).resolve()
    if repo.resolve() not in path.parents or not path.is_file():
        catalog_error(f"{name}: file not found: {relative}")
    return path


def check_date(value: object, name: str, today: dt.date) -> str:
    text = value.isoformat() if isinstance(value, dt.date) else value
    if not isinstance(text, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        catalog_error(f"{name}: expected YYYY-MM-DD")
    if dt.date.fromisoformat(text) > today:
        catalog_error(f"{name}: future date")
    return text


def codes_on_page(repo: Path, page: str, name: str) -> list[str]:
    return sorted(set(RESULT_CODE_ROW.findall(repo_file(repo, page, name).read_text(encoding="utf-8"))))


def version_numbers(text: str) -> tuple:
    """The last dotted number in a version label: «0.37–0.41.11» -> (0, 41, 11)."""
    found = re.findall(r"\d+(?:\.\d+)*", text)
    return tuple(int(part) for part in found[-1].split(".")) if found else UNKNOWN_VERSION


def check_released(repo: Path, entry: dict, name: str) -> None:
    if not entry.get("published_tag"):
        catalog_error(f"{name}: state released needs published_tag")
    # Whether the tag exists in the template is checked by the publication gate (network).
    if entry.get("historical") is True:
        if entry.get("decision_ref"):
            catalog_error(f"{name}: historical and decision_ref exclude each other")
        if version_numbers(entry.get("last_version") or entry["version"]) > HISTORICAL_LIMIT:
            catalog_error(f"{name}: historical applies only up to {'.'.join(map(str, HISTORICAL_LIMIT))}")
        return
    decisions = repo_file(repo, entry.get("decision_ref"), f"{name}.decision_ref").read_text(encoding="utf-8")
    final = FINAL_ROW.search(decisions)
    if not final or not final.group(1).strip().lower().startswith("выпускаем"):
        catalog_error(f"{name}: decisions must record 'выпускаем' in the row «Итог: выпускаем / откладываем»")


def check_entry(repo: Path, entry: object, index: int, today: dt.date) -> dict:
    if not isinstance(entry, dict):
        catalog_error(f"versions[{index}]: expected a mapping")
    name = f"versions[{index}]"
    unknown = set(entry) - KNOWN_FIELDS
    if unknown:
        catalog_error(f"{name}: unknown fields {sorted(unknown)}")
    for key in ("version", "summary"):
        if not isinstance(entry.get(key), str) or not entry[key].strip():
            catalog_error(f"{name}.{key}: expected nonempty text")
    if entry.get("state") not in STATES:
        catalog_error(f"{name}.state: expected one of {STATES}")
    entry = {**entry, "as_of": check_date(entry.get("as_of"), f"{name}.as_of", today)}
    links = entry.get("links") or {}
    if not isinstance(links, dict) or set(links) - set(LINK_KEYS):
        catalog_error(f"{name}.links: allowed keys {LINK_KEYS}")
    for key, relative in links.items():
        repo_file(repo, relative, f"{name}.links.{key}")
    state = entry["state"]
    if state == "released":
        check_released(repo, entry, name)
        if "shipped" not in links:
            catalog_error(f"{name}: state released needs links.shipped")
    elif entry.get("published_tag") or entry.get("decision_ref") or entry.get("historical"):
        catalog_error(f"{name}: published_tag, decision_ref and historical belong to released only")
    if state == "testing" and "release" not in links:
        catalog_error(f"{name}: state testing needs links.release")
    if state == "planned" and (entry.get("composition_page") or entry.get("candidate")):
        catalog_error(f"{name}: a planned version declares no composition")
    if entry.get("last_version") and state != "released":
        catalog_error(f"{name}: last_version belongs to released only")
    if entry.get("composition_page"):
        codes_on_page(repo, entry["composition_page"], f"{name}.composition_page")
    return entry


def load_catalog(repo: Path, today: dt.date | None = None) -> list[dict]:
    """Validated versions in the order written; the file's order is the display order."""
    today = today or dt.date.today()
    raw = yaml.safe_load(repo_file(repo, str(CATALOG_PATH), "catalog").read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema_version") != 1 or not isinstance(raw.get("versions"), list):
        catalog_error("expected schema_version: 1 and a list `versions`")
    entries = [check_entry(repo, entry, index, today) for index, entry in enumerate(raw["versions"])]
    names = [entry["version"] for entry in entries]
    if len(names) != len(set(names)):
        catalog_error("duplicate versions")
    if sum(entry["state"] == "testing" for entry in entries) > 1:
        catalog_error("at most one version may be in state testing")
    return entries


def last_released(entries: list[dict]) -> dict | None:
    return next((entry for entry in entries if entry["state"] == "released"), None)


def testing_now(entries: list[dict]) -> dict | None:
    return next((entry for entry in entries if entry["state"] == "testing"), None)


def shown_version(entry: dict) -> str:
    return entry.get("last_version") or entry["version"]


def details(entry: dict, prefix: str = "") -> str:
    labels = {"release": "о выпуске", "decisions": "решения", "shipped": "что вошло"}
    links = entry.get("links") or {}
    return " · ".join(f"[{labels[key]}]({prefix}{links[key]})" for key in LINK_KEYS if key in links) or "—"


def version_table_lines(entries: list[dict], prefix: str = "") -> list[str]:
    lines = ["| Версия | Состояние | Что внутри | Подробнее |", "|---|---|---|---|"]
    for entry in entries:
        lines.append(f"| {entry['version']} | {STATE_WORDS[entry['state']]} | {entry['summary']} | {details(entry, prefix)} |")
    return lines


def legend_line() -> str:
    return "Состояния: " + "; ".join(f"**{STATE_WORDS[state]}** — {STATE_LEGEND[state]}" for state in STATES) + "."


def current_release_lines(entries: list[dict], prefix: str = "") -> list[str]:
    lines = []
    testing, released = testing_now(entries), last_released(entries)
    if testing:
        link = prefix + testing["links"]["release"]
        candidate = f", кандидат {testing['candidate']}" if testing.get("candidate") else ""
        lines.append(f"Проверяется сейчас: **{testing['version']}** ([что внутри]({link}){candidate}).")
    if released:
        lines.append(f"Последний вышедший: **{shown_version(released)}**.")
    return lines


def board_counts(repo: Path) -> dict[str, int]:
    """Read the totals from the generated BOARD.md so README never carries a second copy."""
    text = (repo / "BOARD.md").read_text(encoding="utf-8")
    counts = {}
    for key, label in COUNT_ROWS:
        match = re.search(rf"^\| {label} \| \**(\d+)\** \|", text, re.MULTILINE)
        if not match:
            catalog_error(f"BOARD.md has no count row for «{key}»")
        counts[key] = int(match.group(1))
    parts = sum(value for key, value in counts.items() if key != "всего")
    if parts != counts["всего"]:
        catalog_error("BOARD.md counts do not add up to the total")
    return counts


def counts_line(counts: dict[str, int]) -> str:
    return (f"Результатов на табло: **{counts['всего']}** — план {counts['план']} · в работе {counts['в работе']} · "
            f"сделано {counts['сделано']} · отложено {counts['отложено']}. "
            "[Табло](BOARD.md) · [как считаем](guides/board-rules.md)")


def catalog_json(repo: Path, entries: list[dict]) -> str:
    out = []
    for entry in entries:
        item = {key: entry[key] for key in ("version", "state", "as_of", "summary") if key in entry}
        for key in ("last_version", "published_tag", "candidate"):
            if entry.get(key):
                item[key] = entry[key]
        item["links"] = entry.get("links") or {}
        if entry.get("composition_page"):
            item["composition_page"] = entry["composition_page"]
            item["result_codes"] = codes_on_page(repo, entry["composition_page"], entry["version"])
        out.append(item)
    document = {"schema_version": 1, "generated_from": str(CATALOG_PATH), "versions": out}
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def index_lines(entries: list[dict]) -> list[str]:
    lines = [
        "# Выпуски шаблона IWE", "",
        "Список собирает программа из файла `releases/index.yaml`; руками не править. "
        "Те же данные для сайта, бота и IWE — [catalog.json](catalog.json).", "",
        *current_release_lines(entries, prefix="../"), "",
    ]
    lines += version_table_lines(entries, prefix="../")
    lines += ["", legend_line(), ""]
    for entry in entries:
        lines.append(f"- {entry['version']}: состояние проверено {entry['as_of']}.")
    return lines + [""]


def catalog_outputs(repo: Path, entries: list[dict]) -> dict[Path, str]:
    return {JSON_PATH: catalog_json(repo, entries), INDEX_PATH: "\n".join(index_lines(entries))}


def stale_outputs(repo: Path, entries: list[dict]) -> list[str]:
    return [str(path) for path, text in catalog_outputs(repo, entries).items()
            if not (repo / path).is_file() or (repo / path).read_text(encoding="utf-8") != text]


def write_outputs(repo: Path, entries: list[dict]) -> None:
    for path, text in catalog_outputs(repo, entries).items():
        target = repo / path
        if not target.is_file() or target.read_text(encoding="utf-8") != text:
            target.write_text(text, encoding="utf-8")


def slug(heading: str) -> str:
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def broken_links(repo: Path, files: list[str]) -> list[str]:
    """Relative links and in-file anchors of the listed Markdown files that lead nowhere."""
    problems = []
    for relative in files:
        path = repo / relative
        text = path.read_text(encoding="utf-8")
        without_code = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        for target in re.findall(r"\]\(([^)\s]+)\)", without_code):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            file_part, _, anchor = target.partition("#")
            destination = (path.parent / file_part).resolve() if file_part else path
            if file_part and not destination.exists():
                problems.append(f"{relative}: missing target {target}")
            elif anchor and destination.is_file() and destination.suffix == ".md":
                headings = re.findall(r"^#{1,6}\s+(.*)$", destination.read_text(encoding="utf-8"), re.MULTILINE)
                if anchor not in {slug(heading) for heading in headings}:
                    problems.append(f"{relative}: missing anchor {target}")
    return problems
