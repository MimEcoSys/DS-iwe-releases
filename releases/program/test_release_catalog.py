import copy
import re
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent))
import release_catalog as rc  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DECISIONS_FINAL = "| Итог: выпускаем / откладываем | {} |\n"
BOARD = (
    "| Стадия | Результатов |\n|---|---:|\n| 1. План | 5 |\n| 2. В работе | 3 |\n"
    "| 3. Сделано | 2 |\n| 4. Отложено | 1 |\n| **Всего** | **11** |\n"
)
BASE = {
    "schema_version": 1,
    "versions": [
        {"version": "0.2", "state": "testing", "as_of": "2026-11-01", "summary": "проверка",
         "links": {"release": "releases/0.N/0.2/README.md"}},
        {"version": "0.1", "state": "released", "as_of": "2026-11-01", "summary": "первый",
         "published_tag": "v0.1.0", "historical": True, "composition_page": "board/done.md",
         "links": {"shipped": "releases/0.N/0.1/shipped.md"}},
    ],
}


def make_repo(tmp_path, catalog=None, decision=None):
    for relative, text in (
        ("releases/0.N/0.2/README.md", "x\n"), ("releases/0.N/0.1/shipped.md", "x\n"),
        ("board/done.md", "| Ц77-04 | a |\n| Ц77-05 | b |\n| Ц77-04 | dup |\n"),
        ("releases/0.N/0.2/decisions.md", DECISIONS_FINAL.format(decision or "")), ("board/README.md", BOARD),
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    (tmp_path / "releases" / "index.yaml").write_text(yaml.safe_dump(catalog or BASE, allow_unicode=True))
    return tmp_path


def changed(**patch):
    catalog = copy.deepcopy(BASE)
    catalog["versions"][1].update(patch)
    return catalog


def test_valid_catalog_loads_in_written_order(tmp_path):
    entries = rc.load_catalog(make_repo(tmp_path))
    assert [e["version"] for e in entries] == ["0.2", "0.1"]
    assert rc.testing_now(entries)["version"] == "0.2"
    assert rc.last_released(entries)["version"] == "0.1"


def test_released_needs_published_tag(tmp_path):
    bad = changed()
    del bad["versions"][1]["published_tag"]
    with pytest.raises(SystemExit, match="published_tag"):
        rc.load_catalog(make_repo(tmp_path, bad))


def test_released_without_history_needs_recorded_pilot_decision(tmp_path):
    bad = changed(historical=False, decision_ref="releases/0.N/0.2/decisions.md")
    with pytest.raises(SystemExit, match="выпускаем"):
        rc.load_catalog(make_repo(tmp_path, bad))
    assert rc.load_catalog(make_repo(tmp_path, bad, decision="выпускаем 16.11"))[1]["state"] == "released"


def test_historical_flag_cannot_release_a_new_version(tmp_path):
    new = changed(version="0.42", last_version="0.42")
    with pytest.raises(SystemExit, match="historical applies only up to"):
        rc.load_catalog(make_repo(tmp_path, new))
    assert rc.version_numbers("0.37–0.41.11") == (0, 41, 11)
    assert rc.version_numbers("до 0.36") == (0, 36)


def test_historical_and_decision_ref_exclude_each_other(tmp_path):
    with pytest.raises(SystemExit, match="exclude each other"):
        rc.load_catalog(make_repo(tmp_path, changed(decision_ref="releases/0.N/0.2/decisions.md")))


@pytest.mark.parametrize("patch,message", [
    ({"state": "planned"}, "planned version declares no composition|belong to released only"),
    ({"as_of": "2999-01-01"}, "future date"),
    ({"surprise": 1}, "unknown fields"),
    ({"links": {"shipped": "releases/missing.md"}}, "file not found"),
    ({"links": {"shipped": "../outside.md"}}, "file not found|relative path"),
])
def test_invalid_entries_are_rejected(tmp_path, patch, message):
    with pytest.raises(SystemExit, match=message):
        rc.load_catalog(make_repo(tmp_path, changed(**patch)))


def test_duplicates_and_two_testing_versions_are_rejected(tmp_path):
    dup = copy.deepcopy(BASE)
    dup["versions"][1]["version"] = "0.2"
    with pytest.raises(SystemExit, match="duplicate"):
        rc.load_catalog(make_repo(tmp_path, dup))
    two = copy.deepcopy(BASE)
    two["versions"][1] = {**two["versions"][0], "version": "0.3"}
    with pytest.raises(SystemExit, match="at most one"):
        rc.load_catalog(make_repo(tmp_path, two))


def test_json_derives_composition_and_stays_empty_for_unlisted(tmp_path):
    repo = make_repo(tmp_path)
    import json
    document = json.loads(rc.catalog_json(repo, rc.load_catalog(repo)))
    by_version = {v["version"]: v for v in document["versions"]}
    assert by_version["0.1"]["result_codes"] == ["Ц77-04", "Ц77-05"]
    assert "result_codes" not in by_version["0.2"]
    assert "historical" not in by_version["0.1"]


def test_stale_outputs_are_detected_and_rewritten(tmp_path):
    repo = make_repo(tmp_path)
    entries = rc.load_catalog(repo)
    assert len(rc.stale_outputs(repo, entries)) == 4
    rc.write_outputs(repo, entries)
    assert rc.stale_outputs(repo, entries) == []
    (repo / rc.INDEX_PATH).write_text("changed by hand\n")
    assert rc.stale_outputs(repo, entries) == [str(rc.INDEX_PATH)]


def test_counts_come_from_the_generated_board_and_must_add_up(tmp_path):
    repo = make_repo(tmp_path)
    assert rc.board_counts(repo) == {"план": 5, "в работе": 3, "сделано": 2, "отложено": 1, "всего": 11}
    (repo / "board" / "README.md").write_text(BOARD.replace("**11**", "**12**"))
    with pytest.raises(SystemExit, match="do not add up"):
        rc.board_counts(repo)


def test_state_legend_makes_no_promises():
    legend = rc.legend_line()
    assert "срок и состав выпуска не объявлены" in legend
    assert not re.search(r"скоро|рекоменду|берите", legend)


def test_broken_links_and_anchors_are_found(tmp_path):
    (tmp_path / "a.md").write_text("# Раздел один\n\n[ok](b.md#цель) [bad](missing.md) [anchor](#нет) [self](#раздел-один)\n")
    (tmp_path / "b.md").write_text("## Цель\n")
    problems = rc.broken_links(tmp_path, ["a.md"])
    assert sorted(problems) == ["a.md: missing anchor #нет", "a.md: missing target missing.md"]


def test_real_repository_is_consistent():
    entries = rc.load_catalog(REPO)
    assert rc.stale_outputs(REPO, entries) == []
    assert rc.broken_links(REPO, ["README.md", "NOW.md", "releases/INDEX.md", "releases/HISTORY.md", "releases/NEXT.md",
                                  "method/board-rules.md", "team/README.md"]) == []


def test_hand_written_readme_carries_no_board_counts():
    outside = (REPO / "README.md").read_text()
    for key, value in rc.board_counts(REPO).items():
        assert not re.search(rf"(?<![\w.\-–])\b{value}\b(?![\w.\-–])", outside), f"hand-written count {value} ({key})"


def test_explicit_html_anchor_counts_as_a_link_target(tmp_path):
    (tmp_path / "a.md").write_text("[ok](b.md#step-1) [bad](b.md#step-2)\n")
    (tmp_path / "b.md").write_text('<a id="step-1"></a>\n| строка |\n')
    assert rc.broken_links(tmp_path, ["a.md"]) == ["a.md: missing anchor b.md#step-2"]


def test_history_and_next_split_the_catalog_by_time(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "releases" / "0.N" / "0.3").mkdir(parents=True)
    (repo / "releases" / "0.N" / "0.3" / "vote.md").write_text("# Голосование\n")
    entries = rc.load_catalog(repo)
    history, coming = "\n".join(rc.history_lines(entries)), "\n".join(rc.next_lines(repo, entries))
    assert "| 0.1 | вышла |" in history and "| 0.2 |" not in history
    assert "| 0.2 | проверяется |" in coming and "| 0.1 |" not in coming
    preparing = coming.split("## Готовится")[1]
    assert "- 0.3: [vote.md](0.N/0.3/vote.md)" in preparing
    assert "- 0.1:" not in preparing and "- 0.2:" not in preparing


def test_release_folder_is_grouped_by_first_number():
    assert rc.layout.release_dir("0.42") == Path("releases/0.N/0.42")
    assert rc.layout.release_dir("1.0") == Path("releases/1.N/1.0")
