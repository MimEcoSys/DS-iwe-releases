"""Tests for the author <-> template block of build_board.py (WP-529 F259)."""
import hashlib
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




def public_fixture(tmp_path, status="в работе"):
    repo = tmp_path / "repo"
    (repo / "ops").mkdir(parents=True)
    (repo / "board").mkdir()
    (repo / "README.md").write_text("# IWE\n\nРучная навигация и правила.\n")
    (repo / "BOARD.md").write_text("Командное табло не менять.\n")
    snapshot = {
        "snapshot": {"collected_at": "2026-11-11"},
        "results": [{"code": "Ц77-04", "status": status, "evidence": "release evidence"}],
    }
    declared = {
        "placement": {"Ц77-04": {"place": "released-0.37-0.41.11", "version": "0.41.10", "evidence": "release evidence"}},
        "public_board": {"schema_version": 1, "entries": [
            {"code": "Ц77-04", "show": True, "title": "Увидеть изменения", "updated_at": "2026-11-14"},
        ]},
    }
    for _, page, _ in board.STAGES:
        if page:
            (repo / "board" / page).write_text("| Ц77-04 | тестовый результат |\n")
    write_public_fixture(repo, snapshot, declared)
    return repo, snapshot, declared


def write_public_fixture(repo, snapshot, declared):
    for name, value in (("snapshot.yaml", snapshot), ("developer-links.yaml", declared)):
        (repo / "ops" / name).write_text(yaml.safe_dump(value, allow_unicode=True))


def run_public_cli(repo, option):
    import subprocess

    return subprocess.run(
        [sys.executable, str(Path(board.__file__)), option, "--repo", str(repo)],
        capture_output=True, text=True,
    )


def test_public_view_uses_source_state_date_and_preserves_other_files(tmp_path):
    repo, _, _ = public_fixture(tmp_path, "в разнице 0.36–0.41.11")
    original = {p.relative_to(repo): p.read_bytes() for p in repo.rglob("*") if p.is_file()}
    assert run_public_cli(repo, "--user-board-only").returncode == 0
    text = (repo / "README.md").read_text()
    assert "Состояния по данным на 2026-11-11" in text
    assert "Состояния по данным на 2026-11-14" not in text
    assert "Доступно с 0.41.10" in text.split("### В работе")[0]
    assert "[Ц77-04](board/2.3.1-released-0.37-0.41.11.md)" in text
    assert text.endswith("\n\nРучная навигация и правила.\n")
    assert "Голосование пока не запущено" in text
    assert "0 голосов" not in text
    assert run_public_cli(repo, "--user-board-only").returncode == 0
    assert (repo / "README.md").read_text() == text
    for path, content in original.items():
        if str(path) != "README.md":
            assert (repo / path).read_bytes() == content


def test_placement_does_not_promote_incomplete_work_to_released(tmp_path):
    repo, snapshot, declared = public_fixture(tmp_path)
    text = board.prepare_public_readme(repo, snapshot, declared)
    released, developing = text.split("### В работе")
    assert "Увидеть изменения" not in released
    assert "Увидеть изменения" in developing.split("### Рассматриваем")[0]
    assert "Доступно с" not in text


def test_hiding_last_entry_removes_stale_text(tmp_path):
    repo, snapshot, declared = public_fixture(tmp_path)
    board.write_public_readme(repo, board.prepare_public_readme(repo, snapshot, declared))
    entry = declared["public_board"]["entries"][0]
    entry.update(show=False, title="PRIVATE_UNIQUE_SENTINEL")
    write_public_fixture(repo, snapshot, declared)
    assert run_public_cli(repo, "--user-board-only").returncode == 0
    text = (repo / "README.md").read_text()
    assert "PRIVATE_UNIQUE_SENTINEL" not in text and "Увидеть изменения" not in text
    assert text.count("Пока нет опубликованных записей.") == 4
    assert run_public_cli(repo, "--check-user-board").returncode == 0


@pytest.mark.parametrize("status", ["у автора", "готово для передачи", "взято в 0.42", "неизвестно", "2.1"])
def test_ineligible_status_leaves_readme_unchanged(tmp_path, status):
    repo, _, _ = public_fixture(tmp_path, status)
    before = (repo / "README.md").read_bytes()
    result = run_public_cli(repo, "--user-board-only")
    assert result.returncode != 0 and "not eligible" in result.stderr
    assert (repo / "README.md").read_bytes() == before


@pytest.mark.parametrize("mutation, message", [
    (lambda s, d: d["public_board"]["entries"].append(dict(d["public_board"]["entries"][0])), "duplicate public code"),
    (lambda s, d: s["results"].append(dict(s["results"][0])), "duplicate source code"),
    (lambda s, d: d["public_board"]["entries"][0].update(code="Ц99-99"), "unknown result code"),
    (lambda s, d: d["public_board"]["entries"][0].update(show="false"), "expected boolean"),
    (lambda s, d: d["public_board"]["entries"][0].update(updated_at="2026-02-30"), "invalid date"),
    (lambda s, d: d["public_board"]["entries"][0].update(updated_at="2999-01-01"), "future date"),
    (lambda s, d: d["public_board"]["entries"][0].update(owner="invented"), "unknown entry fields"),
    (lambda s, d: s["results"][0].update(mismatch="расходится"), "unresolved mismatch"),
])
def test_invalid_public_entry_is_rejected_before_writing(tmp_path, mutation, message):
    repo, snapshot, declared = public_fixture(tmp_path)
    before = (repo / "README.md").read_bytes()
    mutation(snapshot, declared)
    write_public_fixture(repo, snapshot, declared)
    result = run_public_cli(repo, "--user-board-only")
    assert result.returncode != 0 and message in result.stderr
    assert (repo / "README.md").read_bytes() == before


@pytest.mark.parametrize("field, value", [
    ("place", "author-only"), ("version", "0.42.0-rc.15"),
    ("version", "0.42.0"), ("evidence", ""), ("evidence", "another release"),
])
def test_released_claim_needs_consistent_stable_evidence(tmp_path, field, value):
    repo, snapshot, declared = public_fixture(tmp_path, "в разнице 0.36–0.41.11")
    declared["placement"]["Ц77-04"][field] = value
    with pytest.raises(SystemExit, match="public_board"):
        board.prepare_public_readme(repo, snapshot, declared)
    assert (repo / "README.md").read_text() == "# IWE\n\nРучная навигация и правила.\n"


def test_plan_requires_recorded_selection_and_pause_requires_reason(tmp_path):
    repo, snapshot, declared = public_fixture(tmp_path, "план")
    entry = declared["public_board"]["entries"][0]
    with pytest.raises(SystemExit, match="not been selected"):
        board.prepare_public_readme(repo, snapshot, declared)
    entry.update(vote_candidate=True, selection_url="https://github.com/MimEcoSys/DS-iwe-releases/pull/1")
    assert "Отобрано для обсуждения" in board.prepare_public_readme(repo, snapshot, declared)
    snapshot["results"][0]["status"] = "отложено"
    entry.pop("vote_candidate")
    entry.pop("selection_url")
    with pytest.raises(SystemExit, match="pause_reason"):
        board.prepare_public_readme(repo, snapshot, declared)
    entry.update(pause_reason="Ждём проверку", pause_source_url="https://github.com/MimEcoSys/DS-iwe-releases/issues/1")
    text = board.prepare_public_readme(repo, snapshot, declared)
    assert "Ждём проверку" in text.split("### Приостановлено")[1]


@pytest.mark.parametrize("url", ["javascript:alert(1)", "http://github.com/x", "https://user:secret" + "@" + "github.com/x", "https://github.com/x?token=secret"])
def test_bad_decision_url_is_rejected(tmp_path, url):
    repo, snapshot, declared = public_fixture(tmp_path, "план")
    declared["public_board"]["entries"][0].update(vote_candidate=True, selection_url=url)
    with pytest.raises(SystemExit, match="public GitHub URL"):
        board.prepare_public_readme(repo, snapshot, declared)


def test_missing_source_row_and_bad_markers_preserve_readme(tmp_path):
    repo, snapshot, declared = public_fixture(tmp_path)
    before = (repo / "README.md").read_bytes()
    (repo / "board" / "2.1-in-work.md").write_text("| Ц77-05 | другая строка |\n")
    result = run_public_cli(repo, "--user-board-only")
    assert result.returncode != 0 and "missing from source page" in result.stderr
    assert (repo / "README.md").read_bytes() == before
    (repo / "README.md").write_text("# IWE\n" + board.PUBLIC_START)
    with pytest.raises(SystemExit, match="public markers"):
        board.prepare_public_readme(repo, snapshot, declared)


def test_read_only_check_detects_stale_view_and_text_is_escaped(tmp_path):
    repo, snapshot, declared = public_fixture(tmp_path)
    before = (repo / "README.md").read_bytes()
    assert run_public_cli(repo, "--check-user-board").returncode != 0
    assert (repo / "README.md").read_bytes() == before
    declared["public_board"]["entries"][0]["title"] = "Text | [link](bad) <script>\nnext"
    write_public_fixture(repo, snapshot, declared)
    assert run_public_cli(repo, "--user-board-only").returncode == 0
    text = (repo / "README.md").read_text()
    assert r"Text \| \[link\]\(bad\) &lt;script&gt; next" in text
    assert run_public_cli(repo, "--check-user-board").returncode == 0


def test_failed_atomic_replace_keeps_previous_readme(tmp_path, monkeypatch):
    repo, snapshot, declared = public_fixture(tmp_path)
    before = (repo / "README.md").read_bytes()

    def fail_replace(self, target):
        raise OSError("simulated write failure")

    monkeypatch.setattr(Path, "replace", fail_replace)
    with pytest.raises(OSError, match="simulated write failure"):
        board.write_public_readme(repo, board.prepare_public_readme(repo, snapshot, declared))
    assert (repo / "README.md").read_bytes() == before
    assert not list(repo.glob(".user-board-*"))


def test_full_build_updates_public_view_without_changing_team_outputs(tmp_path):
    import subprocess

    src = tmp_path / "source"
    src.mkdir()
    for name in ("sbg.md", "staging.md", "result-codes.md", "weekplan.md", "fmt-files.txt"):
        (src / name).write_text("")
    (src / "map005.md").write_text("| Библиотека методов | 49 |\n")
    (src / "fmt-sha").write_text("a" * 40 + "\n")
    (src / "changelog.md").write_text("## [Unreleased]\n")
    outputs = []
    for name in ("legacy", "public"):
        repo = tmp_path / name
        (repo / "ops").mkdir(parents=True)
        for version in ("0.36", "0.41.11"):
            (repo / "releases" / version).mkdir(parents=True)
        declared = {key: {} for key in ("links", "staging", "placement", "released_0_41_11", "files")}
        if name == "public":
            declared["public_board"] = {"schema_version": 1, "entries": []}
            (repo / "README.md").write_text("# IWE\n\nРучной текст.\n")
        (repo / "ops" / "developer-links.yaml").write_text(yaml.safe_dump(declared))
        result = subprocess.run(
            [sys.executable, board.__file__, "--src", str(src), "--repo", str(repo)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        outputs.append({
            p.relative_to(repo): p.read_bytes() for p in repo.rglob("*")
            if p.is_file() and p.name not in ("developer-links.yaml", "README.md")
        })
    assert outputs[0] == outputs[1]
    assert "public_board" not in (tmp_path / "public/ops/snapshot.yaml").read_text()
    assert (tmp_path / "public/README.md").read_text().count("Пока нет опубликованных записей.") == 4
    assert run_public_cli(tmp_path / "public", "--check-user-board").returncode == 0
    assert not (tmp_path / "legacy/README.md").exists()


def test_invalid_later_entry_does_not_partially_publish_valid_rows(tmp_path):
    repo, snapshot, declared = public_fixture(tmp_path)
    declared["public_board"]["entries"].append({"code": "Ц99-99", "show": True})
    write_public_fixture(repo, snapshot, declared)
    before = (repo / "README.md").read_bytes()
    result = run_public_cli(repo, "--user-board-only")
    assert result.returncode != 0 and "unknown result code" in result.stderr
    assert (repo / "README.md").read_bytes() == before



def test_manual_readme_bytes_survive_generation(tmp_path):
    repo, snapshot, declared = public_fixture(tmp_path)
    prefix = "# IWE\r\n\r\nРучной ввод.\r\n".encode()
    suffix = "\r\n\r\nРучной итог.\r\n".encode()
    path = repo / "README.md"
    path.write_bytes(prefix + board.PUBLIC_START.encode() + b"old" + board.PUBLIC_END.encode() + suffix)
    board.write_public_readme(repo, board.prepare_public_readme(repo, snapshot, declared))
    assert path.read_bytes().startswith(prefix)
    assert path.read_bytes().endswith(suffix)
    assert run_public_cli(repo, "--check-user-board").returncode == 0



@pytest.mark.parametrize("status, field, extra", [
    ("план", "selection_url", {"vote_candidate": True}),
    ("отложено", "pause_source_url", {"pause_reason": "Ждём решение"}),
])
def test_decision_link_cannot_break_table_cells(tmp_path, status, field, extra):
    repo, snapshot, declared = public_fixture(tmp_path, status)
    entry = declared["public_board"]["entries"][0]
    entry.update(extra)
    entry[field] = r"https://github.com/MimEcoSys/DS-iwe-releases/issues/1#choice|next\[link]"
    text = board.prepare_public_readme(repo, snapshot, declared)
    row = next(line for line in text.splitlines() if line.startswith("| Увидеть изменения"))
    assert row.count("|") == 4
    assert "#choice%7Cnext%5C%5Blink%5D)" in row
    assert row.endswith("| 2026-11-14 |")


def test_only_fully_ready_and_selected_results_move_to_taken():
    results = [
        {"code": "Ц1-01", "status": "готово для передачи"},
        {"code": "Ц1-02", "status": "готово для передачи"},
        {"code": "Ц1-03", "status": "готово для передачи"},
        {"code": "Ц1-04", "status": "в работе"},
    ]
    links = [
        {"key": "U-000001", "result": ["Ц1-01", "Ц1-02", "Ц1-04"]},
        {"key": "U-000002", "result": ["Ц1-02"]},
    ]
    board.apply_taken_results(results, links, {"U-000001"})
    assert [result["status"] for result in results] == [
        "взято в 0.42", "готово для передачи", "готово для передачи", "в работе",
    ]
    assert "нет прямой связи" in results[2]["mismatch"]
    assert "mismatch" not in results[1]


def test_general_board_preserves_workflow_stages_and_covers_unselected_results():
    source_text = "\n".join(
        f"| Ц1-{i:02} | 1 | гость | результат {i} | сайт | {stage} | фича | сайт | — | нет |"
        for i, stage in enumerate(("план", "в работе", "сделано", "отложено", "в работе", "в работе", "в работе",
                                   "в работе", "сделано", "сделано", "сделано"), 1)
    )
    results = [
        {"code": "Ц1-02", "status": "в работе"},
        {"code": "Ц1-03", "status": "у автора"},
        {"code": "Ц1-05", "status": "у автора"},
        {"code": "Ц1-06", "status": "готово для передачи"},
        {"code": "Ц1-07", "status": "взято в 0.42"},
        {"code": "Ц1-09", "status": "работает вне выпуска шаблона"},
        {"code": "Ц1-10", "status": "выпущено в 0.36"},
    ]
    states = board.general_result_states(source_text, results)
    assert len(states) == 11
    assert board.board_stage_counts(states) == {"план": 1, "в работе": 6, "сделано": 3, "отложено": 1}
    assert states["Ц1-03"]["source_stage"] == "сделано"
    assert states["Ц1-03"]["stage"] == "в работе"
    assert {code for code, row in states.items() if row["stage"] == "сделано"} == {"Ц1-09", "Ц1-10", "Ц1-11"}
    groups, work_lines = board.work_detail_groups(source_text, results)
    expected = {"Ц1-02", "Ц1-03", "Ц1-05", "Ц1-06", "Ц1-07", "Ц1-08"}
    listed = [code for group in groups for code in group["codes"]]
    assert set(listed) == expected == set(work_lines)
    assert len(listed) == len(set(listed)) == 6
    assert [len(group["codes"]) for group in groups] == [2, 2, 1, 1]
    assert groups[0]["codes"] == {"Ц1-02", "Ц1-08"}
    lines = board.board_lines("2026-11-11", source_text, results, "https://github.com/example/source/blob/sha/results.md")
    text = "\n".join(lines)
    assert "| **Всего** | **11** |" in text
    assert "| 2. В работе | 6 |" in text
    assert "| 3. Сделано | 3 |" in text
    assert "| 4. Отложено | 1 |" in text
    assert "| **Итого пункт 2** | **6** |" in text
    assert "**6 = 2 + 2 + 1 + 1**" in text
    assert "Этап не уточнён" not in text
    inventory = "\n".join(board.work_detail_inventory_lines(source_text, results, "https://github.com/example/source"))
    for code in expected:
        assert inventory.count(f"[{code}]") == 1
    assert "Ц1-09" not in inventory
    for group in groups:
        assert f'board/completeness.md#{group["anchor"]}' in text
        assert f'id="{group["anchor"]}"' in inventory
    with pytest.raises(SystemExit, match="duplicate result codes"):
        board.work_detail_groups(source_text + "\n" + source_text, results)
    reconciliation = "\n".join(board.result_inventory_lines(set(states), source_text, "https://github.com/example/source", results))
    assert "| 2. В работе | 5 | 6 | +1 |" in reconciliation
    assert "| 3. Сделано | 4 | 3 | -1 |" in reconciliation
    assert "«сделано» в источнике → «в работе» на табло: **1**" in reconciliation
    assert "[Ц1-03](https://github.com/example/source#L3)" in reconciliation


@pytest.mark.parametrize(("results", "error"), [
    ([{"code": "Ц1-01", "status": "в работе"}] * 2, "duplicate result codes"),
    ([{"code": "Ц1-02", "status": "в работе"}], "workflow results absent from source"),
    ([{"code": "Ц1-01", "status": "неизвестно"}], "unknown board status"),
])
def test_general_board_rejects_invalid_workflow_input(results, error):
    source_text = "| Ц1-01 | 1 | гость | результат | сайт | в работе |"
    with pytest.raises(SystemExit, match=error):
        board.general_result_states(source_text, results)


def test_stage_pages_cover_every_result_and_detect_equal_count_substitution(tmp_path):
    source = "\n".join(
        f"| Ц1-{i:02} | 1 | гость | описание {i} | сайт | {stage} | фича | сайт | — | нет |"
        for i, stage in enumerate(("план", "в работе", "сделано", "сделано", "сделано", "сделано",
                                   "сделано", "сделано", "сделано", "отложено"), 1)
    )
    results = [{"code": f"Ц1-{i:02}", "status": status, "what": "готовая заметка"}
               for i, status in enumerate(("у автора", "в разнице 0.36–0.41.11", "готово для передачи",
                                           "взято в 0.42", "выпущено в 0.36", "работает вне выпуска шаблона"), 3)]
    states = board.general_result_states(source, results)
    expected = {
        "1-plan.md": {"Ц1-01"}, "2.1-in-work.md": {"Ц1-02"}, "2.2-at-developer.md": {"Ц1-03"},
        "2.3.1-released-0.37-0.41.11.md": {"Ц1-04"}, "2.3.2-merged-after-0.41.11.md": {"Ц1-05"},
        "2.4-taken.md": {"Ц1-06"}, "3-done.md": {"Ц1-07", "Ц1-08", "Ц1-09"},
        "4-deferred.md": {"Ц1-10"}, "outside-template.md": {"Ц1-08"},
    }
    assert board.stage_page_codes(states) == expected
    (tmp_path / "board").mkdir()
    by_code = {r["code"]: r for r in results}
    for page, codes in expected.items():
        text = "\n".join([f"# Этап: {len(codes)}", *board.stage_result_lines(
            codes, states, by_code, "https://github.com/example/source", "2.1 Разрабатывается")])
        (tmp_path / "board" / page).write_text(text)
    board.check_stage_pages(tmp_path, states)
    plan = tmp_path / "board" / "1-plan.md"
    original = plan.read_text()
    assert "[Ц1-01](https://github.com/example/source#L1)" in original
    assert "описание 1" not in original
    for broken in (original.replace("Ц1-01", "Ц1-02"), original.replace("Этап: 1", "Этап: 2"),
                   original + "\n| Ц1-01 | дубль |"):
        plan.write_text(broken)
        with pytest.raises(SystemExit, match="1-plan.md"):
            board.check_stage_pages(tmp_path, states)
    assert "готовая заметка" not in "\n".join(board.stage_result_lines(
        {"Ц1-07"}, states, by_code, None, "3. Сделано"))


def test_completeness_explains_separate_units_and_code_partition():
    source = {"Ц1-01", "Ц1-02", "Ц2-01"}
    source_text = "\n".join([
        "| Ц1-01 | 1 | a | b | c | план |",
        "| Ц1-02 | 1 | a | b | c | сделано |",
        "| Ц2-01 | 2 | a | b | c | в работе |",
    ])
    result_text = "\n".join(board.result_inventory_lines(source, source_text, "https://github.com/example/blob/sha/source.md", []))
    assert (
        '<summary>1. Результаты — <a href="https://github.com/example/blob/sha/source.md">'
        '3 в исходном документе</a></summary>' in result_text
    )
    assert "**3 = 1 + 1 + 1 + 0**" in result_text
    assert "| **Всего** | **3** | **3** | **0** |" in result_text
    assert "| 4. Отложено | 0 | 0 | 0 |" in result_text
    assert "225" not in result_text

    staging = [
        {"staging_status": "testing", "link": {"proposed": {"goal": 1, "what": "A"}}},
        {"staging_status": "promoted"},
        {"staging_status": "rejected"},
    ]
    unreleased = [
        {"proposed": {"goal": 1, "what": "A"}},
        {"proposed": {"goal": 2, "what": "B"}},
    ]
    released = {"0.36": {"0.36": [{}]}, "0.41.11": {"0.41.11": [{}, {}]}}
    record_text = "\n".join(board.record_inventory_lines(staging, unreleased, released, [{"status": "взято в 0.42"}], 2))
    assert "5 = 1 + 2 + 2" in record_text
    assert "3 = 1 + 1 + 1" in record_text
    assert "Предложений новых результатов: 2" in record_text
    assert "1 из обкатки + 2 из невыпущенных правок − 1" in record_text

    index = "| Ц1-01 |\n| Ц1-02 |\n| Ц2-01 |\n| Ц9-01 |\n| Ц9-01 |"
    code_text = "\n".join(board.code_inventory_lines(source, index))
    assert "Уникальных кодов в указателе: **4 = 3 + 1**" in code_text
    assert "Слагаемые — коды результатов и сохранённые коды других записей" in code_text
    assert "Кодов результатов, отсутствующих в указателе: **0**" in code_text


def test_source_link_points_only_to_matching_pinned_revision(tmp_path):
    source_text = "| Ц1-01 | 1 | a | b | c | план |\n"
    source_hash = hashlib.sha256(source_text.encode()).hexdigest()
    (tmp_path / "ops").mkdir()
    (tmp_path / "ops" / "developer-sources.yaml").write_text(
        "inputs:\n"
        "  - name: sbg.md\n"
        "    repo: https://github.com/example/source.git\n"
        "    path: Goals-State/state-by-goals.md\n"
        f"    revision: {'a' * 40}\n"
        f"    sha256: {source_hash}\n"
    )
    assert board.pinned_input_url(tmp_path, "sbg.md", source_text) == (
        f"https://github.com/example/source/blob/{'a' * 40}/Goals-State/state-by-goals.md"
    )
    assert board.pinned_input_url(tmp_path, "sbg.md", source_text + "extra") is None


def test_outside_result_shows_implementation_evidence_separately_from_user_channel():
    row = {
        "code": "Ц82-05",
        "where": "среда на компьютере",
        "evidence": "DS-iwe-wp-panel — отдельное расширение VS Code",
        "what": "колонки стадий рабочих продуктов",
    }
    line, = board.outside_result_rows([row])
    assert "| среда на компьютере | DS-iwe-wp-panel — отдельное расширение VS Code |" in line
