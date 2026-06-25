from lbm.targets.usb import USBTargetInfo


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