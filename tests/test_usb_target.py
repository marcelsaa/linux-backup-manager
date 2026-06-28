import subprocess
from unittest.mock import Mock, patch

from lbm.targets.usb import USBTarget, USBTargetInfo


def test_usb_target_info_can_be_created() -> None:
    info = USBTargetInfo(
        found=True,
        label="LinuxBackup",
        mountpoint="/media/marcel/LinuxBackup",
        fsavail="434,1G",
        fsuse_percent="0%",
        writable=True,
    )

    assert info.found is True
    assert info.label == "LinuxBackup"
    assert info.mountpoint == "/media/marcel/LinuxBackup"
    assert info.fsavail == "434,1G"
    assert info.fsuse_percent == "0%"
    assert info.writable is True


def test_probe_returns_not_found_for_invalid_lsblk_json() -> None:
    result = Mock(stdout="not-json")

    with patch("lbm.targets.usb.subprocess.run", return_value=result):
        info = USBTarget("LinuxBackup").probe()

    assert info.found is False
    assert info.mountpoint is None


def test_probe_returns_not_found_when_lsblk_fails() -> None:
    error = subprocess.CalledProcessError(1, ["lsblk"])

    with patch("lbm.targets.usb.subprocess.run", side_effect=error):
        info = USBTarget("LinuxBackup").probe()

    assert info.found is False


def test_probe_ignores_null_mountpoints() -> None:
    result = Mock(
        stdout='{"blockdevices": [{"label": "LinuxBackup", "mountpoints": [null]}]}'
    )

    with patch("lbm.targets.usb.subprocess.run", return_value=result):
        info = USBTarget("LinuxBackup").probe()

    assert info.found is True
    assert info.mountpoint is None
