import platform
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path

from lbm import __version__
from lbm.core.config import AppConfig
from lbm.core.state import BackupStateStore
from lbm.services.language import LanguageService


class StatusService:
    def __init__(self, config: AppConfig, config_file: Path) -> None:
        self.config = config
        self.config_file = config_file
        self.language = LanguageService(config.system.language)

    def run(self) -> None:
        password_file = Path(self.config.paths.password_file).expanduser()

        title = self.language.translate("app.title")
        print(title)
        print(self.language.translate("status.version", version=__version__))
        print("=" * len(title))
        print()
        self._heading("status.system")
        self._line("status.python", platform.python_version())
        self._line(
            "status.restic",
            self.language.translate(
                "common.ok" if shutil.which("restic") else "common.missing_upper"
            ),
        )
        print()
        self._heading("status.configuration")
        self._line("status.file", self.config_file)
        self._line(
            "status.configuration",
            self.language.translate(
                "common.ok" if self.config_file.exists() else "common.missing_upper"
            ),
        )
        self._line("status.host", self.config.system.host_name)
        self._line("status.language", self.config.system.language)
        print()
        self._heading("status.security")
        self._line(
            "status.password_file",
            self.language.translate(
                "common.ok" if password_file.exists() else "common.missing_upper"
            ),
        )
        self._line("status.path", password_file)
        print()
        self._heading("status.automatic_backups")
        self._line(
            "status.enabled",
            self.language.translate(
                "common.yes_upper" if self.config.schedule.enabled else "common.no_upper"
            ),
        )
        self._line(
            "status.check_time",
            self.language.translate(
                "status.time_value", time=self.config.schedule.daily_time
            ),
        )
        self._line(
            "status.interval",
            self.language.translate(
                "status.interval_value", days=self.config.schedule.interval_days
            ),
        )
        last_backup = BackupStateStore.from_config(
            self.config.paths.state_dir
        ).last_successful_backup()
        if last_backup:
            delta = datetime.now(UTC) - last_backup
            age = self._format_age(delta)
            last_text = f"{last_backup.astimezone().strftime('%d.%m.%Y %H:%M:%S')} ({age})"
        else:
            last_text = "-"
        self._line("status.last_backup", last_text)

    def _format_age(self, delta: timedelta) -> str:
        total_seconds = int(delta.total_seconds())
        if total_seconds < 3600:
            minutes = max(1, total_seconds // 60)
            return self.language.translate("common.age_minutes", minutes=minutes)
        if total_seconds < 86400:
            return self.language.translate("common.age_hours", hours=total_seconds // 3600)
        return self.language.translate("common.age_days", days=delta.days)

    def _heading(self, key: str) -> None:
        heading = self.language.translate(key)
        print(heading)
        print("-" * len(heading))

    def _line(self, key: str, value: object) -> None:
        label = self.language.translate(key)
        print(f"{label:.<22} {value}")
