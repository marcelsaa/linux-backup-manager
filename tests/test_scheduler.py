from pathlib import Path
from unittest.mock import Mock, patch

from lbm.core.config import ScheduleConfig
from lbm.services.scheduler import SystemdScheduler


def test_scheduler_writes_daily_and_boot_timer(tmp_path: Path) -> None:
    scheduler = SystemdScheduler(
        Path("/home/test/.config/linux-backup-manager/config.yaml"),
        ScheduleConfig(
            enabled=True,
            daily_time="20:00",
            interval_days=1,
            boot_delay_minutes=2,
        ),
        unit_dir=tmp_path,
    )
    process = Mock(returncode=0, stdout="", stderr="")

    with (
        patch("lbm.services.scheduler.shutil.which", return_value="/usr/bin/systemctl"),
        patch("lbm.services.scheduler.subprocess.run", return_value=process) as run,
    ):
        installed = scheduler.install()

    assert installed is True
    daily_service = (tmp_path / scheduler.DAILY_SERVICE).read_text(encoding="utf-8")
    due_service = (tmp_path / scheduler.DUE_SERVICE).read_text(encoding="utf-8")
    daily_timer = (tmp_path / scheduler.DAILY_TIMER).read_text(encoding="utf-8")
    due_timer = (tmp_path / scheduler.DUE_TIMER).read_text(encoding="utf-8")
    assert "backup-scheduled" in daily_service
    assert "backup-if-due" in due_service
    assert "LBM_CONFIG_FILE=/home/test/.config/linux-backup-manager/config.yaml" in due_service
    assert "OnCalendar=*-*-* 20:00:00" in daily_timer
    assert "OnActiveSec=2min" in due_timer
    assert "OnBootSec=" not in due_timer
    assert run.call_count == 2


def test_scheduler_reports_missing_systemd(tmp_path: Path) -> None:
    scheduler = SystemdScheduler(
        Path("/tmp/config.yaml"),
        ScheduleConfig(enabled=True),
        unit_dir=tmp_path,
    )

    with patch("lbm.services.scheduler.shutil.which", return_value=None):
        assert scheduler.install() is False
