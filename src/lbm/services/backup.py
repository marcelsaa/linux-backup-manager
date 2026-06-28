from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from lbm.backup.restic import BackupResult
from lbm.core.config import AppConfig
from lbm.services.repository import RepositoryDestination, RepositoryProvider
from lbm.ui.console import Console


class BackupService:
    def __init__(
        self,
        config: AppConfig,
        repository_provider: RepositoryProvider | None = None,
    ) -> None:
        self.config = config
        self.repository_provider = repository_provider or RepositoryProvider(config)

    def run(self) -> bool:
        destinations = self.repository_provider.get_all()
        if not destinations:
            return False

        expected_destinations = int(self.config.targets.usb.enabled) + int(
            self.config.targets.nas.enabled
        )
        all_destinations_available = len(destinations) == expected_destinations

        backup_paths = [Path(path).expanduser() for path in self.config.backup.paths]
        excludes = [str(Path(exclude).expanduser()) for exclude in self.config.backup.excludes]

        print("Starte Backup folgender Pfade:")
        for path in backup_paths:
            print(f"- {path}")

        with ThreadPoolExecutor(max_workers=len(destinations)) as executor:
            results = list(
                executor.map(
                    lambda destination: self._backup(
                        destination,
                        backup_paths,
                        excludes,
                    ),
                    destinations,
                )
            )

        for destination, result in zip(destinations, results, strict=True):
            self._print_result(destination.name, result)
        return all_destinations_available and all(result.ok for result in results)

    def _backup(
        self,
        destination: RepositoryDestination,
        backup_paths: list[Path],
        excludes: list[str],
    ) -> BackupResult:
        repository_check = destination.repository.check()
        if not repository_check.initialized:
            return BackupResult(
                ok=False,
                snapshot_id=None,
                files_new=0,
                files_changed=0,
                files_unmodified=0,
                processed_files=0,
                processed_size="unbekannt",
                duration="unbekannt",
                message=repository_check.message,
            )
        return destination.repository.backup(backup_paths, excludes)

    def _print_result(self, destination_name: str, result: BackupResult) -> None:
        print()
        Console.headline(destination_name)
        if not result.ok:
            Console.error("Backup fehlgeschlagen:")
            Console.error(result.message)
            return

        print("Backup erfolgreich")
        print("------------------")
        print(f"Snapshot-ID........ {result.snapshot_id}")
        print(f"Neue Dateien...... {result.files_new}")
        print(f"Geändert.......... {result.files_changed}")
        print(f"Unverändert....... {result.files_unmodified}")
        print(f"Verarbeitet....... {result.processed_files}")
        print(f"Datenmenge........ {result.processed_size}")
        print(f"Dauer............. {result.duration}")
