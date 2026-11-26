"""release-checklist.py: the after-release steps 7-9 are listed, and a missing row is a gap."""

import importlib.util
import subprocess
import sys
from pathlib import Path

PROGRAM = Path(__file__).parent / "release-checklist.py"
spec = importlib.util.spec_from_file_location("release_checklist", PROGRAM)
checklist = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checklist)


def test_missing_rows_are_shown_as_gaps():
    lines = checklist.post_release_lines("| Решение | Значение |\n|---|---|\n")
    assert len(lines) == 3
    assert all("— не заполнено —" in line for line in lines)


def test_filled_row_shows_its_value_and_others_stay_gaps():
    decisions = "| Табло пересобрано после выхода | 17.11.2026, запрос №65 |\n"
    lines = checklist.post_release_lines(decisions)
    assert "17.11.2026, запрос №65" in lines[2]
    assert "— не заполнено —" in lines[0] and "— не заполнено —" in lines[1]


def test_program_prints_after_release_block(tmp_path):
    release = tmp_path / "releases" / "0.N" / "0.9"
    (release / "tests" / "rc.1").mkdir(parents=True)
    (release / "protocol.md").write_text("| 1 | Проверка | да | x | y | z |\n", encoding="utf-8")
    (release / "decisions.md").write_text(
        "| Итог: выпускаем / откладываем | выпускаем |\n| Итог окна наблюдения | держим |\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(PROGRAM), "--repo", str(tmp_path), "--release", "0.9"],
        capture_output=True, text=True, check=True)
    assert "После выхода (шаги 7–9 протокола):" in result.stdout
    assert "держим" in result.stdout
    assert "8. Исправления сведены в рабочую копию Разработчика\n      — не заполнено —" in result.stdout


def checklist_with(states: dict[str, str]) -> str:
    rows = [f"| {n} | Действие | {state} | - | - | - |" for n, state in states.items()]
    return "| № | Действие | Сделано | Кто | Когда | Где видно |\n|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n"


ALL_CLOSED = {n: "да, сделано" for n in checklist.AFTER_RELEASE_ACTIONS}


def test_closure_finds_every_state_that_is_not_yes_or_not_needed():
    states = dict(ALL_CLOSED)
    states.update({"20": "частично: перенос не закончен", "25": "нет", "26": "идёт", "27": "", "19": "не нужно, отменена"})
    open_rows = checklist.closure_open_rows(checklist_with(states))
    assert [n for n, _ in open_rows] == ["20", "25", "26", "27"]


def test_closure_ignores_rows_before_the_release_and_the_merge_row():
    states = {"1г": "открыт", "15": "нет", "17": "нет", **ALL_CLOSED}
    assert checklist.closure_open_rows(checklist_with(states)) == []


def test_closure_counts_cyrillic_letter_rows_and_missing_rows_as_open():
    states = dict(ALL_CLOSED)
    states["17а"] = "нет"
    del states["28"]
    assert [n for n, _ in checklist.closure_open_rows(checklist_with(states))] == ["17а", "28"]


def test_closure_word_yes_must_stand_alone():
    states = dict(ALL_CLOSED)
    states["21"] = "данные не собраны"
    assert [n for n, _ in checklist.closure_open_rows(checklist_with(states))] == ["21"]


def test_closure_report_names_the_release_and_the_rows():
    report = checklist.closure_report("0.42.2", [("20", "частично"), ("25", "нет")])
    assert report.splitlines()[0] == "Выпуск 0.42.2 не закрыт: открыты строки 20, 25"
    assert checklist.closure_report("0.9", []).startswith("Выпуск 0.9 закрыт")


def run_closure(tmp_path, text):
    release = tmp_path / "releases" / "0.N" / "0.9"
    release.mkdir(parents=True, exist_ok=True)
    (release / "checklist.md").write_text(text, encoding="utf-8")
    return subprocess.run([sys.executable, str(PROGRAM), "--repo", str(tmp_path), "--release", "0.9", "--closure"],
                          capture_output=True, text=True)


def test_closure_program_exit_code_follows_open_rows(tmp_path):
    states = dict(ALL_CLOSED, **{"28": "нет"})
    result = run_closure(tmp_path, checklist_with(states))
    assert result.returncode == 1
    assert "Выпуск 0.9 не закрыт: открыты строки 28" in result.stdout
    assert run_closure(tmp_path, checklist_with(ALL_CLOSED)).returncode == 0


def test_closure_program_without_checklist_exits_with_two(tmp_path):
    result = subprocess.run([sys.executable, str(PROGRAM), "--repo", str(tmp_path), "--release", "0.9", "--closure"],
                            capture_output=True, text=True)
    assert result.returncode == 2
