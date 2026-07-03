from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from lbm.backup.restic import SnapshotInfo
from lbm.core.config import AppConfig
from lbm.services.restore import RestoreService


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


def ready_repository() -> Mock:
    repository = Mock()
    repository.snapshots.return_value = [
        SnapshotInfo("abc123", "28.06.2026 12:00:00", "test-host", ["/tmp/source"])
    ]
    process = Mock()
    process.poll.return_value = None

    def fake_start_mount(mountpoint: Path) -> Mock:
        (mountpoint / "ids" / "abc123").mkdir(parents=True)
        return process

    repository.start_mount.side_effect = fake_start_mount
    repository.process = process
    return repository


def test_run_mount_opens_file_manager_and_unmounts_on_exit() -> None:
    repository = ready_repository()
    provider = Mock()
    provider.get.return_value = repository

    with (
        patch("builtins.input", side_effect=["1", ""]),
        patch("lbm.services.restore.open_in_file_manager", return_value=True) as opener,
        patch("lbm.services.restore.unmount", return_value=True) as unmounter,
    ):
        result = RestoreService(make_config(), repository_provider=provider).run_mount()

    assert result is True
    opener.assert_called_once()
    assert "ids/abc123" in str(opener.call_args[0][0])
    unmounter.assert_called_once()
    repository.process.wait.assert_called_once()


def test_run_mount_reports_when_no_file_manager_is_available(capsys) -> None:
    repository = ready_repository()
    provider = Mock()
    provider.get.return_value = repository

    with (
        patch("builtins.input", side_effect=["1", ""]),
        patch("lbm.services.restore.open_in_file_manager", return_value=False),
        patch("lbm.services.restore.unmount", return_value=True),
    ):
        result = RestoreService(make_config(), repository_provider=provider).run_mount()

    assert result is True
    assert "Kein Dateimanager gefunden" in capsys.readouterr().out


def test_run_mount_fails_when_mount_process_exits_early(capsys) -> None:
    repository = Mock()
    repository.snapshots.return_value = [
        SnapshotInfo("abc123", "28.06.2026 12:00:00", "test-host", ["/tmp/source"])
    ]
    process = Mock()
    process.poll.return_value = 1
    process.stderr = Mock()
    process.stderr.read.return_value = "wrong password"
    repository.start_mount.return_value = process
    provider = Mock()
    provider.get.return_value = repository

    with patch("builtins.input", side_effect=["1"]):
        result = RestoreService(make_config(), repository_provider=provider).run_mount()

    assert result is False
    assert "wrong password" in capsys.readouterr().out


def test_run_mount_returns_false_when_no_snapshots_exist() -> None:
    repository = Mock()
    repository.snapshots.return_value = []
    provider = Mock()
    provider.get.return_value = repository

    result = RestoreService(make_config(), repository_provider=provider).run_mount()

    assert result is False


def test_run_mount_unmounts_even_on_keyboard_interrupt() -> None:
    repository = ready_repository()
    provider = Mock()
    provider.get.return_value = repository

    with (
        patch("builtins.input", side_effect=["1", KeyboardInterrupt]),
        patch("lbm.services.restore.open_in_file_manager", return_value=True),
        patch("lbm.services.restore.unmount", return_value=True) as unmounter,
        pytest.raises(KeyboardInterrupt),
    ):
        RestoreService(make_config(), repository_provider=provider).run_mount()

    unmounter.assert_called_once()
    repository.process.wait.assert_called_once()
