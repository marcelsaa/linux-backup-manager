from unittest.mock import Mock, patch

from lbm.cli.menu import MainMenu
from lbm.core.errors import ConfigurationError
from lbm.services.language import LanguageService


def build_menu() -> tuple[MainMenu, Mock]:
    application = Mock()
    menu = MainMenu(application, LanguageService("de"))
    return menu, application


def test_main_menu_backup_choice_calls_application_backup() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["1", "6"]):
        result = menu.run()

    assert result is True
    application.backup.assert_called_once_with()


def test_main_menu_restore_choice_calls_application_restore() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["2", "6"]):
        menu.run()

    application.restore.assert_called_once_with()


def test_main_menu_status_choice_calls_application_status() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["3", "6"]):
        menu.run()

    application.status.assert_called_once_with()


def test_main_menu_settings_choice_calls_application_settings() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["4", "6"]):
        menu.run()

    application.settings.assert_called_once_with()


def test_main_menu_invalid_choice_is_reported_and_menu_continues(capsys) -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["abc", "99", "6"]):
        result = menu.run()

    assert result is True
    output = capsys.readouterr().out
    assert output.count("Ungültige Auswahl.") == 2
    application.backup.assert_not_called()


def test_main_menu_application_error_is_shown_and_menu_continues(capsys) -> None:
    menu, application = build_menu()
    application.backup.side_effect = ConfigurationError("Konfigurationsdatei nicht gefunden.")

    with patch("builtins.input", side_effect=["1", "6"]):
        result = menu.run()

    assert result is True
    assert "Konfigurationsdatei nicht gefunden." in capsys.readouterr().out


def test_administration_menu_doctor_choice_calls_application_doctor() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["5", "1", "7", "6"]):
        menu.run()

    application.doctor.assert_called_once_with()


def test_administration_menu_logs_choice_calls_application_view_logs() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["5", "3", "7", "6"]):
        menu.run()

    application.view_logs.assert_called_once_with()


def test_administration_menu_history_choice_calls_application_snapshots() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["5", "4", "7", "6"]):
        menu.run()

    application.snapshots.assert_called_once_with()


def test_administration_menu_repository_info_choice_calls_recovery_info() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["5", "5", "7", "6"]):
        menu.run()

    application.recovery_info.assert_called_once_with()


def test_administration_menu_back_choice_returns_to_main_menu() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["5", "7", "3", "6"]):
        result = menu.run()

    assert result is True
    application.status.assert_called_once_with()


def test_expert_menu_change_password_choice_calls_application() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["5", "6", "5", "12", "7", "6"]):
        menu.run()

    application.change_password.assert_called_once_with()


def test_expert_menu_back_choice_returns_to_administration_menu() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["5", "6", "12", "1", "7", "6"]):
        menu.run()

    application.doctor.assert_called_once_with()


def test_main_menu_is_localized_in_english() -> None:
    application = Mock()
    menu = MainMenu(application, LanguageService("en"))

    with patch("builtins.input", side_effect=["6"]) as mocked_input:
        menu.run()

    assert mocked_input.call_args.args[0] == "Choice: "
