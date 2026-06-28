from pathlib import Path
from unittest.mock import patch

import yaml

from lbm.core.config import AppConfig
from lbm.health.checks import HealthResult
from lbm.services.doctor import DoctorService
from lbm.services.health import HealthService
from lbm.services.language import LanguageService
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
