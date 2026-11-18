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
