from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from lbm.backup.restic import ResticRepositoryInfo
from lbm.core.config import AppConfig, ConfigLoader
from lbm.services.repository import RepositoryDestination
from lbm.setup.wizard import SetupWizard


def target_config() -> dict:
    return {
        "targets": {
            "usb": {
                "enabled": True,
                "label": "LinuxBackup",
                "repository_path": "restic/default",
            },
            "nas": {
                "enabled": False,
                "mount_path": "/mnt/backup-nas",
                "repository_path": "restic/default",
            },
        }
    }


def app_config() -> AppConfig:
    return AppConfig.model_validate(
        {
            "system": {"host_name": "test"},
            "paths": {
                "log_dir": "logs",
                "state_dir": "state",
                "password_file": "/tmp/password",
            },
            "backup": {"paths": ["/tmp/source"], "excludes": []},
            "targets": {
                "usb": {
                    "enabled": True,
                    "label": "TestUSB",
                    "repository_path": "usb-repository",
                },
                "nas": {
                    "enabled": True,
                    "mount_path": "/mnt/test-nas",
                    "repository_path": "nas-repository",
                },
            },
            "retention": {
                "keep_daily": 7,
                "keep_weekly": 4,
                "keep_monthly": 3,
                "keep_yearly": 1,
            },
        }
    )


def test_configure_targets_supports_usb_and_nas() -> None:
    data = target_config()
    answers = iter(["", "j", "TestUSB", "restic/usb", "/mnt/test-nas", "restic/nas"])

    with patch("builtins.input", side_effect=lambda _: next(answers)):
        SetupWizard(Path("/tmp/config.yaml"))._configure_targets(data)

    assert data["targets"]["usb"] == {
        "enabled": True,
        "label": "TestUSB",
        "repository_path": "restic/usb",
    }
    assert data["targets"]["nas"] == {
        "enabled": True,
        "mount_path": "/mnt/test-nas",
        "repository_path": "restic/nas",
    }


def test_configure_targets_requires_at_least_one_target() -> None:
    data = target_config()
    answers = iter(["n", "n", "", "n", "", ""])

    with patch("builtins.input", side_effect=lambda _: next(answers)):
        SetupWizard(Path("/tmp/config.yaml"))._configure_targets(data)

    assert data["targets"]["usb"]["enabled"] is True
    assert data["targets"]["nas"]["enabled"] is False


def test_check_repositories_initializes_all_destinations() -> None:
    first = Mock()
    first.check.return_value = ResticRepositoryInfo(False, "missing")
    first.init_repository.return_value = ResticRepositoryInfo(True, "created")
    second = Mock()
    second.check.return_value = ResticRepositoryInfo(False, "missing")
    second.init_repository.return_value = ResticRepositoryInfo(True, "created")
    destinations = [
        RepositoryDestination("USB: TestUSB", first),
        RepositoryDestination("NAS: /mnt/test-nas", second),
    ]
    wizard = SetupWizard(Path("/tmp/config.yaml"))
    wizard.config = app_config()

    with (
        patch("lbm.setup.wizard.RepositoryProvider.get_all", return_value=destinations),
        patch("builtins.input", side_effect=["", ""]),
    ):
        result = wizard._check_repositories()

    assert result is True
    first.init_repository.assert_called_once_with()
    second.init_repository.assert_called_once_with()


def test_first_run_writes_a_valid_usb_configuration(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    wizard = SetupWizard(config_file)
    answers = [
        "",  # create configuration
        "",  # include documents
        "n",
        "n",
        "n",
        "n",
        "",  # no additional path
        "",  # use USB
        "n",  # do not use NAS
        "TestUSB",
        "restic/test",
        "",  # enable automatic backups
        "",  # default 20:00
        "",  # default daily interval
    ]

    with patch("builtins.input", side_effect=answers):
        created = wizard._check_config()

    assert created is True
    config = ConfigLoader(config_file).load()
    assert config.backup.paths == ["~/Dokumente"]
    assert config.targets.usb.enabled is True
    assert config.targets.usb.label == "TestUSB"
    assert config.targets.usb.repository_path == "restic/test"
    assert config.targets.nas.enabled is False
    assert config.schedule.enabled is True
    assert config.schedule.daily_time == "20:00"
    assert config.schedule.interval_days == 1


def test_config_model_rejects_disabled_usb_and_nas() -> None:
    data = app_config().model_dump()
    data["targets"]["usb"]["enabled"] = False
    data["targets"]["nas"]["enabled"] = False

    with pytest.raises(ValueError, match="at least one backup target"):
        AppConfig.model_validate(data)


def test_configure_schedule_accepts_custom_time_and_interval() -> None:
    data = {
        "schedule": {
            "enabled": True,
            "daily_time": "20:00",
            "interval_days": 1,
            "boot_delay_minutes": 2,
        }
    }

    with patch("builtins.input", side_effect=["", "18:30", "7"]):
        SetupWizard(Path("/tmp/config.yaml"))._configure_schedule(data)

    assert data["schedule"]["enabled"] is True
    assert data["schedule"]["daily_time"] == "18:30"
    assert data["schedule"]["interval_days"] == 7
