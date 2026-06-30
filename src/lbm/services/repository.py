from dataclasses import dataclass
from pathlib import Path

from lbm.backup.restic import ResticRepository
from lbm.core.config import AppConfig
from lbm.services.language import LanguageService
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
        self.language = LanguageService(config.system.language)

    def get(self) -> ResticRepository | None:
        destinations = self.get_all()
        if not destinations:
            return None
        if len(destinations) == 1:
            return destinations[0].repository

        heading = self.language.translate("repository.available_targets")
        print(heading)
        print("-" * len(heading))
        for index, destination in enumerate(destinations, start=1):
            print(f"{index}) {destination.name}")

        selection = input(self.language.translate("repository.select_target")).strip()
        try:
            index = int(selection)
        except ValueError:
            Console.error(self.language.translate("repository.invalid_selection"))
            return None

        if index < 1 or index > len(destinations):
            Console.error(self.language.translate("repository.target_not_exists"))
            return None
        return destinations[index - 1].repository

    def get_all(self) -> list[RepositoryDestination]:
        destinations: list[RepositoryDestination] = []
        usb_config = self.config.targets.usb

        if usb_config.enabled:
            usb_info = USBTarget(usb_config.label).probe()
            if not usb_info.found:
                Console.warning(
                    self.language.translate(
                        "repository.usb_not_found", label=usb_config.label
                    )
                )
            elif usb_info.mountpoint is None:
                Console.warning(
                    self.language.translate(
                        "repository.usb_not_mounted", label=usb_config.label
                    )
                )
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
                Console.warning(
                    self.language.translate(
                        "repository.nas_unavailable", path=mount_path
                    )
                )
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
            Console.error(self.language.translate("repository.no_target_available"))
        return destinations

    def _repository(self, path: Path) -> ResticRepository:
        return ResticRepository(path, Path(self.config.paths.password_file))
