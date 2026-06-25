from pathlib import Path
import platform
import shutil

from lbm.core.config import ConfigLoader


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