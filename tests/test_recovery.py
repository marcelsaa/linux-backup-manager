from pathlib import Path
from unittest.mock import patch

import pytest

from lbm.core.config import AppConfig
from lbm.core.errors import RecoverySheetError
from lbm.services.recovery import RecoveryInfoService, RecoverySheetService


def make_config() -> AppConfig:
    return AppConfig.model_validate(
        {
            "system": {"host_name": "test-host"},
            "paths": {
                "log_dir": "logs",
                "state_dir": "state",
                "password_file": "/tmp/restic.pass",
            },
            "backup": {"paths": ["/home/test/Documents"], "excludes": []},
            "targets": {
                "usb": {
                    "enabled": True,
                    "label": "LinuxBackup",
                    "repository_path": "restic/test-host",
                }
            },
            "retention": {
                "keep_daily": 14,
                "keep_weekly": 8,
                "keep_monthly": 12,
                "keep_yearly": 3,
            },
        }
    )


def test_recovery_info_displays_metadata_without_password_content(
    tmp_path: Path,
    capsys,
) -> None:
    config = make_config()
    password_file = tmp_path / "restic.pass"
    password_file.write_text("never-print-this-secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    config.paths.password_file = str(password_file)
    config_file = tmp_path / "config.yaml"

    original_read_text = Path.read_text

    def reject_password_read(path: Path, *args, **kwargs) -> str:
        if path == password_file:
            raise AssertionError("recovery-info must not read the password file")
        return original_read_text(path, *args, **kwargs)

    with patch("pathlib.Path.read_text", autospec=True, side_effect=reject_password_read):
        RecoveryInfoService(config, config_file).run()

    output = capsys.readouterr().out
    assert str(config_file) in output
    assert str(password_file) in output
    assert "LinuxBackup" in output
    assert "restic/test-host" in output
    assert "Rechte 0600" in output
    assert "kann nicht wiederhergestellt werden" in output
    assert "never-print-this-secret" not in output


def test_recovery_info_reports_a_missing_password_file(tmp_path: Path, capsys) -> None:
    config = make_config()
    config.paths.password_file = str(tmp_path / "missing.pass")

    RecoveryInfoService(config, tmp_path / "config.yaml").run()

    assert "Passwortdatei-Status. FEHLT" in capsys.readouterr().out


def test_recovery_sheet_is_password_free_and_has_secure_permissions(
    tmp_path: Path,
    capsys,
) -> None:
    config = make_config()
    password_file = tmp_path / "restic.pass"
    password_file.write_text("never-copy-this-secret\n", encoding="utf-8")
    config.paths.password_file = str(password_file)
    target = tmp_path / "recovery" / "sheet.txt"
    original_read_text = Path.read_text

    def reject_password_read(path: Path, *args, **kwargs) -> str:
        if path == password_file:
            raise AssertionError("recovery-sheet must not read the password file")
        return original_read_text(path, *args, **kwargs)

    with (
        patch("builtins.input", return_value=str(target)),
        patch("pathlib.Path.read_text", autospec=True, side_effect=reject_password_read),
    ):
        created = RecoverySheetService(config, tmp_path / "config.yaml").run()

    content = target.read_text(encoding="utf-8")
    assert created is True
    assert target.stat().st_mode & 0o777 == 0o600
    assert "Dieses Dokument enthält KEIN Repository-Passwort" in content
    assert "LinuxBackup" in content
    assert "restic/test-host" in content
    assert "Aufbewahrungsort der Passwortkopie" in content
    assert "Datum des letzten erfolgreichen Restore-Tests" in content
    assert "never-copy-this-secret" not in content
    assert "Recovery Sheet erstellt" in capsys.readouterr().out


def test_recovery_sheet_does_not_overwrite_without_confirmation(
    tmp_path: Path,
    capsys,
) -> None:
    target = tmp_path / "sheet.txt"
    target.write_text("keep this content", encoding="utf-8")
    service = RecoverySheetService(make_config(), tmp_path / "config.yaml")

    with patch("builtins.input", side_effect=[str(target), "n"]):
        created = service.run()

    assert created is False
    assert target.read_text(encoding="utf-8") == "keep this content"
    assert "nicht überschrieben" in capsys.readouterr().out


def test_recovery_sheet_translates_write_errors(tmp_path: Path) -> None:
    target = tmp_path / "sheet.txt"
    service = RecoverySheetService(make_config(), tmp_path / "config.yaml")

    with (
        patch("builtins.input", return_value=str(target)),
        patch("pathlib.Path.write_text", side_effect=OSError("disk full")),
        pytest.raises(RecoverySheetError, match="nicht sicher gespeichert"),
    ):
        service.run()
