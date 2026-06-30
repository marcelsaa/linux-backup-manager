from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from lbm.backup.restic import RepositoryStatus, ResticRepositoryInfo
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

    with (
        patch("builtins.input", side_effect=lambda _: next(answers)),
        patch.object(SetupWizard, "_selected_targets_available", return_value=True),
    ):
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

    with (
        patch("builtins.input", side_effect=lambda _: next(answers)),
        patch.object(SetupWizard, "_selected_targets_available", return_value=True),
    ):
        SetupWizard(Path("/tmp/config.yaml"))._configure_targets(data)

    assert data["targets"]["usb"]["enabled"] is True
    assert data["targets"]["nas"]["enabled"] is False


def test_unavailable_nas_can_be_corrected_during_configuration(tmp_path: Path) -> None:
    data = target_config()
    valid_nas = tmp_path / "nas"
    valid_nas.mkdir()
    answers = [
        "n", "j", str(tmp_path / "missing"), "repository", "",
        "n", "j", str(valid_nas), "repository",
    ]

    with patch("builtins.input", side_effect=answers):
        configured = SetupWizard(tmp_path / "config.yaml")._configure_targets(data)

    assert configured is True
    assert data["targets"]["usb"]["enabled"] is False
    assert data["targets"]["nas"]["mount_path"] == str(valid_nas)


def test_unavailable_usb_can_cancel_target_configuration(tmp_path: Path) -> None:
    data = target_config()
    missing = Mock(found=False, mountpoint=None, writable=False)

    with (
        patch("builtins.input", side_effect=["", "n", "MissingUSB", "repository", "n"]),
        patch("lbm.setup.wizard.USBTarget.probe", return_value=missing),
    ):
        configured = SetupWizard(tmp_path / "config.yaml")._configure_targets(data)

    assert configured is False


def test_check_repositories_initializes_all_destinations() -> None:
    first = Mock()
    first.check.return_value = ResticRepositoryInfo(
        False,
        "missing",
        RepositoryStatus.MISSING,
    )
    first.init_repository.return_value = ResticRepositoryInfo(True, "created")
    second = Mock()
    second.check.return_value = ResticRepositoryInfo(
        False,
        "missing",
        RepositoryStatus.MISSING,
    )
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
        "",  # keep German language
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
        "",  # confirm summary
    ]

    with (
        patch("builtins.input", side_effect=answers),
        patch.object(SetupWizard, "_selected_targets_available", return_value=True),
        patch("lbm.setup.wizard.gethostname", return_value="fresh-host"),
    ):
        created = wizard._check_config()

    assert created is True
    config = ConfigLoader(config_file).load()
    assert config.backup.paths == ["~/Dokumente"]
    assert config.system.language == "de"
    assert config.system.host_name == "fresh-host"
    assert config.targets.usb.enabled is True
    assert config.targets.usb.label == "TestUSB"
    assert config.targets.usb.repository_path == "restic/test"
    assert config.targets.nas.enabled is False
    assert config.schedule.enabled is True
    assert config.schedule.daily_time == "20:00"
    assert config.schedule.interval_days == 1


def test_existing_configuration_can_be_edited_with_backup(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    data = app_config().model_dump()
    data["backup"]["paths"] = ["~/Dokumente", "/tmp/source"]
    data["targets"]["nas"]["enabled"] = False
    data["checks"] = {"restic_check_interval_days": 30}
    original = yaml.safe_dump(data, sort_keys=False)
    config_file.write_text(original, encoding="utf-8")
    answers = [
        "j",  # edit existing configuration
        "en",  # switch language
        "n",  # remove documents
        "",  # images remain disabled
        "",  # desktop remains disabled
        "",  # downloads remain disabled
        "j",  # add projects
        "n",  # remove custom /tmp/source
        "/tmp/new-source",
        "",  # finish custom paths
        "",  # keep USB enabled
        "",  # keep NAS disabled
        "TestUSB",
        "usb-production",
        "",  # keep schedule disabled
        "",  # confirm summary
    ]

    with (
        patch("builtins.input", side_effect=answers),
        patch.object(SetupWizard, "_selected_targets_available", return_value=True),
    ):
        edited = SetupWizard(config_file)._check_config()

    assert edited is True
    assert (tmp_path / "config.yaml.bak").read_text(encoding="utf-8") == original
    saved_data = yaml.safe_load(config_file.read_text(encoding="utf-8"))
    assert saved_data["backup"]["paths"] == ["~/Projekte", "/tmp/new-source"]
    assert saved_data["system"]["language"] == "en"
    assert saved_data["targets"]["usb"]["repository_path"] == "usb-production"
    assert saved_data["checks"] == {"restic_check_interval_days": 30}


def test_wrong_repository_password_is_not_treated_as_missing() -> None:
    repository = Mock()
    repository.check.return_value = ResticRepositoryInfo(
        False,
        "Fatal: wrong password or no key found",
        RepositoryStatus.WRONG_PASSWORD,
    )
    wizard = SetupWizard(Path("/tmp/config.yaml"))

    result = wizard._check_repository(RepositoryDestination("USB: TestUSB", repository))

    assert result is False
    repository.init_repository.assert_not_called()


def test_password_creation_requires_recovery_warning_confirmation(tmp_path: Path) -> None:
    wizard = SetupWizard(tmp_path / "config.yaml")
    wizard.password_file = tmp_path / "restic.pass"

    with (
        patch("builtins.input", return_value="n"),
        patch("lbm.setup.wizard.getpass") as getpass,
    ):
        created = wizard._create_password_file()

    assert created is False
    assert not wizard.password_file.exists()
    getpass.assert_not_called()


def test_confirmed_password_creation_uses_secure_file_permissions(tmp_path: Path) -> None:
    wizard = SetupWizard(tmp_path / "config.yaml")
    wizard.password_file = tmp_path / "restic.pass"

    with (
        patch("builtins.input", return_value="j"),
        patch("lbm.setup.wizard.getpass", side_effect=["secure-password", "secure-password"]),
    ):
        created = wizard._create_password_file()

    assert created is True
    assert wizard.password_file.stat().st_mode & 0o777 == 0o600


def test_incomplete_repository_setup_does_not_install_scheduler(tmp_path: Path) -> None:
    wizard = SetupWizard(tmp_path / "config.yaml")

    with (
        patch.object(wizard, "_detect_language"),
        patch.object(wizard, "_select_initial_language"),
        patch.object(wizard, "_print_header"),
        patch.object(wizard, "_check_config", return_value=True),
        patch.object(wizard, "_load_setup_config", return_value=True),
        patch.object(wizard, "_check_password", return_value=True),
        patch.object(wizard, "_check_programs", return_value=True),
        patch.object(wizard, "_check_repositories", return_value=False),
        patch.object(wizard, "_check_scheduler") as scheduler,
    ):
        result = wizard.run()

    assert result is False
    scheduler.assert_not_called()


def test_english_configuration_summary_lists_all_decisions(
    tmp_path: Path,
    capsys,
) -> None:
    wizard = SetupWizard(tmp_path / "config.yaml")
    wizard.language = wizard.language.__class__("en")
    data = app_config().model_dump()
    data["system"]["host_name"] = "fresh-host"
    data["targets"]["usb"]["enabled"] = False

    wizard._print_configuration_summary(data)

    output = capsys.readouterr().out
    assert "Configuration summary" in output
    assert "Host: fresh-host" in output
    assert "Backup paths:" in output
    assert "NAS target: /mnt/test-nas" in output
    assert "Schedule: disabled" in output


def test_config_model_rejects_disabled_usb_and_nas() -> None:
    data = app_config().model_dump()
    data["targets"]["usb"]["enabled"] = False
    data["targets"]["nas"]["enabled"] = False

    with pytest.raises(ValueError, match="at least one backup target"):
        AppConfig.model_validate(data)


def test_existing_config_without_language_defaults_to_german() -> None:
    data = app_config().model_dump()
    del data["system"]["language"]

    config = AppConfig.model_validate(data)

    assert config.system.language == "de"


def test_configure_language_rejects_unknown_value_and_accepts_english(
    capsys,
) -> None:
    data = {"system": {"host_name": "test", "language": "de"}}

    with patch("builtins.input", side_effect=["fr", "en"]):
        SetupWizard(Path("/tmp/config.yaml"))._configure_language(data)

    assert data["system"]["language"] == "en"
    output = capsys.readouterr().out
    assert "Bitte 'de' oder 'en' eingeben" in output
    assert "Language selected: en" in output


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
