from pathlib import Path
from unittest.mock import patch

from lbm.core.config import AppConfig
from lbm.services.recovery import RecoveryInfoService


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

    with patch(
        "pathlib.Path.read_text",
        side_effect=AssertionError("recovery-info must not read file contents"),
    ):
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
