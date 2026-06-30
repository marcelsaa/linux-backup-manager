from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from lbm.backup.restic import BackupResult
from lbm.core.config import AppConfig
from lbm.services.language import LanguageService
from lbm.services.repository import RepositoryDestination, RepositoryProvider
from lbm.ui.console import Console


class BackupService:
    def __init__(
        self,
        config: AppConfig,
        repository_provider: RepositoryProvider | None = None,
    ) -> None:
        self.config = config
        self.language = LanguageService(config.system.language)
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

        print(self._text("backup.start_paths"))
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
            if result.ok:
                self._cleanup(destination)
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
                processed_size=self._text("common.unknown"),
                duration=self._text("common.unknown"),
                message=repository_check.message,
            )
        return destination.repository.backup(backup_paths, excludes)

    def _print_result(self, destination_name: str, result: BackupResult) -> None:
        print()
        Console.headline(destination_name)
        if not result.ok:
            Console.error(self._text("backup.failed"))
            Console.error(result.message)
            return

        heading = self._text("backup.success")
        print(heading)
        print("-" * len(heading))
        self._line("backup.snapshot_id", result.snapshot_id)
        self._line("backup.new_files", result.files_new)
        self._line("backup.changed", result.files_changed)
        self._line("backup.unchanged", result.files_unmodified)
        self._line("backup.processed", result.processed_files)
        self._line("backup.data_size", result.processed_size)
        self._line("backup.duration", result.duration)

    def _cleanup(self, destination: RepositoryDestination) -> None:
        r = self.config.retention
        Console.info(self._text("backup.cleanup_start"))
        ok = destination.repository.cleanup(
            r.keep_daily, r.keep_weekly, r.keep_monthly, r.keep_yearly
        )
        if ok:
            Console.success(self._text("backup.cleanup_done"))
        else:
            Console.warning(self._text("backup.cleanup_failed"))

    def _line(self, key: str, value: object) -> None:
        print(f"{self._text(key):.<20} {value}")

    def _text(self, key: str, **values: object) -> str:
        return self.language.translate(key, **values)
