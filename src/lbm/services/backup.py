from pathlib import Path

from lbm.core.config import AppConfig
from lbm.services.repository import RepositoryProvider
from lbm.ui.console import Console


class BackupService:
    def __init__(
        self,
        config: AppConfig,
        repository_provider: RepositoryProvider | None = None,
    ) -> None:
        self.config = config
        self.repository_provider = repository_provider or RepositoryProvider(config)

    def run(self) -> None:
        restic = self.repository_provider.get()
        if restic is None:
            return

        repository_check = restic.check()
        if not repository_check.initialized:
            Console.error("Repository ist nicht verfügbar:")
            Console.error(repository_check.message)
            return

        backup_paths = [Path(path).expanduser() for path in self.config.backup.paths]
        excludes = [str(Path(exclude).expanduser()) for exclude in self.config.backup.excludes]

        print("Starte Backup folgender Pfade:")
        for path in backup_paths:
            print(f"- {path}")

        result = restic.backup(backup_paths, excludes)
        if not result.ok:
            print("Backup fehlgeschlagen:")
            print(result.message)
            return

        print()
        print("Backup erfolgreich")
        print("------------------")
        print(f"Snapshot-ID........ {result.snapshot_id}")
        print(f"Neue Dateien...... {result.files_new}")
        print(f"Geändert.......... {result.files_changed}")
        print(f"Unverändert....... {result.files_unmodified}")
        print(f"Verarbeitet....... {result.processed_files}")
        print(f"Datenmenge........ {result.processed_size}")
        print(f"Dauer............. {result.duration}")
