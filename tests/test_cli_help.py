from unittest.mock import patch

import pytest

from lbm.cli.main import CommandLineInterface
from lbm.ui.console import Console


def test_help_flag_exits_with_code_zero() -> None:
    cli = CommandLineInterface()

    with patch("sys.argv", ["backup-manager", "-h"]), pytest.raises(SystemExit) as excinfo:
        cli.run()

    assert excinfo.value.code == 0


def test_long_help_flag_exits_with_code_zero() -> None:
    cli = CommandLineInterface()

    with patch("sys.argv", ["backup-manager", "--help"]), pytest.raises(SystemExit) as excinfo:
        cli.run()

    assert excinfo.value.code == 0


def test_help_output_contains_both_language_headings(capsys) -> None:
    cli = CommandLineInterface()

    with patch("sys.argv", ["backup-manager", "-h"]), pytest.raises(SystemExit):
        cli.run()

    output = capsys.readouterr().out
    assert "Befehle (Deutsch):" in output
    assert "Commands (English):" in output


def test_help_output_contains_descriptions_in_both_languages(capsys) -> None:
    cli = CommandLineInterface()

    with patch("sys.argv", ["backup-manager", "-h"]), pytest.raises(SystemExit):
        cli.run()

    output = capsys.readouterr().out
    assert "Neues Backup erstellen" in output
    assert "Create a new backup" in output


def test_help_output_uses_distinct_colors_per_language(capsys) -> None:
    cli = CommandLineInterface()

    with patch("sys.argv", ["backup-manager", "-h"]), pytest.raises(SystemExit):
        cli.run()

    output = capsys.readouterr().out
    assert Console.CYAN in output
    assert Console.MAGENTA in output


def test_help_flag_takes_precedence_over_invalid_argument() -> None:
    cli = CommandLineInterface()

    with (
        patch("sys.argv", ["backup-manager", "-h", "--unknown"]),
        pytest.raises(SystemExit) as excinfo,
    ):
        cli.run()

    assert excinfo.value.code == 0
