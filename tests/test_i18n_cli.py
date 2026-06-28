from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from lbm.backup.restic import (
    BackupResult,
    RepositoryStats,
    ResticRepositoryInfo,
    SnapshotInfo,
)
from lbm.cli.main import CommandLineInterface
from lbm.core.application import Application
from lbm.core.config import AppConfig
from lbm.core.state import BackupStateStore
from lbm.health.checks import HealthResult
from lbm.services.backup import BackupService
from lbm.services.doctor import DoctorService
from lbm.services.health import HealthService
from lbm.services.language import LanguageService
from lbm.services.recovery import RecoveryInfoService, RecoverySheetService
from lbm.services.repository import RepositoryDestination
from lbm.services.repository_maintenance import RepositoryMaintenanceService
from lbm.services.restore import RestoreService
from lbm.services.status import StatusService
from lbm.setup.wizard import SetupWizard
from lbm.targets.usb import USBTargetInfo


def english_config(tmp_path: Path) -> AppConfig:
    return AppConfig.model_validate(
        {
            "system": {"host_name": "test-host", "language": "en"},
            "paths": {
                "log_dir": "logs",
                "state_dir": str(tmp_path / "state"),
                "password_file": str(tmp_path / "restic.pass"),
            },
            "backup": {"paths": [str(tmp_path)], "excludes": []},
            "targets": {
                "usb": {
                    "enabled": True,
                    "label": "TestUSB",
                    "repository_path": "restic/test-host",
                }
            },
            "retention": {
                "keep_daily": 7,
                "keep_weekly": 4,
                "keep_monthly": 3,
                "keep_yearly": 1,
            },
        }
    )


def test_status_output_is_english(tmp_path: Path, capsys) -> None:
    config = english_config(tmp_path)
    config_file = tmp_path / "config.yaml"
    config_file.touch()

    with patch("lbm.services.status.shutil.which", return_value=None):
        StatusService(config, config_file).run()

    output = capsys.readouterr().out
    assert "Configuration" in output
    assert "Password file" in output
    assert "Automatic backups" in output
    assert "Last backup" in output
    assert "Konfiguration" not in output


def test_health_output_is_english(tmp_path: Path, capsys) -> None:
    config = english_config(tmp_path)

    with (
        patch(
            "lbm.services.health.HealthChecker.run",
            return_value=[HealthResult("Password file", False, "missing")],
        ),
        patch("lbm.services.health.RepositoryProvider.get_all", return_value=[]),
    ):
        HealthService(config).run()

    output = capsys.readouterr().out
    assert "Backup targets" in output
    assert "Not all targets are available" in output
    assert "Overall status" in output and "ERROR" in output
    assert "Backup-Ziele" not in output


def test_doctor_output_is_english(tmp_path: Path, capsys) -> None:
    config = english_config(tmp_path)
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        yaml.safe_dump(config.model_dump(), sort_keys=False),
        encoding="utf-8",
    )

    with (
        patch(
            "lbm.services.doctor.HealthChecker.check_restic",
            return_value=HealthResult("Restic", True, "restic test"),
        ),
        patch(
            "lbm.services.doctor.USBTarget.probe",
            return_value=USBTargetInfo(False, "TestUSB", None, None, None, False),
        ),
    ):
        DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert "Configuration" in output
    assert "Password file" in output
    assert "not found" in output
    assert "Last backup" in output
    assert "No repairs or configuration changes were performed" in output
    assert "Passwortdatei" not in output


def test_setup_interactions_are_english(tmp_path: Path, capsys) -> None:
    wizard = SetupWizard(tmp_path / "config.yaml")
    wizard.language = LanguageService("en")
    data = {
        "targets": {
            "usb": {
                "enabled": True,
                "label": "TestUSB",
                "repository_path": "restic/test",
            },
            "nas": {
                "enabled": False,
                "mount_path": "/mnt/nas",
                "repository_path": "restic/test",
            },
        },
        "schedule": {
            "enabled": True,
            "daily_time": "20:00",
            "interval_days": 1,
        },
    }
    prompts: list[str] = []
    answers = iter(["y", "n", "", "", "y", "21:00", "2", "n"])

    def answer(prompt: str) -> str:
        prompts.append(prompt)
        return next(answers)

    with patch("builtins.input", side_effect=answer):
        wizard._print_header()
        wizard._configure_targets(data)
        wizard._configure_schedule(data)
        wizard._create_password_file()

    output = capsys.readouterr().out
    prompt_text = "\n".join(prompts)
    assert "Welcome to the setup wizard" in output
    assert "Which backup targets should be used" in output
    assert "Use a USB drive? [Y/n]" in prompt_text
    assert "Enable automatic backups? [Y/n]" in prompt_text
    assert "repository password cannot be recovered" in output
    assert "I understand the potential data loss" in prompt_text
    assert "Welche Backup-Ziele" not in output


def test_fresh_setup_selects_language_before_header(tmp_path: Path, capsys) -> None:
    wizard = SetupWizard(tmp_path / "config.yaml")

    with patch("builtins.input", return_value="en") as user_input:
        wizard._select_initial_language()
        wizard._print_header()

    prompt = user_input.call_args.args[0]
    output = capsys.readouterr().out
    assert "Language" in prompt and "Sprache" in prompt
    assert "Language selected: en" in output
    assert "Welcome to the setup wizard" in output


def test_backup_output_is_english(tmp_path: Path, capsys) -> None:
    config = english_config(tmp_path)
    repository = Mock()
    repository.check.return_value = ResticRepositoryInfo(True, "ready")
    repository.backup.return_value = BackupResult(
        True, "abc123", 1, 2, 3, 6, "10 MiB", "0:01", "ok"
    )
    provider = Mock()
    provider.get_all.return_value = [RepositoryDestination("NAS", repository)]

    assert BackupService(config, provider).run() is True

    output = capsys.readouterr().out
    assert "Starting backup of the following paths" in output
    assert "Backup successful" in output
    assert "New files" in output
    assert "Neue Dateien" not in output


def test_restore_output_is_english(tmp_path: Path, capsys) -> None:
    config = english_config(tmp_path)
    repository = Mock()
    repository.snapshots.return_value = [
        SnapshotInfo("abc123", "28.06.2026 12:00:00", "test-host", ["/tmp/source"])
    ]
    repository.restore.return_value = BackupResult(
        True, "abc123", 0, 0, 0, 0, "", "", "ok"
    )
    provider = Mock()
    provider.get.return_value = repository

    with patch("builtins.input", side_effect=["1", "", "y"]):
        RestoreService(config, repository_provider=provider).run()

    output = capsys.readouterr().out
    assert "Available snapshots" in output
    assert "Selected snapshot" in output
    assert "Target directory" in output
    assert "Restore successful" in output


def test_maintenance_output_is_english(tmp_path: Path, capsys) -> None:
    config = english_config(tmp_path)
    repository = Mock()
    repository.snapshots.return_value = [
        SnapshotInfo("abc123", "28.06.2026 12:00:00", "test-host", ["/tmp/source"])
    ]
    repository.stats.return_value = RepositoryStats(
        1, "28.06.2026 12:00:00", "28.06.2026 12:00:00", "test-host"
    )
    repository.check_repository.return_value = ResticRepositoryInfo(True, "ok")
    provider = Mock()
    provider.get.return_value = repository
    service = RepositoryMaintenanceService(config, provider)

    service.snapshots()
    service.stats()
    service.check()

    output = capsys.readouterr().out
    assert "Snapshot count: 1" in output
    assert "Repository statistics" in output
    assert "First snapshot" in output
    assert "Repository check successful" in output


def test_recovery_outputs_are_english(tmp_path: Path, capsys) -> None:
    config = english_config(tmp_path)
    password_file = Path(config.paths.password_file)
    password_file.write_text("secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    config_file = tmp_path / "config.yaml"
    sheet = tmp_path / "sheet.txt"

    RecoveryInfoService(config, config_file).run()
    with patch("builtins.input", return_value=str(sheet)):
        RecoverySheetService(config, config_file).run()

    output = capsys.readouterr().out
    content = sheet.read_text(encoding="utf-8")
    assert "Recovery information" in output
    assert "Important files" in output
    assert "The recovery sheet deliberately contains no password" in output
    assert "IMPORTANT: This document contains NO repository password" in content
    assert "EMERGENCY PROCEDURE" in content


def test_due_message_and_cli_help_are_english(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    config = english_config(tmp_path)
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        yaml.safe_dump(config.model_dump(), sort_keys=False), encoding="utf-8"
    )
    BackupStateStore(tmp_path / "state").record_success()
    application = Application()
    application.config = config

    assert application.backup_if_due() is True

    monkeypatch.setenv("LBM_CONFIG_FILE", str(config_file))
    with (
        patch("sys.argv", ["backup-manager", "--help"]),
        pytest.raises(SystemExit, match="0"),
    ):
        CommandLineInterface().run()

    output = capsys.readouterr().out
    assert "Backup is not due yet" in output
    assert "command to execute" in output
    assert "Do not perform interactive changes" in output
