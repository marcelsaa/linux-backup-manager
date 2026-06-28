import platform
import shutil
from pathlib import Path

from lbm import __version__
from lbm.core.config import AppConfig


class StatusService:
    def __init__(self, config: AppConfig, config_file: Path) -> None:
        self.config = config
        self.config_file = config_file

    def run(self) -> None:
        password_file = Path(self.config.paths.password_file).expanduser()

        print("Linux Backup Manager")
        print(f"Version {__version__}")
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
