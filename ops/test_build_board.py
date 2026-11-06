"""Tests for the author <-> template block of build_board.py (WP-529 F259)."""
import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

spec = importlib.util.spec_from_file_location("build_board", Path(__file__).parent / "build_board.py")
board = importlib.util.module_from_spec(spec)
sys.modules["build_board"] = board
spec.loader.exec_module(board)

BY_CODE = {"Ц34-10": {"code": "Ц34-10"}}
FMT_SHA = "1a4b9afc47d5a186a875fe3c9ac1a45aace059cb"


def measurement(tmp_path, **overrides):
    doc = {
        "schema_version": 1,
        "measured_at": "2026-11-06T08:34:19Z",
        "template_commit": FMT_SHA,
        "duration_s": 146,
        "complete": True,
        "incomplete_reasons": [],
        "files": [
            {"path": "CLAUDE.md", "category": "template_has_foreign_edits"},
            {"path": "memory/protocol-close.md", "category": "would_update"},
            {"path": "memory/protocol-open.md", "category": "accepted_base_unproven"},
        ],
        **overrides,
    }
    path = tmp_path / "author-ahead.yaml"
    path.write_text(yaml.safe_dump(doc, allow_unicode=True))
    return path


def lines_for(aa, fmt_sha=FMT_SHA):
    return "\n".join(board.author_ahead_lines(aa, fmt_sha))


def test_missing_measurement_is_reported_not_faked(tmp_path):
    aa = board.load_author_ahead(tmp_path / "author-ahead.yaml")
    assert aa == {"present": False, "files": []}
    assert "не приложен" in lines_for(aa)


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"schema_version": 2}, "schema_version"),
        ({"complete": "yes"}, "complete"),
        ({"files": [{"path": "a", "category": "weird"}]}, "unknown category"),
        ({"files": ["a"]}, "needs a path"),
        ({"files": [{"path": "a|b", "category": "would_update"}]}, "breaks the board table"),
        ({"files": [{"path": "a", "category": "would_update"}] * 2}, "twice"),
        ({"complete": False, "incomplete_reasons": []}, "incomplete_reasons"),
        ({"complete": True, "incomplete_reasons": ["x"]}, "no incomplete_reasons"),
        ({"template_commit": None}, "template_commit"),
    ],
)
def test_broken_measurement_stops_the_build(tmp_path, overrides, message):
    with pytest.raises(SystemExit, match=message):
        board.load_author_ahead(measurement(tmp_path, **overrides))


def test_measurement_without_required_field_stops_the_build(tmp_path):
    path = measurement(tmp_path)
    doc = yaml.safe_load(path.read_text())
    del doc["duration_s"]
    path.write_text(yaml.safe_dump(doc))
    with pytest.raises(SystemExit, match="duration_s"):
        board.load_author_ahead(path)


def test_each_file_shown_once_in_its_group(tmp_path):
    aa = board.load_author_ahead(measurement(tmp_path))
    board.apply_file_links(aa, {"CLAUDE.md": {"result": ["Ц34-10"]}}, BY_CODE)
    text = lines_for(aa)
    assert board.count_measured_rows(text) == 3
    assert "### Уйдёт в шаблон при синхронизации: 1" in text
    assert "### Расходится с шаблоном — сверить вручную: 1" in text
    assert "### Не доказано — нужна проверка Разработчика: 1" in text
    assert "| `CLAUDE.md` | в шаблоне есть свои правки; нужна сверка версий | Ц34-10 |" in text
    assert "| `memory/protocol-close.md` | синхронизация перенесёт версию Разработчика в шаблон | не привязано |" in text
    assert "другой версии шаблона" not in text


def test_measurement_against_other_template_commit_is_flagged(tmp_path):
    aa = board.load_author_ahead(measurement(tmp_path))
    board.apply_file_links(aa, {}, BY_CODE)
    assert "другой версии шаблона, чем табло (ffffffffff)" in lines_for(aa, "f" * 40)


def test_incomplete_measurement_shows_reasons_not_files(tmp_path):
    aa = board.load_author_ahead(measurement(tmp_path, complete=False, incomplete_reasons=["тайм-аут 900 с"]))
    board.apply_file_links(aa, {}, BY_CODE)
    text = lines_for(aa)
    assert "Замер неполный" in text and "тайм-аут 900 с" in text
    assert board.count_measured_rows(text) == 0


def test_count_measured_rows_ignores_other_tables():
    page = "## На обкатке\n\n| S-1 | x |\n" + board.AUTHOR_AHEAD_HEADING + "\n\n### A: 1\n\n| `a.md` | x | y |\n\n## Дальше\n\n| `b.md` | z |\n"
    assert board.count_measured_rows(page) == 1
    assert board.count_measured_rows("## другое\n| `a.md` |\n") == 0


def test_every_declared_file_link_is_validated(tmp_path):
    aa = board.load_author_ahead(measurement(tmp_path))
    with pytest.raises(SystemExit, match="Ц99-01"):
        board.apply_file_links(aa, {"deleted.md": {"result": ["Ц99-01"]}}, BY_CODE)


def test_empty_files_section_is_allowed(tmp_path):
    aa = board.load_author_ahead(measurement(tmp_path))
    assert board.apply_file_links(aa, None, BY_CODE) == []
    assert all(f["link"] == {} for f in aa["files"])


def test_links_to_files_missing_from_complete_measurement_are_reported(tmp_path):
    aa = board.load_author_ahead(measurement(tmp_path))
    stale = board.apply_file_links(aa, {"old.md": {"service": "x"}, "CLAUDE.md": {"service": "y"}}, BY_CODE)
    assert stale == ["old.md"]


def test_proposed_link_is_labelled_as_proposal(tmp_path):
    aa = board.load_author_ahead(measurement(tmp_path))
    board.apply_file_links(aa, {"CLAUDE.md": {"proposed": {"goal": 34, "what": "w"}}}, BY_CODE)
    assert "| `CLAUDE.md` | в шаблоне есть свои правки; нужна сверка версий | новый результат цели 34 |" in lines_for(aa)
