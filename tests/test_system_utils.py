from pathlib import Path
from unittest.mock import Mock, patch

from lbm.utils.system import open_in_file_manager, unmount


def test_unmount_prefers_fusermount_when_available() -> None:
    fake_result = Mock()
    fake_result.returncode = 0

    with (
        patch("lbm.utils.system.shutil.which", return_value="/usr/bin/fusermount"),
        patch("lbm.utils.system.subprocess.run", return_value=fake_result) as run_mock,
    ):
        result = unmount(Path("/tmp/mount"))

    assert result is True
    args = run_mock.call_args[0][0]
    assert args == ["fusermount", "-u", "/tmp/mount"]


def test_unmount_falls_back_to_umount_when_fusermount_is_missing() -> None:
    fake_result = Mock()
    fake_result.returncode = 0

    with (
        patch("lbm.utils.system.shutil.which", return_value=None),
        patch("lbm.utils.system.subprocess.run", return_value=fake_result) as run_mock,
    ):
        result = unmount(Path("/tmp/mount"))

    assert result is True
    args = run_mock.call_args[0][0]
    assert args == ["umount", "/tmp/mount"]


def test_unmount_returns_false_on_failure() -> None:
    fake_result = Mock()
    fake_result.returncode = 1

    with (
        patch("lbm.utils.system.shutil.which", return_value="/usr/bin/fusermount"),
        patch("lbm.utils.system.subprocess.run", return_value=fake_result),
    ):
        result = unmount(Path("/tmp/mount"))

    assert result is False


def test_unmount_returns_false_when_command_is_missing() -> None:
    with (
        patch("lbm.utils.system.shutil.which", return_value=None),
        patch("lbm.utils.system.subprocess.run", side_effect=FileNotFoundError),
    ):
        result = unmount(Path("/tmp/mount"))

    assert result is False


def test_open_in_file_manager_launches_xdg_open() -> None:
    with (
        patch("lbm.utils.system.shutil.which", return_value="/usr/bin/xdg-open"),
        patch("lbm.utils.system.subprocess.Popen") as popen_mock,
    ):
        result = open_in_file_manager(Path("/tmp/mount/ids/abc123"))

    assert result is True
    args = popen_mock.call_args[0][0]
    assert args == ["xdg-open", "/tmp/mount/ids/abc123"]


def test_open_in_file_manager_returns_false_when_xdg_open_is_missing() -> None:
    with patch("lbm.utils.system.shutil.which", return_value=None):
        result = open_in_file_manager(Path("/tmp/mount/ids/abc123"))

    assert result is False
