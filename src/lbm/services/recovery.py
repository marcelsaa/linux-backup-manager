from pathlib import Path
from stat import S_IMODE

from lbm.core.config import AppConfig
from lbm.ui.console import Console


class RecoveryInfoService:
    """Display recovery-critical metadata without reading repository secrets."""

    def __init__(self, config: AppConfig, config_file: Path) -> None:
        self.config = config
        self.config_file = config_file
        self.password_file = Path(config.paths.password_file).expanduser()

    def run(self) -> None:
        print("Linux Backup Manager")
        print("Recovery-Informationen")
        print("======================")
        print()
        Console.warning("Das Repository-Passwort kann nicht wiederhergestellt werden.")
        print(
            "Ohne das richtige Passwort oder eine sichere Kopie der Passwortdatei "
            "sind die Backups dauerhaft unzugänglich."
        )

        self._print_files()
        self._print_targets()
        self._print_recovery_steps()

    def _print_files(self) -> None:
        print()
        print("Wichtige Dateien")
        print("-----------------")
        print(f"Konfiguration....... {self.config_file}")
        print(f"Passwortdatei........ {self.password_file}")
        print(f"Passwortdatei-Status. {self._password_status()}")
        print(f"Konfigurationskopie.. {self.config_file}.bak")

    def _password_status(self) -> str:
        try:
            mode = S_IMODE(self.password_file.stat().st_mode)
        except FileNotFoundError:
            return "FEHLT"
        except OSError:
            return "nicht prüfbar"
        return f"vorhanden (Rechte {mode:04o})"

    def _print_targets(self) -> None:
        print()
        print("Konfigurierte Repository-Ziele")
        print("------------------------------")

        usb = self.config.targets.usb
        if usb.enabled:
            print(f"USB-Label............ {usb.label}")
            print(f"USB-Repository....... {usb.repository_path}")

        nas = self.config.targets.nas
        if nas.enabled:
            repository = Path(nas.mount_path).expanduser() / nas.repository_path
            print(f"NAS-Repository....... {repository}")

    def _print_recovery_steps(self) -> None:
        print()
        print("Notfallablauf")
        print("-------------")
        print("1. Restic und Linux Backup Manager auf dem Ersatzsystem installieren.")
        print("2. Das USB- oder NAS-Backup-Ziel einhängen.")
        print("3. Konfiguration und Passwortdatei aus einer getrennten Kopie wiederherstellen.")
        print(f"4. Dateirechte setzen: chmod 600 {self.password_file}")
        print("5. Zugriff prüfen: backup-manager health")
        print("6. Snapshots anzeigen: backup-manager snapshots")
        print("7. Wiederherstellung starten: backup-manager restore")
        print()
        Console.info(
            "Bewahren Sie eine Kopie der Passwortdatei getrennt vom Backup-Repository "
            "und vor unbefugtem Zugriff geschützt auf."
        )
