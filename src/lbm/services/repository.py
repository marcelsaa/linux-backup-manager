from pathlib import Path

from lbm.backup.restic import ResticRepository
from lbm.core.config import AppConfig
from lbm.targets.usb import USBTarget
from lbm.ui.console import Console


class RepositoryProvider:
    """Resolve the configured backup target to a Restic repository."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def get(self) -> ResticRepository | None:
        usb_info = USBTarget(self.config.targets.usb.label).probe()

        if not usb_info.found:
            Console.error("Backup-Laufwerk wurde nicht gefunden.")
            return None

        if usb_info.mountpoint is None:
            Console.error("Backup-Laufwerk ist nicht eingehängt.")
            return None

        repository = usb_info.mountpoint / self.config.targets.usb.repository_path
        return ResticRepository(repository, Path(self.config.paths.password_file))
