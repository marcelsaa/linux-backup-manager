from getpass import getpass
from importlib.resources import files
from pathlib import Path
from shutil import which

from lbm.backup.restic import ResticRepository
from lbm.core.config import ConfigLoader
from lbm.core.errors import ApplicationError
from lbm.targets.usb import USBTarget
from lbm.ui.console import Console


class SetupWizard:
    def __init__(
        self,
        config_file: Path,
        interactive: bool = True,
    ) -> None:
        self.config_file = config_file
        # self.password_file = Path("~/.config/linux-backup-manager/restic-password").expanduser()
        # self.usb_label = "LinuxBackup"
        # self.repository_path = "restic-repository"
        self.password_file = Path()
        self.usb_label = ""
        self.repository_path = ""
        self.interactive = interactive

    def _load_setup_config(self) -> bool:
        try:
            config = ConfigLoader(self.config_file).load()
        except ApplicationError as error:
            Console.error("config.yaml konnte nicht geladen werden.")
            Console.error(error.message)
            if error.hint:
                Console.info(error.hint)
            for detail in error.details:
                Console.info(detail)
            return False

        self.password_file = Path(config.paths.password_file).expanduser()
        self.usb_label = config.targets.usb.label
        self.repository_path = config.targets.usb.repository_path

        return True

    def _print_header(self) -> None:
        print("Linux Backup Manager Setup")
        print("==========================")
        print()
        print("Willkommen zum Einrichtungsassistenten.")
        print()

    def _print_summary(self, all_ok: bool) -> None:
        print()

        if all_ok:
            Console.success("System ist vollständig eingerichtet.")
        else:
            Console.warning("Setup abgeschlossen, es bestehen noch offene Punkte.")

    def _replace_backup_paths(
        self,
        config_content: str,
        backup_paths: list[str],
    ) -> str:
        if not backup_paths:
            return config_content

        lines = config_content.splitlines()
        result: list[str] = []

        inside_backup_paths = False

        for line in lines:
            stripped = line.strip()

            if stripped == "paths:" and result and result[-1].strip() == "backup:":
                result.append(line)
                for path in backup_paths:
                    result.append(f"    - {path}")
                inside_backup_paths = True
                continue

            if inside_backup_paths:
                if stripped.startswith("- "):
                    continue

                inside_backup_paths = False

            result.append(line)

        return "\n".join(result) + "\n"

    def _check_config(self) -> bool:
        if self.config_file.exists():
            Console.success("config.yaml vorhanden")
            return True

        Console.error("config.yaml fehlt")

        if not self.interactive:
            Console.warning(
                "config.yaml fehlt. Automatische Erstellung übersprungen."
            )
            return False

        answer = input(
            "Standardkonfiguration jetzt erstellen? [J/n]: "
        ).strip().lower()

        if answer not in ("", "j"):
            print("config.yaml wurde nicht erstellt.")
            return False

        try:
            template = files("lbm.resources").joinpath("config.example.yaml")
            config_content = template.read_text(encoding="utf-8")
        except FileNotFoundError:
            Console.error("Standardkonfiguration konnte nicht gefunden werden.")
            return False

        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        backup_paths = self._ask_backup_paths()
        config_content = self._replace_backup_paths(config_content, backup_paths)
        self.config_file.write_text(config_content, encoding="utf-8")

        Console.success("config.yaml erstellt")
        return True
    
    def _ask_backup_paths(self) -> list[str]:
        default_paths = [
            "~/Dokumente",
            "~/Bilder",
            "~/Schreibtisch",
            "~/Downloads",
            "~/Projekte",
        ]

        print()
        print("Welche Standardordner sollen gesichert werden?")
        print()

        selected_paths: list[str] = []

        for path in default_paths:
            answer = input(f"{path} sichern? [J/n]: ").strip().lower()

            if answer in ("", "j"):
                selected_paths.append(path)

        print()
        print("Weitere eigene Ordner hinzufügen?")
        print("Leere Eingabe beendet die Auswahl.")
        print()

        while True:
            value = input("Zusätzlicher Backup-Ordner: ").strip()

            if not value:
                break

            selected_paths.append(value)
        if not selected_paths:
            Console.error(
                "Es muss mindestens ein Backup-Ordner ausgewählt werden."
            )
            return self._ask_backup_paths()

        return selected_paths

    def _check_password(self) -> bool:
        if self.password_file.exists():
            Console.success("Passwortdatei vorhanden")
            return True

        Console.error("Passwortdatei fehlt")

        if not self.interactive:
            Console.warning("Passwortdatei fehlt. Automatische Erstellung übersprungen.")
            return False

        answer = input("Passwortdatei jetzt erstellen? [J/n]: ").strip().lower()

        if answer in ("", "j") and self._create_password_file():
            print("✓ Passwortdatei vorhanden")
            return True

        print("Passwortdatei wurde nicht erstellt.")
        return False

    def _create_password_file(self) -> bool:
        print()
        Console.info("Dieses Passwort schützt Ihr Backup-Repository.")
        Console.info(
            "Ohne dieses Passwort können Backups nicht wiederhergestellt werden."
        )
        Console.info("Die Mindestlänge des Passworts beträgt 8 Zeichen.")
        print()

        while True:
            password = getpass("Neues Backup-Passwort: ")
            confirmation = getpass("Backup-Passwort wiederholen: ")

            if not password:
                Console.error("Das Backup-Passwort darf nicht leer sein.")
                print()
                continue

            if len(password) < 8:
                Console.error(
                    "Das Backup-Passwort muss mindestens 8 Zeichen lang sein."
                )
                print()
                continue

            if password != confirmation:
                Console.error(
                    "Die Passwörter stimmen nicht überein. Bitte erneut eingeben."
                )
                print()
                continue

            break

        self.password_file.parent.mkdir(parents=True, exist_ok=True)
        self.password_file.write_text(password + "\n")
        self.password_file.chmod(0o600)

        Console.success("Passwortdatei erstellt.")
        return True

    def _check_program(
        self,
        program: str,
        name: str,
    ) -> bool:
        if which(program):
            Console.success(f"{name} installiert")
            return True

        Console.error(f"{name} fehlt")
        return False

    def _check_programs(self) -> bool:
        ok = True

        if not self._check_program("restic", "Restic"):
            ok = False

        if not self._check_program("timeshift", "Timeshift"):
            ok = False

        return ok

    def _check_usb(self) -> Path | None:
        usb = USBTarget(self.usb_label)
        info = usb.probe()

        if not info.found:
            Console.error(f"USB-Laufwerk '{self.usb_label}' nicht gefunden")
            return None

        Console.success(f"USB-Laufwerk '{self.usb_label}' gefunden")

        if info.mountpoint is None:
            Console.error("USB-Laufwerk ist nicht eingehängt")
            return None

        return info.mountpoint

    def _check_repository(self, mountpoint: Path) -> bool:
        repository = mountpoint / self.repository_path

        restic = ResticRepository(
            repository,
            self.password_file,
        )

        if restic.check().initialized:
            Console.success("Repository vorhanden")
            return True

        Console.error("Repository fehlt")

        if not self.interactive:
            Console.warning("Repository fehlt. Automatische Erstellung übersprungen.")
            return False

        answer = input("Repository jetzt erstellen? [J/n]: ").strip().lower()

        if answer in ("", "j") and self._create_repository():
            Console.success("Repository vorhanden")
            return True

        print("Repository wurde nicht erstellt.")
        return False

    def _create_repository(self) -> bool:
        usb = USBTarget(self.usb_label)
        info = usb.probe()

        if not info.found or info.mountpoint is None:
            print("USB-Laufwerk nicht verfügbar.")
            return False

        repository = Path(info.mountpoint) / self.repository_path

        restic = ResticRepository(
            repository,
            self.password_file,
        )

        result = restic.init_repository()

        if result.initialized:
            Console.success("Repository erstellt.")
            return True

        Console.error(result.message)
        return False

    def run(self) -> None:
        self._print_header()

        status = True

        status &= self._check_config()
        if not status:
            self._print_summary(False)
            return

        if not self._load_setup_config():
            self._print_summary(False)
            return

        status &= self._check_password()
        status &= self._check_programs()

        mountpoint = self._check_usb()

        if mountpoint is None:
            self._print_summary(False)
            return

        status &= self._check_repository(mountpoint)

        self._print_summary(status)
