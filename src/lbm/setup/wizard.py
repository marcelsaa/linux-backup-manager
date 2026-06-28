from getpass import getpass
from importlib.resources import files
from pathlib import Path
from shutil import which

import yaml

from lbm.core.config import AppConfig, ConfigLoader
from lbm.core.errors import ApplicationError
from lbm.services.repository import RepositoryDestination, RepositoryProvider
from lbm.ui.console import Console


class SetupWizard:
    def __init__(self, config_file: Path, interactive: bool = True) -> None:
        self.config_file = config_file
        self.password_file = Path()
        self.config: AppConfig | None = None
        self.interactive = interactive

    def _load_setup_config(self) -> bool:
        try:
            self.config = ConfigLoader(self.config_file).load()
        except ApplicationError as error:
            Console.error("config.yaml konnte nicht geladen werden.")
            Console.error(error.message)
            if error.hint:
                Console.info(error.hint)
            for detail in error.details:
                Console.info(detail)
            return False

        self.password_file = Path(self.config.paths.password_file).expanduser()
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

    def _check_config(self) -> bool:
        if self.config_file.exists():
            Console.success("config.yaml vorhanden")
            return True

        Console.error("config.yaml fehlt")
        if not self.interactive:
            Console.warning("config.yaml fehlt. Automatische Erstellung übersprungen.")
            return False

        if input("Standardkonfiguration jetzt erstellen? [J/n]: ").strip().lower() not in (
            "",
            "j",
        ):
            print("config.yaml wurde nicht erstellt.")
            return False

        try:
            template = files("lbm.resources").joinpath("config.example.yaml")
            data = yaml.safe_load(template.read_text(encoding="utf-8"))
        except (FileNotFoundError, yaml.YAMLError):
            Console.error("Standardkonfiguration konnte nicht geladen werden.")
            return False

        data["backup"]["paths"] = self._ask_backup_paths()
        self._configure_targets(data)

        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
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

        selected_paths = [
            path
            for path in default_paths
            if input(f"{path} sichern? [J/n]: ").strip().lower() in ("", "j")
        ]

        print()
        print("Weitere eigene Ordner hinzufügen?")
        print("Leere Eingabe beendet die Auswahl.")
        print()
        while value := input("Zusätzlicher Backup-Ordner: ").strip():
            selected_paths.append(value)

        if not selected_paths:
            Console.error("Es muss mindestens ein Backup-Ordner ausgewählt werden.")
            return self._ask_backup_paths()
        return selected_paths

    def _configure_targets(self, data: dict) -> None:
        print()
        print("Welche Backup-Ziele sollen verwendet werden?")
        print()

        use_usb = input("USB-Laufwerk verwenden? [J/n]: ").strip().lower() in ("", "j")
        use_nas = input("Eingehängtes NAS verwenden? [j/N]: ").strip().lower() == "j"
        if not use_usb and not use_nas:
            Console.error("Es muss mindestens ein Backup-Ziel ausgewählt werden.")
            self._configure_targets(data)
            return

        usb = data["targets"]["usb"]
        usb["enabled"] = use_usb
        if use_usb:
            usb["label"] = self._ask_value("USB-Dateisystemlabel", usb["label"])
            usb["repository_path"] = self._ask_value(
                "Repository-Pfad auf USB",
                usb["repository_path"],
            )

        nas = data["targets"]["nas"]
        nas["enabled"] = use_nas
        if use_nas:
            nas["mount_path"] = self._ask_value("NAS-Mountpfad", nas["mount_path"])
            nas["repository_path"] = self._ask_value(
                "Repository-Pfad auf NAS",
                nas["repository_path"],
            )

    def _ask_value(self, label: str, default: str) -> str:
        return input(f"{label} [{default}]: ").strip() or default

    def _check_password(self) -> bool:
        if self.password_file.exists():
            Console.success("Passwortdatei vorhanden")
            return True

        Console.error("Passwortdatei fehlt")
        if not self.interactive:
            Console.warning("Passwortdatei fehlt. Automatische Erstellung übersprungen.")
            return False
        if input("Passwortdatei jetzt erstellen? [J/n]: ").strip().lower() in (
            "",
            "j",
        ) and self._create_password_file():
            Console.success("Passwortdatei vorhanden")
            return True
        print("Passwortdatei wurde nicht erstellt.")
        return False

    def _create_password_file(self) -> bool:
        print()
        Console.info("Dieses Passwort schützt Ihr Backup-Repository.")
        Console.info("Ohne dieses Passwort können Backups nicht wiederhergestellt werden.")
        Console.info("Die Mindestlänge des Passworts beträgt 8 Zeichen.")
        print()
        while True:
            password = getpass("Neues Backup-Passwort: ")
            confirmation = getpass("Backup-Passwort wiederholen: ")
            if not password:
                Console.error("Das Backup-Passwort darf nicht leer sein.")
            elif len(password) < 8:
                Console.error("Das Backup-Passwort muss mindestens 8 Zeichen lang sein.")
            elif password != confirmation:
                Console.error("Die Passwörter stimmen nicht überein. Bitte erneut eingeben.")
            else:
                break
            print()

        self.password_file.parent.mkdir(parents=True, exist_ok=True)
        self.password_file.write_text(password + "\n")
        self.password_file.chmod(0o600)
        Console.success("Passwortdatei erstellt.")
        return True

    def _check_program(self, program: str, name: str) -> bool:
        if which(program):
            Console.success(f"{name} installiert")
            return True
        Console.error(f"{name} fehlt")
        return False

    def _check_programs(self) -> bool:
        return self._check_program("restic", "Restic")

    def _check_repositories(self) -> bool:
        if self.config is None:
            return False

        destinations = RepositoryProvider(self.config).get_all()
        enabled_count = int(self.config.targets.usb.enabled) + int(
            self.config.targets.nas.enabled
        )
        status = len(destinations) == enabled_count
        for destination in destinations:
            status &= self._check_repository(destination)
        return status

    def _check_repository(self, destination: RepositoryDestination) -> bool:
        result = destination.repository.check()
        if result.initialized:
            Console.success(f"Repository vorhanden: {destination.name}")
            return True

        Console.error(f"Repository fehlt: {destination.name}")
        if not self.interactive:
            Console.warning("Repository fehlt. Automatische Erstellung übersprungen.")
            return False
        answer = input(f"Repository für '{destination.name}' jetzt erstellen? [J/n]: ")
        if answer.strip().lower() not in ("", "j"):
            print("Repository wurde nicht erstellt.")
            return False

        created = destination.repository.init_repository()
        if created.initialized:
            Console.success(f"Repository erstellt: {destination.name}")
            return True
        Console.error(created.message)
        return False

    def run(self) -> bool:
        self._print_header()
        if not self._check_config():
            self._print_summary(False)
            return False
        if not self._load_setup_config():
            self._print_summary(False)
            return False

        status = self._check_password()
        status &= self._check_programs()
        status &= self._check_repositories()
        self._print_summary(status)
        return status
