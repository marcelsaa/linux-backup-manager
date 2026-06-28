import platform
import shutil
from pathlib import Path

from lbm import __version__
from lbm.core.config import AppConfig
from lbm.core.state import BackupStateStore


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
        print()
        print("Automatische Backups")
        print("--------------------")
        print(f"Aktiviert............ {'JA' if self.config.schedule.enabled else 'NEIN'}")
        print(f"Prüfzeit............. {self.config.schedule.daily_time} Uhr")
        print(f"Intervall............ {self.config.schedule.interval_days} Tag(e)")
        last_backup = BackupStateStore.from_config(
            self.config.paths.state_dir
        ).last_successful_backup()
        last_text = last_backup.astimezone().strftime("%d.%m.%Y %H:%M:%S") if last_backup else "-"
        print(f"Letztes Backup....... {last_text}")
