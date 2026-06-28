import os
from pathlib import Path

from lbm.core.config import AppConfig, ConfigLoader
from lbm.core.state import BackupStateStore
from lbm.services.backup import BackupService
from lbm.services.health import HealthService
from lbm.services.recovery import RecoveryInfoService
from lbm.services.repository_maintenance import RepositoryMaintenanceService
from lbm.services.restore import RestoreService
from lbm.services.scheduler import SystemdScheduler
from lbm.services.setup import SetupService
from lbm.services.status import StatusService


class Application:
    """Coordinate CLI commands and their application services."""

    def __init__(self) -> None:
        configured_file = os.environ.get("LBM_CONFIG_FILE")
        self.config_file = (
            Path(configured_file).expanduser()
            if configured_file
            else Path("~/.config/linux-backup-manager/config.yaml").expanduser()
        )
        self.config: AppConfig | None = None

    def _load_config(self) -> AppConfig:
        if self.config is None:
            self.config = ConfigLoader(self.config_file).load()
        return self.config

    def _maintenance(self) -> RepositoryMaintenanceService:
        return RepositoryMaintenanceService(self._load_config())

    def status(self) -> None:
        StatusService(self._load_config(), self.config_file).run()

    def health(self) -> None:
        HealthService(self._load_config()).run()

    def recovery_info(self) -> None:
        RecoveryInfoService(self._load_config(), self.config_file).run()

    def init_repository(self) -> None:
        self._maintenance().init_repository()

    def backup(self) -> bool:
        config = self._load_config()
        successful = BackupService(config).run()
        if successful:
            BackupStateStore.from_config(config.paths.state_dir).record_success()
        return successful

    def backup_if_due(self) -> bool:
        config = self._load_config()
        state = BackupStateStore.from_config(config.paths.state_dir)
        max_age_hours = config.schedule.interval_days * 24
        if not state.is_due(max_age_hours):
            print("Backup ist noch nicht fällig.")
            return True
        print(
            "Letztes erfolgreiches Backup ist älter als "
            f"{max_age_hours} Stunden oder unbekannt."
        )
        return self.backup()

    def backup_scheduled(self) -> bool:
        config = self._load_config()
        state = BackupStateStore.from_config(config.paths.state_dir)
        if not state.is_scheduled_due(config.schedule.interval_days):
            print("Das konfigurierte Backup-Intervall ist noch nicht erreicht.")
            return True
        return self.backup()

    def schedule_install(self) -> bool:
        config = self._load_config()
        return SystemdScheduler(self.config_file, config.schedule).install()

    def schedule_status(self) -> bool:
        config = self._load_config()
        return SystemdScheduler(self.config_file, config.schedule).status()

    def schedule_remove(self) -> bool:
        config = self._load_config()
        return SystemdScheduler(self.config_file, config.schedule).remove()

    def snapshots(self) -> None:
        self._maintenance().snapshots()

    def restore(self) -> None:
        RestoreService(self._load_config()).run()

    def stats(self) -> None:
        self._maintenance().stats()

    def check(self) -> None:
        self._maintenance().check()

    def forget(self) -> None:
        self._maintenance().forget()

    def prune(self) -> None:
        self._maintenance().prune()

    def setup(self, interactive: bool = True) -> bool:
        return SetupService(self.config_file).run(interactive=interactive)
