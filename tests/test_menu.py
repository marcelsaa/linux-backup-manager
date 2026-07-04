from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, patch

from lbm.cli.menu import MainMenu
from lbm.core.errors import ConfigurationError
from lbm.services.language import LanguageService


def build_menu() -> tuple[MainMenu, Mock]:
    application = Mock()
    application.last_successful_backup.return_value = None
    menu = MainMenu(application, LanguageService("de"))
    return menu, application


def test_main_menu_backup_choice_calls_application_backup() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["1", "6"]):
        result = menu.run()

    assert result is True
    application.backup.assert_called_once_with()


def test_main_menu_restore_choice_calls_application_mount() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["2", "6"]):
        menu.run()

    application.mount.assert_called_once_with()


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


def test_expert_menu_full_restore_choice_calls_application_restore() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["5", "6", "2", "14", "7", "6"]):
        menu.run()

    application.restore.assert_called_once_with()


def test_expert_menu_migrate_choice_calls_application() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["5", "6", "6", "14", "7", "6"]):
        menu.run()

    application.migrate_repository.assert_called_once_with()


def test_expert_menu_change_password_choice_calls_application() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["5", "6", "7", "14", "7", "6"]):
        menu.run()

    application.change_password.assert_called_once_with()


def test_expert_menu_back_choice_returns_to_administration_menu() -> None:
    menu, application = build_menu()

    with patch("builtins.input", side_effect=["5", "6", "14", "1", "7", "6"]):
        menu.run()

    application.doctor.assert_called_once_with()


def test_main_menu_is_localized_in_english() -> None:
    application = Mock()
    application.last_successful_backup.return_value = None
    menu = MainMenu(application, LanguageService("en"))

    with patch("builtins.input", side_effect=["6"]) as mocked_input:
        menu.run()

    assert mocked_input.call_args.args[0] == "Choice: "


def test_main_menu_shows_no_backup_yet_when_none_recorded(capsys) -> None:
    menu, application = build_menu()
    application.last_successful_backup.return_value = None

    with patch("builtins.input", side_effect=["6"]):
        menu.run()

    assert "Noch kein Backup durchgeführt" in capsys.readouterr().out


def test_main_menu_shows_last_backup_timestamp_when_recorded(capsys) -> None:
    menu, application = build_menu()
    application.last_successful_backup.return_value = datetime.now(UTC) - timedelta(hours=2)

    with patch("builtins.input", side_effect=["6"]):
        menu.run()

    assert "Letztes Backup:" in capsys.readouterr().out


def test_main_menu_backup_summary_is_localized_in_english() -> None:
    application = Mock()
    application.last_successful_backup.return_value = None
    menu = MainMenu(application, LanguageService("en"))

    with patch("builtins.input", side_effect=["6"]):
        menu.run()

    assert "No backup has been performed yet" in menu._backup_summary()


def test_administration_menu_does_not_show_backup_summary(capsys) -> None:
    menu, application = build_menu()
    application.last_successful_backup.return_value = None

    with patch("builtins.input", side_effect=["5", "7", "6"]):
        menu.run()

    output = capsys.readouterr().out
    admin_section = output[output.index("Administration") : output.index("1) Doctor")]
    assert "Noch kein Backup durchgeführt" not in admin_section
