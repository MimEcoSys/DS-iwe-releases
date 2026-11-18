"""Results and statistics of IWE as big numbers (WP-529 F278): board/stats.md.

Every number names what is counted, its source and the date of the pinned inputs.
A number without a source is shown as an empty place, never estimated.

Inputs (optional, from --src; a missing file shows as "not in this build"):
  fmt-tags.txt     tags of the template merged into the pinned revision: "<tag> <YYYY-MM-DD>"
  fmt-history.txt  first-parent history of the template main: "<YYYY-MM-DD> <subject>"
"""

from __future__ import annotations

import datetime as dt
import re

STABLE_TAG = re.compile(r"^v\d+\.\d+\.\d+$")
CANDIDATE_TAG = re.compile(r"^v(?P<version>\d+\.\d+\.\d+)-rc\.\d+$")
MERGED_REQUEST = re.compile(r"^Merge pull request #\d+|\(#\d+\)$")
WINDOW_DAYS = 30
TEMPLATE_COMMIT_URL = "https://github.com/TserenTserenov/FMT-exocortex-template/commit/"
# Numbers people ask for that have no agreed source yet (decision of the pilot, 17.11).
EMPTY_PLACES = (
    ("Доля кода, написанного ИИ", "подпись соавтора в коммите этого не доказывает; правило подсчёта не определено"),
    ("Токены и стоимость", "данные пилота; публиковать ли сводную цифру — решение пилота, пока не принято"),
    ("Пользователей на последней версии", "сбора сведений об установках нет"),
    ("Длительность выпуска", "нужны даты снимка и выхода с определением обоих событий"),
    ("Рабочих сессий агентов в день", "журнал сессий закрытый; открытая сводная цифра не определена"),
)


def parse_tags(text: str) -> list[tuple[str, str]]:
    return [tuple(line.split()[:2]) for line in text.splitlines() if len(line.split()) >= 2]


def parse_history(text: str) -> list[tuple[str, str]]:
    return [(line[:10], line[11:]) for line in text.splitlines() if re.match(r"\d{4}-\d{2}-\d{2} ", line)]


def tag_numbers(tags: list[tuple[str, str]]) -> dict:
    stable = sorted((date, name) for name, date in tags if STABLE_TAG.match(name))
    candidates = [CANDIDATE_TAG.match(name).group("version") for name, _ in tags if CANDIDATE_TAG.match(name)]
    last = stable[-1][1].removeprefix("v") if stable else None
    return {
        "releases": len(stable),
        "first": stable[0] if stable else None,
        "candidates": len(candidates),
        "last_release": last,
        "last_release_candidates": sum(version == last for version in candidates),
    }


def window_numbers(history: list[tuple[str, str]], source_date: str) -> dict:
    end = dt.date.fromisoformat(source_date)
    start = end - dt.timedelta(days=WINDOW_DAYS)
    inside = [subject for date, subject in history if start < dt.date.fromisoformat(date) <= end]
    return {"start": start.isoformat(), "changes": len(inside), "merged": sum(bool(MERGED_REQUEST.search(s)) for s in inside)}


def stats_lines(stamp: str, source_date: str, fmt_sha: str, counts: dict[str, int], released_records: int,
                tags_text: str | None, history_text: str | None) -> list[str]:
    commit = f"[{fmt_sha[:7]}]({TEMPLATE_COMMIT_URL}{fmt_sha})"
    absent = "нет в этой сборке: вход не собран"
    lines = [
        stamp, "", "# Результаты и статистика IWE", "", "[← общее табло](README.md)", "",
        "Крупные цифры по закреплённым источникам сборки. У каждой — что считаем, откуда и на какую дату. "
        "Где источника нет, стоит пустое место: цифру не придумываем.", "",
        "| Цифра | Что это | Откуда | На дату |", "|---|---|---|---|",
        f"| **{counts['всего']}** | результатов IWE: план {counts['план']} · в работе {counts['в работе']} · "
        f"сделано {counts['сделано']} · отложено {counts['отложено']} | «Состояние по целям», [табло](README.md) | {source_date} |",
        f"| **{released_records}** | записей списка изменений вышло в выпусках шаблона | список изменений шаблона на {commit} | {source_date} |",
    ]
    if tags_text is None:
        lines.append(f"| — | выпусков и сборок-кандидатов шаблона | {absent} | — |")
    else:
        tags = tag_numbers(parse_tags(tags_text))
        first = f", первая метка — {tags['first'][1]} от {tags['first'][0]}" if tags["first"] else ""
        lines += [
            f"| **{tags['releases']}** | выпусков шаблона (метки vX.Y.Z){first} | метки шаблона на {commit} | {source_date} |",
            f"| **{tags['candidates']}** | сборок-кандидатов (метки -rc), из них у выпуска {tags['last_release']} — "
            f"{tags['last_release_candidates']} | метки шаблона на {commit} | {source_date} |",
        ]
    if history_text is None:
        lines.append(f"| — | изменений основной ветки шаблона за {WINDOW_DAYS} дней | {absent} | — |")
    else:
        window = window_numbers(parse_history(history_text), source_date)
        lines.append(
            f"| **{window['changes']}** | изменений основной ветки шаблона за {WINDOW_DAYS} дней "
            f"(с {window['start']}); через запрос на слияние — {window['merged']} | история шаблона до {commit} | {source_date} |")
    lines += ["", "## Пустые места", "", "| Цифра | Почему пока нет |", "|---|---|"]
    lines += [f"| {name} | {reason} |" for name, reason in EMPTY_PLACES]
    lines += ["", "Как собираются входы — [описание сборки](developer-sources.yaml); "
              "что значат стадии результатов — [правила табло](../method/board-rules.md).", ""]
    return lines
