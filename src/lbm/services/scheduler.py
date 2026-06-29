import shutil
import subprocess
import sys
from pathlib import Path

from lbm.core.config import ScheduleConfig
from lbm.services.language import LanguageService
from lbm.ui.console import Console


class SystemdScheduler:
    DAILY_SERVICE = "linux-backup-manager-daily.service"
    DAILY_TIMER = "linux-backup-manager-daily.timer"
    DUE_SERVICE = "linux-backup-manager-due.service"
    DUE_TIMER = "linux-backup-manager-due.timer"

    def __init__(
        self,
        config_file: Path,
        schedule: ScheduleConfig,
        unit_dir: Path | None = None,
        language: str = "de",
    ) -> None:
        self.config_file = config_file
        self.schedule = schedule
        self.unit_dir = unit_dir or Path.home() / ".config" / "systemd" / "user"
        self.language = LanguageService(language)

    def install(self) -> bool:
        if shutil.which("systemctl") is None:
            Console.error(self.language.translate("scheduler.systemd_missing"))
            return False

        self.unit_dir.mkdir(parents=True, exist_ok=True)
        units = {
            self.DAILY_SERVICE: self._service_content(
                "backup-scheduled", self.language.translate("scheduler.scheduled_backup")
            ),
            self.DUE_SERVICE: self._service_content(
                "backup-if-due", self.language.translate("scheduler.due_check")
            ),
            self.DAILY_TIMER: self._daily_timer_content(),
            self.DUE_TIMER: self._due_timer_content(),
        }
        for name, content in units.items():
            (self.unit_dir / name).write_text(content, encoding="utf-8")

        if not self._systemctl("daemon-reload"):
            return False
        if not self._systemctl("enable", "--now", self.DAILY_TIMER, self.DUE_TIMER):
            return False
        Console.success(self.language.translate("scheduler.enabled"))
        return True

    def remove(self) -> bool:
        self._systemctl("disable", "--now", self.DAILY_TIMER, self.DUE_TIMER)
        for name in (self.DAILY_SERVICE, self.DAILY_TIMER, self.DUE_SERVICE, self.DUE_TIMER):
            (self.unit_dir / name).unlink(missing_ok=True)
        self._systemctl("daemon-reload")
        Console.success(self.language.translate("scheduler.disabled"))
        return True

    def status(self) -> bool:
        daily_ok = self._systemctl("status", self.DAILY_TIMER, "--no-pager")
        due_ok = self._systemctl("status", self.DUE_TIMER, "--no-pager")
        return daily_ok and due_ok

    def _systemctl(self, *arguments: str) -> bool:
        result = subprocess.run(
            ["systemctl", "--user", *arguments],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            if result.stdout.strip():
                print(result.stdout.strip())
            return True
        Console.error(
            result.stderr.strip()
            or self.language.translate("scheduler.systemctl_failed")
        )
        return False

    def _service_content(self, command: str, description: str) -> str:
        return f"""[Unit]
Description=Linux Backup Manager – {description}
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
Environment=\"LBM_CONFIG_FILE={self.config_file}\"
ExecStart=\"{sys.executable}\" -m lbm {command}
"""

    def _daily_timer_content(self) -> str:
        return f"""[Unit]
Description=Linux Backup Manager – {self.language.translate("scheduler.daily_backup")}

[Timer]
OnCalendar=*-*-* {self.schedule.daily_time}:00
Unit={self.DAILY_SERVICE}

[Install]
WantedBy=timers.target
"""

    def _due_timer_content(self) -> str:
        return f"""[Unit]
Description=Linux Backup Manager – {self.language.translate("scheduler.boot_check")}

[Timer]
OnActiveSec={self.schedule.boot_delay_minutes}min
Unit={self.DUE_SERVICE}

[Install]
WantedBy=timers.target
"""
