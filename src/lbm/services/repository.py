from dataclasses import dataclass
from pathlib import Path

from lbm.backup.restic import ResticRepository
from lbm.core.config import AppConfig
from lbm.targets.usb import USBTarget
from lbm.ui.console import Console


@dataclass(frozen=True)
class RepositoryDestination:
    name: str
    repository: ResticRepository


class RepositoryProvider:
    """Resolve the configured backup target to a Restic repository."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def get(self) -> ResticRepository | None:
        destinations = self.get_all()
        if not destinations:
            return None
        if len(destinations) == 1:
            return destinations[0].repository

        print("Verfügbare Backup-Ziele")
        print("-----------------------")
        for index, destination in enumerate(destinations, start=1):
            print(f"{index}) {destination.name}")

        selection = input("Backup-Ziel auswählen: ").strip()
        try:
            index = int(selection)
        except ValueError:
            Console.error("Ungültige Auswahl.")
            return None

        if index < 1 or index > len(destinations):
            Console.error("Backup-Ziel existiert nicht.")
            return None
        return destinations[index - 1].repository

    def get_all(self) -> list[RepositoryDestination]:
        destinations: list[RepositoryDestination] = []
        usb_config = self.config.targets.usb

        if usb_config.enabled:
            usb_info = USBTarget(usb_config.label).probe()
            if not usb_info.found:
                Console.warning(f"USB-Ziel '{usb_config.label}' wurde nicht gefunden.")
            elif usb_info.mountpoint is None:
                Console.warning(f"USB-Ziel '{usb_config.label}' ist nicht eingehängt.")
            else:
                destinations.append(
                    RepositoryDestination(
                        name=f"USB: {usb_config.label}",
                        repository=self._repository(
                            usb_info.mountpoint / usb_config.repository_path
                        ),
                    )
                )

        nas_config = self.config.targets.nas
        if nas_config.enabled:
            mount_path = Path(nas_config.mount_path).expanduser()
            if not mount_path.is_dir():
                Console.warning(f"NAS-Ziel ist nicht verfügbar: {mount_path}")
            else:
                destinations.append(
                    RepositoryDestination(
                        name=f"NAS: {mount_path}",
                        repository=self._repository(
                            mount_path / nas_config.repository_path
                        ),
                    )
                )

        if not destinations:
            Console.error("Kein konfiguriertes Backup-Ziel ist verfügbar.")
        return destinations

    def _repository(self, path: Path) -> ResticRepository:
        return ResticRepository(path, Path(self.config.paths.password_file))
