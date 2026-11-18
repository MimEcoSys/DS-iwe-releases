"""Tests for tools/iwe_stats.py (WP-529 F278): big numbers with a source each."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import iwe_stats  # noqa: E402

COUNTS = {"план": 5, "в работе": 3, "сделано": 2, "отложено": 1, "всего": 11}
TAGS = "v0.1.0 2026-01-05\nv0.2.0 2026-02-01\nv0.2.0-rc.1 2026-01-20\nv0.2.0-rc.2 2026-01-25\nv0.1.0-rc.1 2026-01-02\n"
HISTORY = ("2026-03-01 Last change (#12)\n2026-02-20 Merge pull request #11 from x/y\n"
           "2026-02-10 Direct fix\n2026-01-01 Too old (#1)\n")


def page(tags=TAGS, history=HISTORY):
    return "\n".join(iwe_stats.stats_lines("> Собрано", "2026-03-01", "a" * 40, COUNTS, 7, tags, history))


def test_tags_give_releases_candidates_and_the_last_release():
    numbers = iwe_stats.tag_numbers(iwe_stats.parse_tags(TAGS))
    assert numbers == {"releases": 2, "first": ("2026-01-05", "v0.1.0"), "candidates": 3,
                       "last_release": "0.2.0", "last_release_candidates": 2}


def test_window_counts_only_the_last_thirty_days_and_merged_requests():
    window = iwe_stats.window_numbers(iwe_stats.parse_history(HISTORY), "2026-03-01")
    assert window == {"start": "2026-01-30", "changes": 3, "merged": 2}


def test_every_number_has_a_source_and_a_date():
    text = page()
    assert "| **11** | результатов IWE: план 5 · в работе 3 · сделано 2 · отложено 1 |" in text
    assert "| **2** | выпусков шаблона (метки vX.Y.Z), первая метка — v0.1.0 от 2026-01-05 |" in text
    assert "из них у выпуска 0.2.0 — 2" in text
    assert "| **3** | изменений основной ветки шаблона за 30 дней (с 2026-01-30); через запрос на слияние — 2 |" in text
    rows = [line for line in text.splitlines() if line.startswith("| **")]
    assert len(rows) == 5 and all(line.endswith("| 2026-03-01 |") for line in rows)


def test_missing_input_is_an_empty_place_not_a_guess():
    text = page(tags=None, history=None)
    assert text.count("нет в этой сборке: вход не собран") == 2
    assert "Токены и стоимость" in text.split("## Пустые места")[1]
