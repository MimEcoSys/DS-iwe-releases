"""Tests for tools/check_decisions.py (WP-529 Ф250/Ф252)."""
import importlib.util
import sys
from pathlib import Path

import yaml
import pytest

spec = importlib.util.spec_from_file_location("check_decisions", Path(__file__).parent / "check_decisions.py")
cd = importlib.util.module_from_spec(spec)
sys.modules["check_decisions"] = cd
spec.loader.exec_module(cd)


def record(unit, **overrides):
    rec = {
        "rollback_unit": unit,
        "commits": ["abc12345"],
        "user_gets": "польза",
        "how_to_check": "bash test.sh",
        "risk": "низкий: причина",
        "recommendation": "взять: причина",
    }
    rec.update(overrides)
    return rec


HANDOFF = {
    "release": "0.42",
    "groups": {
        "aaaa1111 (#1)": {"separable": "нет"},
        "bbbb2222 (#2)": {"separable": "да"},
    },
    "records": {
        "U-000001": record("aaaa1111 (#1)"),
        "U-000002": record("aaaa1111 (#1)"),
        "U-000003": record("bbbb2222 (#2)"),
        "U-000004": record("bbbb2222 (#2)"),
        "U-000005": record("cccc3333 (#3)"),
    },
}


def decisions(taken="", deferred=""):
    return (
        "| Решение | Значение |\n|---|---|\n"
        f"| Состав: что взято (ключи из [кандидатов](candidates.md)) | {taken} |\n"
        f"| Состав: что отложено | {deferred} |\n"
    )


def test_empty_decisions_and_complete_records_have_no_problems():
    assert cd.decision_problems(HANDOFF, decisions()) == []
    assert all(cd.record_problems(k, r) == [] for k, r in HANDOFF["records"].items())


def test_split_inseparable_group_is_reported():
    problems = cd.decision_problems(HANDOFF, decisions(taken="U-000001", deferred="U-000002"))
    assert problems == ["группа aaaa1111 (#1) неразделима, но разорвана: взято U-000001, отложено U-000002"]


def test_partly_named_inseparable_group_is_reported():
    problems = cd.decision_problems(HANDOFF, decisions(taken="U-000001, U-000005"))
    assert problems == ["группа aaaa1111 (#1) неразделима: взято U-000001, не названо U-000002"]


def test_partly_deferred_inseparable_group_is_reported():
    problems = cd.decision_problems(HANDOFF, decisions(deferred="U-000002"))
    assert problems == ["группа aaaa1111 (#1) неразделима: отложено U-000002, не названо U-000001"]


def test_missing_decision_row_is_a_form_error_not_ok():
    form = "| Решение | Значение |\n|---|---|\n| Состав: что взято | U-000001 U-000002 |\n"
    try:
        cd.decision_problems(HANDOFF, form)
    except cd.DecisionsFormError as error:
        assert "Состав: что отложено" in str(error)
    else:
        raise AssertionError("missing row must raise DecisionsFormError")


def test_duplicated_decision_row_is_reported_and_both_rows_are_read():
    form = decisions(taken="U-000001") + "| Состав: что взято, продолжение | U-abcdef |\n"
    problems = cd.decision_problems(HANDOFF, form)
    assert "строка «Состав: что взято» в decisions.md повторяется 2 раза — оставить одну" in problems
    assert "U-abcdef: в решениях, но нет среди кандидатов" in problems


def test_separable_group_may_be_split():
    assert cd.decision_problems(HANDOFF, decisions(taken="U-000003", deferred="U-000004")) == []


def test_unknown_and_double_keys_are_reported():
    problems = cd.decision_problems(HANDOFF, decisions(taken="U-000005 U-abcdef", deferred="U-000005"))
    assert "U-abcdef: в решениях, но нет среди кандидатов" in problems
    assert "U-000005: одновременно «взято» и «отложено»" in problems


def test_record_without_rollback_or_check_is_reported():
    problems = cd.record_problems("U-000009", record("dddd4444 (#4)", commits=[], how_to_check="  "))
    assert "U-000009: нет коммитов для отката (commits)" in problems
    assert "U-000009: пусто поле «как проверить» (how_to_check)" in problems


def test_main_reads_repo_and_returns_one_on_problems(tmp_path, capsys):
    (tmp_path / "releases").mkdir(exist_ok=True)
    (tmp_path / "releases" / "0.N" / "0.42").mkdir(parents=True)
    (tmp_path / "releases" / "developer-handoff.yaml").write_text(yaml.safe_dump(HANDOFF, allow_unicode=True), encoding="utf-8")
    (tmp_path / "releases" / "0.N" / "0.42" / "decisions.md").write_text(decisions(taken="U-000001"), encoding="utf-8")
    assert cd.main(["--repo", str(tmp_path)]) == 1
    assert "неразделима" in capsys.readouterr().out

    (tmp_path / "releases" / "0.N" / "0.42" / "decisions.md").write_text(decisions(taken="U-000001 U-000002"), encoding="utf-8")
    assert cd.main(["--repo", str(tmp_path)]) == 0
    assert "замечаний нет" in capsys.readouterr().out


def test_missing_decisions_file_is_exit_two(tmp_path):
    (tmp_path / "releases").mkdir(exist_ok=True)
    (tmp_path / "releases" / "developer-handoff.yaml").write_text(yaml.safe_dump(HANDOFF), encoding="utf-8")
    assert cd.main(["--repo", str(tmp_path)]) == 2


# WP-529 Ф261: the final gate (empty form rows, red team verdict kept outside the template tree).

TREE = "a" * 40
FILLED = (
    "| Решение | Значение |\n|---|---|\n"
    "| Состав: что взято (ключи из [кандидатов](candidates.md)) | U-000001 U-000002 |\n"
    "| Состав: что отложено | |\n"
    "| Какие строки проверки сборки блокируют выпуск | 1-5, 11-13 |\n"
    "| Кто исполняет роли (Разработчик, Выпускающий, проверяющий red team) | один человек, независимости нет |\n"
    "| Итог: выпускаем / откладываем | выпускаем |\n"
)


def repo_with(tmp_path, decisions_text, rc_files=None):
    (tmp_path / "releases").mkdir(exist_ok=True)
    (tmp_path / "releases" / "0.N" / "0.42" / "tests").mkdir(parents=True)
    (tmp_path / "releases" / "developer-handoff.yaml").write_text(yaml.safe_dump(HANDOFF, allow_unicode=True), encoding="utf-8")
    (tmp_path / "releases" / "0.N" / "0.42" / "decisions.md").write_text(decisions_text, encoding="utf-8")
    for name, body in (rc_files or {}).items():
        target = tmp_path / "releases" / "0.N" / "0.42" / "tests" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(yaml.safe_dump(body, allow_unicode=True), encoding="utf-8")
    return tmp_path


def verdict(**overrides):
    block = {"verdict": "GO", "checker": "codex-fresh-session", "report": "https://example.org/pr/1#c1", "tree": TREE}
    block.update(overrides)
    return {"build": "0.42-rc.1", "red_team": block}


def test_empty_form_passes_by_default_but_is_not_called_clean(tmp_path, capsys):
    repo = repo_with(tmp_path, decisions(taken="U-000001 U-000002"))
    assert cd.main(["--repo", str(repo)]) == 0
    out = capsys.readouterr().out
    assert "ЗАМЕТКА" in out and "Итог: выпускаем / откладываем" in out


def test_final_fails_on_empty_rows_and_missing_verdict(tmp_path, capsys):
    repo = repo_with(tmp_path, decisions(taken="U-000001 U-000002"))
    assert cd.main(["--repo", str(repo), "--require-final"]) == 1
    out = capsys.readouterr().out
    assert "не заполнена строка «Итог: выпускаем / откладываем»" in out
    assert "нет папки отметок rc.<K>/" in out


def test_final_passes_with_filled_form_and_stable_verdict(tmp_path, capsys):
    repo = repo_with(tmp_path, FILLED, {"rc.1/linux-tester.yaml": verdict()})
    assert cd.main(["--repo", str(repo), "--require-final", "--rc-tree", TREE]) == 0
    assert "замечаний нет" in capsys.readouterr().out


def test_final_without_rc_tree_is_refused(tmp_path, capsys):
    repo = repo_with(tmp_path, FILLED, {"rc.1/linux-tester.yaml": verdict()})
    assert cd.main(["--repo", str(repo), "--require-final"]) == 1
    assert "требует --rc-tree" in capsys.readouterr().out


def test_final_reads_the_newest_rc_only(tmp_path, capsys):
    repo = repo_with(tmp_path, FILLED, {"rc.1/linux-tester.yaml": verdict(), "rc.2/macos-tester.yaml": {"build": "0.42-rc.2", "marks": []}})
    assert cd.main(["--repo", str(repo), "--require-final", "--rc-tree", TREE]) == 1
    assert "rc.2/: ни в одном файле отметок нет блока red_team" in capsys.readouterr().out


def test_blocked_and_unaccepted_caution_fail(tmp_path):
    assert any("BLOCKED" in p for p in cd.red_team_problems(repo_with(tmp_path, FILLED, {"rc.1/linux-tester.yaml": verdict(verdict="BLOCKED")}) / "releases" / "0.N" / "0.42" / "tests", None))
    other = tmp_path / "other"
    other.mkdir()
    caution = cd.red_team_problems(repo_with(other, FILLED, {"rc.1/linux-tester.yaml": verdict(verdict="CAUTION")}) / "releases" / "0.N" / "0.42" / "tests", None)
    assert any("accepted_by" in p for p in caution)


def test_skill_verdict_words_are_the_scale(tmp_path):
    # The skill iwe-platform-redteam answers GO / CAUTION / BLOCKED or cannot_verify; the old local word STABLE is refused.
    tests = repo_with(tmp_path, FILLED, {"rc.1/linux-tester.yaml": verdict(verdict="cannot_verify")}) / "releases" / "0.N" / "0.42" / "tests"
    assert any("cannot_verify" in p and "не пройдена" in p for p in cd.red_team_problems(tests, None))
    (tests / "rc.1/linux-tester.yaml").write_text(yaml.safe_dump(verdict(verdict="STABLE"), allow_unicode=True), encoding="utf-8")
    assert any("GO, CAUTION, BLOCKED" in p for p in cd.red_team_problems(tests, None))


def test_verdict_for_another_tree_fails(tmp_path):
    repo = repo_with(tmp_path, FILLED, {"rc.1/linux-tester.yaml": verdict()})
    problems = cd.red_team_problems(repo / "releases" / "0.N" / "0.42" / "tests", "b" * 40)
    assert any("относится к дереву" in p for p in problems)


def test_every_verdict_in_the_newest_folder_is_checked(tmp_path):
    # Two testers attacked the same candidate: one GO does not hide the other's unaccepted CAUTION.
    files = {"rc.3/linux-tester.yaml": verdict(), "rc.3/macos-tester.yaml": verdict(verdict="CAUTION"),
             "rc.3/macos-marks-only.yaml": {"build": "0.42-rc.3", "marks": []}}
    problems = cd.red_team_problems(repo_with(tmp_path, FILLED, files) / "releases" / "0.N" / "0.42" / "tests", TREE)
    assert problems == ["rc.3/macos-tester.yaml: вердикт CAUTION без red_team.accepted_by — оговорки не приняты Выпускающим"]


def test_newest_folder_is_chosen_by_number_not_by_name(tmp_path):
    # rc.10 sorts before rc.9 as text; the newer candidate must win.
    files = {"rc.9/linux-tester.yaml": verdict(), "rc.10/linux-tester.yaml": verdict(verdict="BLOCKED")}
    problems = cd.red_team_problems(repo_with(tmp_path, FILLED, files) / "releases" / "0.N" / "0.42" / "tests", None)
    assert problems == ["rc.10/linux-tester.yaml: вердикт BLOCKED — не сливать"]


CUT_SHA = "a" * 40
ALL_CUT = (
    "| Версия основной ветки шаблона в момент «режем» | `" + CUT_SHA + "` |\n"
    "| Состав: что взято | " + cd.ALL_CUT_RECORDS + " |\n"
    "| Состав: что отложено | ничего |\n"
)


def test_all_at_cut_means_every_record_not_an_empty_selection():
    selected, rows = cd.selected_record_keys(HANDOFF, ALL_CUT, CUT_SHA)
    assert rows == 1
    assert selected == set(HANDOFF["records"])
    assert cd.decision_problems(HANDOFF, ALL_CUT, CUT_SHA) == []


def test_all_at_cut_rejects_wrong_snapshot_and_deferred_records():
    for form, commit in (
        (ALL_CUT, "b" * 40),
        (ALL_CUT, None),
        (ALL_CUT.replace("| ничего |", "| U-000001 |"), CUT_SHA),
    ):
        with pytest.raises(cd.DecisionsFormError):
            cd.selected_record_keys(HANDOFF, form, commit)


def test_short_snapshot_commit_is_not_a_prefix_match():
    with pytest.raises(cd.DecisionsFormError):
        cd.selected_record_keys(HANDOFF, ALL_CUT, "a" * 9)
    assert cd.selected_record_keys(HANDOFF, ALL_CUT, "a" * 10)[0] == set(HANDOFF["records"])


def released_repo(tmp_path, snapshot_commit, candidates_stamp):
    repo = repo_with(tmp_path, ALL_CUT)
    (repo / "board").mkdir()
    (repo / "board" / "snapshot.yaml").write_text(yaml.safe_dump({"snapshot": {"template_commit": snapshot_commit}}))
    (repo / "releases" / "index.yaml").write_text(
        yaml.safe_dump({"versions": [{"version": "0.42", "state": "released"}]}), encoding="utf-8")
    (repo / "releases" / "0.N" / "0.42" / "candidates.md").write_text(candidates_stamp, encoding="utf-8")
    return repo


def test_released_version_is_checked_against_its_frozen_candidates_not_the_live_board(tmp_path, capsys):
    # WP-529 F274: after 0.42 the board was rebuilt on a newer template and the check broke.
    repo = released_repo(tmp_path, "b" * 40, "> Собрано 2026-11-11 по шаблону " + CUT_SHA[:10] + ".\n")
    assert cd.main(["--repo", str(repo)]) == 0
    assert "замечаний нет" in capsys.readouterr().out
    (repo / "releases" / "0.N" / "0.42" / "candidates.md").write_text("> Собрано 2026-11-11 по шаблону " + "c" * 10 + ".\n")
    assert cd.main(["--repo", str(repo)]) == 2
    (repo / "releases" / "0.N" / "0.42" / "candidates.md").write_text("# без отметки сборки\n")
    assert cd.main(["--repo", str(repo)]) == 2
    assert "нет версии шаблона снимка" in capsys.readouterr().err


def test_unreleased_version_is_still_checked_against_the_live_board(tmp_path):
    repo = released_repo(tmp_path, "b" * 40, "> Собрано 2026-11-11 по шаблону " + CUT_SHA[:10] + ".\n")
    (repo / "releases" / "index.yaml").write_text(
        yaml.safe_dump({"versions": [{"version": "0.42", "state": "testing"}]}), encoding="utf-8")
    assert cd.main(["--repo", str(repo)]) == 2


def test_unrecognized_take_all_wording_is_not_read_as_zero():
    form = decisions(taken="все кандидаты", deferred="ничего")
    with pytest.raises(cd.DecisionsFormError, match="не содержит кодов"):
        cd.selected_record_keys(HANDOFF, form, CUT_SHA)


# 28.11.2026: 0.43's composition was decided in words before the cut; its keys are named at the cut,
# after candidates.md has been built from the handoff.

BEFORE_CUT = (
    "| Версия основной ветки шаблона в момент «режем» | | предложение Разработчика |\n"
    "| Состав: что взято | решение 27.11: пять возможностей и всё влитое после прошлого выпуска | |\n"
    "| Состав: что отложено | часы по направлениям — в 0.44 | |\n"
)


def test_composition_in_words_before_the_cut_waits_for_keys():
    assert cd.keys_pending(BEFORE_CUT)
    assert cd.selected_record_keys(HANDOFF, BEFORE_CUT, CUT_SHA) == (set(), 1)
    assert cd.decision_problems(HANDOFF, BEFORE_CUT, CUT_SHA) == []


def test_composition_in_words_is_refused_once_the_cut_is_named():
    named = BEFORE_CUT.replace("| | предложение Разработчика |", f"| `{CUT_SHA}` | |")
    assert not cd.keys_pending(named)
    with pytest.raises(cd.DecisionsFormError, match="не содержит кодов"):
        cd.selected_record_keys(HANDOFF, named, CUT_SHA)


def test_composition_in_words_without_the_cut_row_is_refused():
    form = BEFORE_CUT.split("\n", 1)[1]
    assert not cd.keys_pending(form)
    with pytest.raises(cd.DecisionsFormError, match="не содержит кодов"):
        cd.selected_record_keys(HANDOFF, form, CUT_SHA)


def test_keys_or_the_all_at_cut_wording_are_not_pending():
    assert not cd.keys_pending(BEFORE_CUT.replace("решение 27.11: пять возможностей и всё влитое после прошлого выпуска", "U-000001 U-000002"))
    assert not cd.keys_pending(BEFORE_CUT.replace("решение 27.11: пять возможностей и всё влитое после прошлого выпуска", cd.ALL_CUT_RECORDS))
    assert not cd.keys_pending(BEFORE_CUT.replace("решение 27.11: пять возможностей и всё влитое после прошлого выпуска", "ничего"))


def test_words_before_the_cut_pass_by_default_with_a_note(tmp_path, capsys):
    repo = repo_with(tmp_path, BEFORE_CUT)
    assert cd.main(["--repo", str(repo)]) == 0
    out = capsys.readouterr().out
    assert "замечаний нет" in out and "ключи кандидатов Выпускающий называет при нарезке" in out


def test_words_before_the_cut_do_not_pass_final(tmp_path, capsys):
    text = FILLED.replace("U-000001 U-000002", "решение 27.11: всё влитое") + "| Версия основной ветки шаблона в момент «режем» | |\n"
    repo = repo_with(tmp_path, text, {"rc.1/linux-tester.yaml": verdict()})
    assert cd.main(["--repo", str(repo), "--require-final", "--rc-tree", TREE]) == 1
    assert "нет ключей кандидатов" in capsys.readouterr().out


# 20.11.2026: a release without its own candidate list (0.42.1 while the handoff lists 0.42).

def repo_for_release(tmp_path, release, decisions_text, rc_files=None):
    base = tmp_path / "releases" / "0.N" / release
    (base / "tests").mkdir(parents=True)
    (tmp_path / "releases" / "developer-handoff.yaml").write_text(yaml.safe_dump(HANDOFF, allow_unicode=True), encoding="utf-8")
    (base / "decisions.md").write_text(decisions_text, encoding="utf-8")
    for name, body in (rc_files or {}).items():
        target = base / "tests" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(yaml.safe_dump(body, allow_unicode=True), encoding="utf-8")
    return tmp_path


def test_other_release_composition_in_words_passes_final(tmp_path, capsys):
    text = FILLED.replace("U-000001 U-000002", "всё, что в ветке выпуска на последней сборке")
    repo = repo_for_release(tmp_path, "0.42.1", text, {"rc.1/macos-tester.yaml": verdict()})
    assert cd.main(["--repo", str(repo), "--release", "0.42.1", "--require-final", "--rc-tree", TREE]) == 0
    out = capsys.readouterr().out
    assert "кандидатов 0, замечаний нет" in out and "сверен только на заполненность" in out


def test_other_release_still_requires_the_composition_row_filled(tmp_path, capsys):
    text = FILLED.replace("U-000001 U-000002", "")
    repo = repo_for_release(tmp_path, "0.42.1", text, {"rc.1/macos-tester.yaml": verdict()})
    assert cd.main(["--repo", str(repo), "--release", "0.42.1", "--require-final", "--rc-tree", TREE]) == 1
    assert "не заполнена строка «Состав: что взято" in capsys.readouterr().out


def test_own_release_words_without_keys_are_still_refused(tmp_path):
    text = FILLED.replace("U-000001 U-000002", "всё, что в ветке выпуска на последней сборке")
    repo = repo_with(tmp_path, text, {"rc.1/linux-tester.yaml": verdict()})
    assert cd.main(["--repo", str(repo), "--require-final", "--rc-tree", TREE]) == 2


# WP-529 Ф282: a deferral is a revert on the release branch; after the release merge it must come back to main.

DEFERRED_LINE = "[behavior] Новая проверка закрытия РП (#1633)."
RETURNED_CHANGELOG = f"# Changelog\n\n## [Unreleased]\n\n### Изменено\n- {DEFERRED_LINE}\n  - Как проверить: тест\n\n## [0.42.2] - 2026-11-25\n- [fix] исправление\n"
SHIPPED_ONLY_CHANGELOG = f"# Changelog\n\n## [Unreleased]\n\n## [0.42.2] - 2026-11-25\n- {DEFERRED_LINE}\n"


def deferred_key():
    return next(e["key"] for e in cd.changelog_sections(RETURNED_CHANGELOG)["Unreleased"])


def with_return_row(text, value):
    return text + f"| {cd.RETURN_ROW} | {value} |\n"


def test_deferred_record_missing_from_unreleased_is_reported():
    key = deferred_key()
    problems = cd.return_problems(with_return_row(decisions(deferred=key), "FMT #1700"), SHIPPED_ONLY_CHANGELOG, "0.42.2")
    assert problems == [
        f"{key}: отложено в 0.42.2, но в «Ещё не выпущено» основной ветки шаблона записи нет — "
        "вернуть правку (откат отката) и её запись в этот раздел"
    ]


def test_returned_record_with_filled_row_passes():
    key = deferred_key()
    assert cd.return_problems(with_return_row(decisions(deferred=key), "FMT #1700"), RETURNED_CHANGELOG, "0.42.2") == []


def test_returned_record_still_needs_the_form_row():
    problems = cd.return_problems(decisions(deferred=deferred_key()), RETURNED_CHANGELOG, "0.42.2")
    assert problems == [f"в decisions.md не заполнена строка «{cd.RETURN_ROW}»: каким запросом в шаблоне возвращено отложенное"]


def test_nothing_deferred_needs_no_return():
    assert cd.return_problems(decisions(deferred="ничего"), SHIPPED_ONLY_CHANGELOG, "0.42.2") == []


def test_deferred_in_words_only_is_a_note_not_a_pass_claim():
    assert cd.deferred_without_keys(decisions(deferred="исправление #1487: в основной ветке его не было"))
    assert not cd.deferred_without_keys(decisions(deferred="ничего"))
    assert not cd.deferred_without_keys(decisions(deferred=deferred_key()))


def test_after_release_reads_template_changelog_and_fails_on_lost_record(tmp_path, capsys):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(SHIPPED_ONLY_CHANGELOG, encoding="utf-8")
    repo = repo_with(tmp_path, with_return_row(FILLED.replace("| Состав: что отложено | |", f"| Состав: что отложено | {deferred_key()} |"), "FMT #1700"))
    other = {**HANDOFF, "release": "0.41"}  # composition of 0.42 is checked only for being filled
    (repo / "releases" / "developer-handoff.yaml").write_text(yaml.safe_dump(other, allow_unicode=True), encoding="utf-8")
    assert cd.main(["--repo", str(repo), "--release", "0.42", "--after-release", "--template-changelog", str(changelog)]) == 1
    assert "отложено в 0.42, но в «Ещё не выпущено»" in capsys.readouterr().out

    changelog.write_text(RETURNED_CHANGELOG, encoding="utf-8")
    assert cd.main(["--repo", str(repo), "--release", "0.42", "--after-release", "--template-changelog", str(changelog)]) == 0


def test_after_release_without_changelog_is_refused(tmp_path):
    with pytest.raises(SystemExit) as stop:
        cd.main(["--repo", str(tmp_path), "--after-release"])
    assert stop.value.code == 2


def test_after_release_on_a_file_without_unreleased_is_exit_two(tmp_path):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("# Changelog\n\n## [0.42.2]\n- x\n", encoding="utf-8")
    repo = repo_with(tmp_path, FILLED)
    assert cd.main(["--repo", str(repo), "--after-release", "--template-changelog", str(changelog)]) == 2
