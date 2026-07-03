from pathlib import Path

from lbm.services.language import LanguageService
from lbm.services.logs import LogViewerService


def test_log_viewer_shows_the_log_path(tmp_path: Path, capsys) -> None:
    log_file = tmp_path / "backup-manager.log"
    log_file.write_text("line 1\n", encoding="utf-8")

    LogViewerService(LanguageService("de"), log_file).run()

    assert str(log_file) in capsys.readouterr().out


def test_log_viewer_reports_no_entries_for_a_missing_file(tmp_path: Path, capsys) -> None:
    log_file = tmp_path / "missing.log"

    LogViewerService(LanguageService("de"), log_file).run()

    assert "Noch keine Log-Einträge vorhanden." in capsys.readouterr().out


def test_log_viewer_reports_no_entries_for_an_empty_file(tmp_path: Path, capsys) -> None:
    log_file = tmp_path / "backup-manager.log"
    log_file.write_text("", encoding="utf-8")

    LogViewerService(LanguageService("de"), log_file).run()

    assert "Noch keine Log-Einträge vorhanden." in capsys.readouterr().out


def test_log_viewer_shows_only_the_last_lines(tmp_path: Path, capsys) -> None:
    log_file = tmp_path / "backup-manager.log"
    log_file.write_text("\n".join(f"line {i}" for i in range(1, 51)) + "\n", encoding="utf-8")

    LogViewerService(LanguageService("de"), log_file).run()

    output = capsys.readouterr().out
    assert "line 1\n" not in output
    assert "line 11" in output
    assert "line 50" in output
    assert "Letzte 40 Zeile(n):" in output


def test_log_viewer_is_localized_in_english(tmp_path: Path, capsys) -> None:
    log_file = tmp_path / "missing.log"

    LogViewerService(LanguageService("en"), log_file).run()

    assert "No log entries yet." in capsys.readouterr().out
