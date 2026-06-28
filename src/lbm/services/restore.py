from pathlib import Path

from lbm.core.config import AppConfig
from lbm.services.repository import RepositoryProvider


class RestoreService:
    def __init__(
        self,
        config: AppConfig,
        target: Path | None = None,
        repository_provider: RepositoryProvider | None = None,
    ) -> None:
        self.target = target
        self.repository_provider = repository_provider or RepositoryProvider(config)

    def run(self) -> None:
        restic = self.repository_provider.get()
        if restic is None:
            return

        snapshots = restic.snapshots()
        if not snapshots:
            print("Keine Snapshots gefunden.")
            return

        newest_first = list(reversed(snapshots))
        print("Verfügbare Snapshots")
        print("--------------------")
        for index, snapshot in enumerate(newest_first, start=1):
            print(f"{index}) {snapshot.snapshot_id} {snapshot.time}")

        selection = input("\nWelchen Snapshot möchten Sie wiederherstellen? ").strip()
        try:
            index = int(selection)
        except ValueError:
            print("Ungültige Eingabe.")
            return

        if index < 1 or index > len(newest_first):
            print("Snapshot existiert nicht.")
            return

        snapshot = newest_first[index - 1]
        target = self.target or self._ask_target(snapshot.snapshot_id)
        print()
        print("Ausgewählter Snapshot:")
        print(f"ID..... {snapshot.snapshot_id}")
        print(f"Datum.. {snapshot.time}")
        print(f"Host... {snapshot.host}")
        print()
        print(f"Zielverzeichnis: {target}")

        if target.exists() and any(target.iterdir()):
            warning = input("Zielverzeichnis ist nicht leer. Trotzdem fortfahren? [j/N]: ")
            if warning.strip().lower() != "j":
                print("Abgebrochen.")
                return

        if input("Restore starten? [j/N]: ").strip().lower() != "j":
            print("Abgebrochen.")
            return

        result = restic.restore(snapshot.snapshot_id, target)
        print()
        if result.ok:
            print(result.message)
        else:
            print("Restore fehlgeschlagen:")
            print(result.message)

    def _ask_target(self, snapshot_id: str) -> Path:
        default = Path.home() / "lbm-restore" / snapshot_id
        value = input(f"Restore-Ziel [{default}]: ").strip()
        return Path(value).expanduser() if value else default
