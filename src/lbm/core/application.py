import os
from pathlib import Path

from lbm.core.config import AppConfig, ConfigLoader
from lbm.services.backup import BackupService
from lbm.services.health import HealthService
from lbm.services.repository_maintenance import RepositoryMaintenanceService
from lbm.services.restore import RestoreService
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

    def init_repository(self) -> None:
        self._maintenance().init_repository()

    def backup(self) -> None:
        BackupService(self._load_config()).run()

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
