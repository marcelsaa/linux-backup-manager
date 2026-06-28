from datetime import datetime
from getpass import getpass
from importlib.resources import files
from pathlib import Path
from shutil import copy2, which

import yaml

from lbm.backup.restic import RepositoryStatus
from lbm.core.config import AppConfig, ConfigLoader, UniqueKeyLoader
from lbm.core.errors import ApplicationError
from lbm.services.language import LanguageService
from lbm.services.repository import RepositoryDestination, RepositoryProvider
from lbm.services.scheduler import SystemdScheduler
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
            if not self.interactive:
                return True
            answer = input("Bestehende Konfiguration bearbeiten? [j/N]: ")
            if answer.strip().lower() != "j":
                return True
            return self._edit_config()

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

        self._configure_language(data)
        data["backup"]["paths"] = self._ask_backup_paths()
        self._configure_targets(data)
        self._configure_schedule(data)

        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self._write_config(data)
        Console.success("config.yaml erstellt")
        return True

    def _edit_config(self) -> bool:
        try:
            ConfigLoader(self.config_file).load()
            data = yaml.load(
                self.config_file.read_text(encoding="utf-8"),
                Loader=UniqueKeyLoader,
            )
        except ApplicationError as error:
            Console.error(error.message)
            if error.hint:
                Console.info(error.hint)
            for detail in error.details:
                Console.info(detail)
            return False
        except (OSError, yaml.YAMLError) as error:
            Console.error(f"Konfiguration konnte nicht bearbeitet werden: {error}")
            return False

        print()
        Console.info("Sprache, Backup-Ordner, Backup-Ziele und Zeitplan werden neu abgefragt.")
        self._configure_language(data)
        data["backup"]["paths"] = self._ask_backup_paths(data["backup"]["paths"])
        self._configure_targets(data)
        self._configure_schedule(data)

        try:
            AppConfig.model_validate(data)
            backup_file = self.config_file.with_name(f"{self.config_file.name}.bak")
            copy2(self.config_file, backup_file)
            self._write_config(data)
        except (OSError, ValueError, yaml.YAMLError) as error:
            Console.error(f"Konfiguration konnte nicht gespeichert werden: {error}")
            return False

        Console.success("config.yaml aktualisiert")
        Console.info(f"Sicherung der vorherigen Konfiguration: {backup_file}")
        return True

    def _write_config(self, data: dict) -> None:
        temporary_file = self.config_file.with_name(f".{self.config_file.name}.tmp")
        temporary_file.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        temporary_file.replace(self.config_file)

    def _ask_yes_no(self, prompt: str, default: bool) -> bool:
        suffix = "[J/n]" if default else "[j/N]"
        answer = input(f"{prompt} {suffix}: ").strip().lower()
        if not answer:
            return default
        return answer == "j"

    def _configure_language(self, data: dict) -> None:
        system = data.setdefault("system", {})
        current = system.get("language", LanguageService.default_language)
        language = LanguageService(current)

        while True:
            prompt = language.translate("language.selection_prompt")
            selected = input(f"{prompt} [{current}]: ").strip().lower() or current
            if selected in LanguageService.supported_languages:
                system["language"] = selected
                confirmation = LanguageService(selected).translate(
                    "language.selected",
                    language=selected,
                )
                Console.info(confirmation)
                return
            Console.error(language.translate("language.invalid"))

    def _ask_backup_paths(self, current_paths: list[str] | None = None) -> list[str]:
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

        selected_paths = []
        for path in default_paths:
            default = current_paths is None or path in current_paths
            if self._ask_yes_no(f"{path} sichern?", default):
                selected_paths.append(path)

        custom_paths = [path for path in current_paths or [] if path not in default_paths]
        if custom_paths:
            print()
            print("Bereits konfigurierte eigene Ordner:")
            for path in custom_paths:
                if self._ask_yes_no(f"{path} weiter sichern?", True):
                    selected_paths.append(path)

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

        usb = data["targets"]["usb"]
        nas = data["targets"]["nas"]
        use_usb = self._ask_yes_no("USB-Laufwerk verwenden?", usb["enabled"])
        use_nas = self._ask_yes_no("Eingehängtes NAS verwenden?", nas["enabled"])
        if not use_usb and not use_nas:
            Console.error("Es muss mindestens ein Backup-Ziel ausgewählt werden.")
            self._configure_targets(data)
            return

        usb["enabled"] = use_usb
        if use_usb:
            usb["label"] = self._ask_value("USB-Dateisystemlabel", usb["label"])
            usb["repository_path"] = self._ask_value(
                "Repository-Pfad auf USB",
                usb["repository_path"],
            )

        nas["enabled"] = use_nas
        if use_nas:
            nas["mount_path"] = self._ask_value("NAS-Mountpfad", nas["mount_path"])
            nas["repository_path"] = self._ask_value(
                "Repository-Pfad auf NAS",
                nas["repository_path"],
            )

    def _ask_value(self, label: str, default: str) -> str:
        return input(f"{label} [{default}]: ").strip() or default

    def _configure_schedule(self, data: dict) -> None:
        print()
        enabled = self._ask_yes_no(
            "Automatische Backups aktivieren?",
            data["schedule"]["enabled"],
        )
        data["schedule"]["enabled"] = enabled
        if not enabled:
            return
        data["schedule"]["daily_time"] = self._ask_schedule_time(
            data["schedule"]["daily_time"]
        )
        data["schedule"]["interval_days"] = self._ask_interval_days(
            data["schedule"]["interval_days"]
        )

    def _ask_schedule_time(self, default: str) -> str:
        while True:
            value = input(f"Backup-Uhrzeit [{default}]: ").strip() or default
            try:
                parsed = datetime.strptime(value, "%H:%M")
            except ValueError:
                Console.error("Bitte eine Uhrzeit im Format HH:MM eingeben.")
                continue
            return parsed.strftime("%H:%M")

    def _ask_interval_days(self, default: int) -> int:
        while True:
            value = input(f"Backup alle wie viele Tage? [{default}]: ").strip()
            try:
                interval = int(value) if value else default
            except ValueError:
                interval = 0
            if 1 <= interval <= 365:
                return interval
            Console.error("Das Intervall muss zwischen 1 und 365 Tagen liegen.")

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
        Console.warning("WICHTIG: Das Repository-Passwort kann nicht wiederhergestellt werden.")
        Console.info(
            "Weder Linux Backup Manager noch Restic oder die Projektentwickler "
            "können ein vergessenes Passwort zurücksetzen."
        )
        Console.info(
            "Bewahren Sie das Passwort oder eine geschützte Kopie der Passwortdatei "
            "getrennt vom Backup-Repository auf."
        )
        confirmation = input(
            "Ich habe den möglichen Datenverlust verstanden. Fortfahren? [j/N]: "
        )
        if confirmation.strip().lower() != "j":
            Console.warning("Passworterstellung wurde nicht bestätigt.")
            return False

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

        if result.status is RepositoryStatus.WRONG_PASSWORD:
            Console.error(f"Repository-Passwort ungültig: {destination.name}")
            Console.info(result.message)
            Console.info(
                "Bitte die konfigurierte Passwortdatei prüfen. "
                "Das Repository wird nicht neu initialisiert."
            )
            return False

        if result.status is RepositoryStatus.ERROR:
            Console.error(f"Repository konnte nicht geprüft werden: {destination.name}")
            Console.info(result.message)
            return False

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

    def _check_scheduler(self) -> bool:
        if self.config is None or not self.config.schedule.enabled:
            return True
        return SystemdScheduler(self.config_file, self.config.schedule).install()

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
        status &= self._check_scheduler()
        self._print_summary(status)
        return status
