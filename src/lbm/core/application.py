import platform
import shutil
from pathlib import Path

from lbm.backup.restic import ResticRepository
from lbm.core.config import ConfigLoader
from lbm.health.checks import HealthChecker
from lbm.targets.usb import USBTarget


class Application:
    """Zentrale Anwendungsklasse des Linux Backup Managers."""

    def __init__(self) -> None:
        self.project_dir = Path(__file__).resolve().parents[3]
        self.config_file = self.project_dir / "config" / "config.yaml"
        self.config = ConfigLoader(self.config_file).load()

    def status(self) -> None:
        password_file = Path(self.config.paths.password_file).expanduser()

        print("Linux Backup Manager")
        print("====================")
        print()
        print("System")
        print("------")
        print(f"Python............... {platform.python_version()}")
        print(f"Restic............... {'OK' if shutil.which('restic') else 'FEHLT'}")
        print(f"Timeshift............ {'OK' if shutil.which('timeshift') else 'FEHLT'}")
        print()
        print("Konfiguration")
        print("-------------")
        print(f"Datei................ {self.config_file}")
        print(f"Konfiguration........ {'OK' if self.config_file.exists() else 'FEHLT'}")
        print(f"Host................. {self.config.system.host_name}")
        print()
        print("Sicherheit")
        print("----------")
        print(f"Passwortdatei........ {'OK' if password_file.exists() else 'FEHLT'}")
        print(f"Pfad................. {password_file}")
    
    def health(self) -> None:
        checker = HealthChecker(Path(self.config.paths.password_file),
        self.config.targets.usb.label,
        self.config.targets.usb.repository_path,
        )
        results = checker.run()

        print("Linux Backup Manager")
        print("====================")
        print()
        print("Health Check")
        print("------------")

        overall = True

        for result in results:
            symbol = "✓" if result.ok else "✗"
            print(f"{symbol} {result.name:<16} {result.message}")

            if not result.ok:
                overall = False

        print()
        print(f"Gesamtstatus........ {'OK' if overall else 'FEHLER'}")

    def init_repository(self) -> None:
        restic = self._get_restic_repository()

        if restic is None:
            return


        if restic.check().initialized:
            print("Repository ist bereits vorhanden.")
            return

        print(f"Repository wird angelegt unter:\n{restic.repository}")
        answer = input("Fortfahren? [j/N]: ").strip().lower()

        if answer != "j":
            print("Abgebrochen.")
            return

        result = restic.init_repository()

        if result.initialized:
            print(result.message)
        else:
            print("Fehler beim Erstellen des Repositorys:")
            print(result.message)

    def backup(self) -> None:
        restic = self._get_restic_repository()

        if restic is None:
            return

        if not restic.check().initialized:
            print("Fehler: Restic-Repository ist nicht vorhanden.")
            print("Bitte zuerst ausführen:")
            print("backup-manager init")
            return

        backup_paths = [
            Path(path).expanduser()
            for path in self.config.backup.paths
        ]

        print("Starte Backup folgender Pfade:")

        for path in backup_paths:
            print(f"- {path}")

        excludes = [
            str(Path(exclude).expanduser())
            for exclude in self.config.backup.excludes
]

        result = restic.backup(backup_paths, excludes)

        if result.ok:
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
        else:
            print("Backup fehlgeschlagen:")
            print(result.message)
    
    def _get_restic_repository(self) -> ResticRepository | None:
        usb = USBTarget(self.config.targets.usb.label)
        usb_info = usb.probe()

        if not usb_info.found:
            print("Fehler: Backup-Laufwerk wurde nicht gefunden.")
            return None

        if usb_info.mountpoint is None:
            print("Fehler: Backup-Laufwerk ist nicht eingehängt.")
            return None

        repository = (
            Path(usb_info.mountpoint)
            / self.config.targets.usb.repository_path
        )

        return ResticRepository(
            repository,
            Path(self.config.paths.password_file),
        )
    
    def snapshots(self) -> None:
        restic = self._get_restic_repository()

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

            print(
                f"{marker} {snapshot.snapshot_id:<8} "
                f"{snapshot.time:<20} "
                f"{snapshot.host}"
            )

        print()
        print(f"Anzahl Snapshots: {len(snapshots)}")
    
    def restore(self) -> None:
        restic = self._get_restic_repository()

        if restic is None:
            return

        snapshots = restic.snapshots()

        if not snapshots:
            print("Keine Snapshots gefunden.")
            return

        print("Verfügbare Snapshots")
        print("--------------------")

        for index, snapshot in enumerate(reversed(snapshots), start=1):
            print(
                f"{index}) "
                f"{snapshot.snapshot_id} "
                f"{snapshot.time}"
            )

        selection = input(
            "\nWelchen Snapshot möchten Sie wiederherstellen? "
        ).strip()

        try:
            index = int(selection)
        except ValueError:
            print("Ungültige Eingabe.")
            return

        if index < 1 or index > len(snapshots):
            print("Snapshot existiert nicht.")
            return

        snapshot = list(reversed(snapshots))[index - 1]

        print()
        print("Ausgewählter Snapshot:")
        print(f"ID..... {snapshot.snapshot_id}")
        print(f"Datum.. {snapshot.time}")
        print(f"Host... {snapshot.host}")

        target = self.project_dir / "tests" / "restore-test"

        print()
        print(f"Zielverzeichnis: {target}")

        answer = input("Restore starten? [j/N]: ").strip().lower()

        if answer != "j":
            print("Abgebrochen.")
            return

        result = restic.restore(
            snapshot.snapshot_id,
            target,
        )

        print()

        if result.ok:
            print(result.message)
        else:
            print("Restore fehlgeschlagen:")
            print(result.message)