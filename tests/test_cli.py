from pathlib import Path
from unittest.mock import Mock, patch

from lbm.cli.main import CommandLineInterface, _configured_language, main
from lbm.core.errors import ConfigurationError


def test_non_interactive_setup_is_forwarded_to_application() -> None:
    application = Mock()
    application.setup.return_value = True
    cli = CommandLineInterface()
    cli.application = application

    with patch("sys.argv", ["backup-manager", "setup", "--non-interactive"]):
        cli.run()

    application.setup.assert_called_once_with(interactive=False)


def test_recovery_info_is_forwarded_to_application() -> None:
    application = Mock()
    cli = CommandLineInterface()
    cli.application = application

    with patch("sys.argv", ["backup-manager", "recovery-info"]):
        cli.run()

    application.recovery_info.assert_called_once_with()


def test_doctor_is_forwarded_to_application() -> None:
    application = Mock()
    application.doctor.return_value = True
    cli = CommandLineInterface()
    cli.application = application

    with patch("sys.argv", ["backup-manager", "doctor"]):
        result = cli.run()

    assert result is True
    application.doctor.assert_called_once_with()


def test_recovery_sheet_is_forwarded_to_application() -> None:
    application = Mock()
    application.recovery_sheet.return_value = True
    cli = CommandLineInterface()
    cli.application = application

    with patch("sys.argv", ["backup-manager", "recovery-sheet"]):
        result = cli.run()

    assert result is True
    application.recovery_sheet.assert_called_once_with()


def test_configured_language_falls_back_to_detected_language_for_broken_config(
    tmp_path: Path, monkeypatch
) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text("system:\n  language: en\n", encoding="utf-8")
    monkeypatch.setenv("LBM_CONFIG_FILE", str(config_file))

    language = _configured_language()

    assert language.language == "en"


def test_configured_language_defaults_to_german_when_language_cannot_be_detected(
    tmp_path: Path, monkeypatch
) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text("not valid yaml: [", encoding="utf-8")
    monkeypatch.setenv("LBM_CONFIG_FILE", str(config_file))

    language = _configured_language()

    assert language.language == "de"


def test_main_returns_nonzero_for_an_application_error() -> None:
    with (
        patch("lbm.cli.main.setup_logging"),
        patch(
            "lbm.cli.main.CommandLineInterface.run",
            side_effect=ConfigurationError("invalid config"),
        ),
    ):
        exit_code = main()

    assert exit_code == 1


def test_main_returns_nonzero_when_noninteractive_setup_is_incomplete() -> None:
    with (
        patch("lbm.cli.main.setup_logging"),
        patch("lbm.cli.main.CommandLineInterface.run", return_value=False),
    ):
        exit_code = main()

    assert exit_code == 1


def test_main_handles_ended_interactive_input_without_traceback(capsys) -> None:
    with (
        patch("lbm.cli.main.setup_logging"),
        patch("lbm.cli.main.CommandLineInterface.run", side_effect=EOFError),
    ):
        exit_code = main()

    assert exit_code == 1
    assert "Eingabe wurde beendet" in capsys.readouterr().out
