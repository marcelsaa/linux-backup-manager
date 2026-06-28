from lbm.core.config import AppConfig
from lbm.services.repository import RepositoryProvider
from lbm.ui.console import Console


class RepositoryMaintenanceService:
    def __init__(
        self,
        config: AppConfig,
        repository_provider: RepositoryProvider | None = None,
    ) -> None:
        self.config = config
        self.repository_provider = repository_provider or RepositoryProvider(config)

    def init_repository(self) -> None:
        restic = self.repository_provider.get()
        if restic is None:
            return
        if restic.check().initialized:
            print("Repository ist bereits vorhanden.")
            return

        print(f"Repository wird angelegt unter:\n{restic.repository}")
        if input("Fortfahren? [j/N]: ").strip().lower() != "j":
            print("Abgebrochen.")
            return

        result = restic.init_repository()
        if result.initialized:
            print(result.message)
        else:
            print("Fehler beim Erstellen des Repositorys:")
            print(result.message)

    def snapshots(self) -> None:
        restic = self.repository_provider.get()
        if restic is None:
            return
        snapshots = restic.snapshots()
        if not snapshots:
            print("Keine Snapshots gefunden.")
            return

        print("Linux Backup Manager")
        print("====================")
        print()
        print("Snapshots")
        print("---------")
        print(f"{'':<2}{'ID':<8} {'Datum':<20} {'Host'}")
        print("-" * 45)
        for index, snapshot in enumerate(reversed(snapshots)):
            marker = "*" if index == 0 else " "
            print(f"{marker} {snapshot.snapshot_id:<8} {snapshot.time:<20} {snapshot.host}")
        print()
        print(f"Anzahl Snapshots: {len(snapshots)}")

    def stats(self) -> None:
        restic = self.repository_provider.get()
        if restic is None:
            return
        stats = restic.stats()
        print("Linux Backup Manager")
        print("====================")
        print()
        print("Repository-Statistik")
        print("--------------------")
        print(f"Snapshots........... {stats.snapshot_count}")
        print(f"Erster Snapshot..... {stats.first_snapshot}")
        print(f"Letzter Snapshot.... {stats.last_snapshot}")
        print(f"Host................ {stats.host}")

    def check(self) -> None:
        restic = self.repository_provider.get()
        if restic is None:
            return
        Console.info("Repository wird geprüft...")
        print()
        result = restic.check_repository()
        if result.initialized:
            Console.success(result.message)
        else:
            Console.error("Repository-Prüfung fehlgeschlagen:")
            Console.error(result.message)

    def forget(self) -> None:
        restic = self.repository_provider.get()
        if restic is None:
            return

        retention = self.config.retention
        print("Forget Dry-Run")
        print("--------------")
        dry_run = restic.forget_dry_run(
            keep_daily=retention.keep_daily,
            keep_weekly=retention.keep_weekly,
            keep_monthly=retention.keep_monthly,
            keep_yearly=retention.keep_yearly,
        )
        print(dry_run if dry_run else "Keine Snapshots würden gelöscht.")
        print()
        if input("Snapshots wirklich löschen? [j/N]: ").strip().lower() != "j":
            print("Abgebrochen.")
            return

        result = restic.forget(
            keep_daily=retention.keep_daily,
            keep_weekly=retention.keep_weekly,
            keep_monthly=retention.keep_monthly,
            keep_yearly=retention.keep_yearly,
        )
        print()
        print(result if result else "Forget abgeschlossen.")

    def prune(self) -> None:
        restic = self.repository_provider.get()
        if restic is None:
            return
        print("Repository wird optimiert.")
        print()
        if input("Prune starten? [j/N]: ").strip().lower() != "j":
            print("Abgebrochen.")
            return
        result = restic.prune()
        print()
        print(result if result else "Prune abgeschlossen.")
