"""Tests for ops/check_decisions.py (WP-529 Ф250/Ф252)."""
import importlib.util
import sys
from pathlib import Path

import yaml

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
    (tmp_path / "ops").mkdir()
    (tmp_path / "releases" / "0.42").mkdir(parents=True)
    (tmp_path / "ops" / "developer-handoff.yaml").write_text(yaml.safe_dump(HANDOFF, allow_unicode=True), encoding="utf-8")
    (tmp_path / "releases" / "0.42" / "decisions.md").write_text(decisions(taken="U-000001"), encoding="utf-8")
    assert cd.main(["--repo", str(tmp_path)]) == 1
    assert "неразделима" in capsys.readouterr().out

    (tmp_path / "releases" / "0.42" / "decisions.md").write_text(decisions(taken="U-000001 U-000002"), encoding="utf-8")
    assert cd.main(["--repo", str(tmp_path)]) == 0
    assert "замечаний нет" in capsys.readouterr().out


def test_missing_decisions_file_is_exit_two(tmp_path):
    (tmp_path / "ops").mkdir()
    (tmp_path / "ops" / "developer-handoff.yaml").write_text(yaml.safe_dump(HANDOFF), encoding="utf-8")
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
    (tmp_path / "ops").mkdir()
    (tmp_path / "releases" / "0.42" / "tests").mkdir(parents=True)
    (tmp_path / "ops" / "developer-handoff.yaml").write_text(yaml.safe_dump(HANDOFF, allow_unicode=True), encoding="utf-8")
    (tmp_path / "releases" / "0.42" / "decisions.md").write_text(decisions_text, encoding="utf-8")
    for name, body in (rc_files or {}).items():
        (tmp_path / "releases" / "0.42" / "tests" / name).write_text(yaml.safe_dump(body, allow_unicode=True), encoding="utf-8")
    return tmp_path


def verdict(**overrides):
    block = {"verdict": "STABLE", "checker": "codex-fresh-session", "report": "https://example.org/pr/1#c1", "tree": TREE}
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
    assert "нет файла отметок rc.<K>.yaml" in out


def test_final_passes_with_filled_form_and_stable_verdict(tmp_path, capsys):
    repo = repo_with(tmp_path, FILLED, {"rc.1.yaml": verdict()})
    assert cd.main(["--repo", str(repo), "--require-final", "--rc-tree", TREE]) == 0
    assert "замечаний нет" in capsys.readouterr().out


def test_final_without_rc_tree_is_refused(tmp_path, capsys):
    repo = repo_with(tmp_path, FILLED, {"rc.1.yaml": verdict()})
    assert cd.main(["--repo", str(repo), "--require-final"]) == 1
    assert "требует --rc-tree" in capsys.readouterr().out


def test_final_reads_the_newest_rc_only(tmp_path, capsys):
    repo = repo_with(tmp_path, FILLED, {"rc.1.yaml": verdict(), "rc.2.yaml": {"build": "0.42-rc.2", "marks": []}})
    assert cd.main(["--repo", str(repo), "--require-final", "--rc-tree", TREE]) == 1
    assert "rc.2.yaml: нет блока red_team" in capsys.readouterr().out


def test_blocked_and_unaccepted_caution_fail(tmp_path):
    assert any("BLOCKED" in p for p in cd.red_team_problems(repo_with(tmp_path, FILLED, {"rc.1.yaml": verdict(verdict="BLOCKED")}) / "releases" / "0.42" / "tests", None))
    other = tmp_path / "other"
    other.mkdir()
    caution = cd.red_team_problems(repo_with(other, FILLED, {"rc.1.yaml": verdict(verdict="CAUTION")}) / "releases" / "0.42" / "tests", None)
    assert any("accepted_by" in p for p in caution)


def test_verdict_for_another_tree_fails(tmp_path):
    repo = repo_with(tmp_path, FILLED, {"rc.1.yaml": verdict()})
    problems = cd.red_team_problems(repo / "releases" / "0.42" / "tests", "b" * 40)
    assert any("относится к дереву" in p for p in problems)
