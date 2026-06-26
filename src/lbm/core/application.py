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
        usb = USBTarget(self.config.targets.usb.label)
        usb_info = usb.probe()

        if not usb_info.found:
            print("Fehler: Backup-Laufwerk wurde nicht gefunden.")
            return

        if usb_info.mountpoint is None:
            print("Fehler: Backup-Laufwerk ist nicht eingehängt.")
            return

        repository = (
            Path(usb_info.mountpoint)
            / self.config.targets.usb.repository_path
        )

        restic = ResticRepository(
            repository,
            Path(self.config.paths.password_file),
        )

        if restic.check().initialized:
            print("Repository ist bereits vorhanden.")
            return

        print(f"Repository wird angelegt unter:\n{repository}")
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
        usb = USBTarget(self.config.targets.usb.label)
        usb_info = usb.probe()

        if not usb_info.found:
            print("Fehler: Backup-Laufwerk wurde nicht gefunden.")
            return

        if usb_info.mountpoint is None:
            print("Fehler: Backup-Laufwerk ist nicht eingehängt.")
            return

        repository = (
            Path(usb_info.mountpoint)
            / self.config.targets.usb.repository_path
        )

        restic = ResticRepository(
            repository,
            Path(self.config.paths.password_file),
        )

        if not restic.check().initialized:
            print("Fehler: Restic-Repository ist nicht vorhanden.")
            print("Bitte zuerst ausführen:")
            print("backup-manager init")
            return

        sample_data = self.project_dir / "tests" / "sample-data"

        print("Starte Testbackup:")
        print(sample_data)

        result = restic.backup([sample_data])

        if result.initialized:
            print("Backup erfolgreich erstellt.")
        else:
            print("Backup fehlgeschlagen:")
            print(result.message)