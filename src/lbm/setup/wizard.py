from getpass import getpass
from pathlib import Path
from shutil import which

from lbm.backup.restic import ResticRepository
from lbm.targets.usb import USBTarget


class SetupWizard:
    def __init__(
        self,
        config_file: Path,
        password_file: Path,
        usb_label: str,
        repository_path: str,
        interactive: bool = True,
    ) -> None:
        self.config_file = config_file
        self.password_file = password_file.expanduser()
        self.usb_label = usb_label
        self.repository_path = repository_path
        self.interactive = interactive

    def _print_header(self) -> None:
        print("Linux Backup Manager Setup")
        print("==========================")
        print()
        print("Willkommen zum Einrichtungsassistenten.")
        print()

    def _print_summary(self, all_ok: bool) -> None:
        print()

        if all_ok:
            print("System ist vollständig eingerichtet.")
        else:
            print("Setup abgeschlossen, es bestehen noch offene Punkte.")

    def _check_config(self) -> bool:
        if self.config_file.exists():
            print("✓ config.yaml vorhanden")
            return True

        print("✗ config.yaml fehlt")
        return False

    def _check_password(self) -> bool:
        if self.password_file.exists():
            print("✓ Passwortdatei vorhanden")
            return True

        print("✗ Passwortdatei fehlt")

        if not self.interactive:
            print("Passwortdatei fehlt. Automatische Erstellung übersprungen.")
            return False

        answer = input("Passwortdatei jetzt erstellen? [J/n]: ").strip().lower()

        if answer in ("", "j") and self._create_password_file():
            print("✓ Passwortdatei vorhanden")
            return True

        print("Passwortdatei wurde nicht erstellt.")
        return False

    def _create_password_file(self) -> bool:
        print()

        password = getpass("Neues Repository-Passwort: ")
        confirmation = getpass("Passwort wiederholen: ")

        if password != confirmation:
            print("Passwörter stimmen nicht überein.")
            return False

        self.password_file.parent.mkdir(parents=True, exist_ok=True)
        self.password_file.write_text(password + "\n")
        self.password_file.chmod(0o600)

        print("✓ Passwortdatei erstellt.")
        return True

    def _check_program(
        self,
        program: str,
        name: str,
    ) -> bool:
        if which(program):
            print(f"✓ {name} installiert")
            return True

        print(f"✗ {name} fehlt")
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
            print(f"✗ USB-Laufwerk '{self.usb_label}' nicht gefunden")
            return None

        print(f"✓ USB-Laufwerk '{self.usb_label}' gefunden")

        if info.mountpoint is None:
            print("✗ USB-Laufwerk ist nicht eingehängt")
            return None

        return info.mountpoint

    def _check_repository(self, mountpoint: str) -> bool:
        repository = Path(mountpoint) / self.repository_path

        restic = ResticRepository(
            repository,
            self.password_file,
        )

        if restic.check().initialized:
            print("✓ Repository vorhanden")
            return True

        print("✗ Repository fehlt")

        if not self.interactive:
            print("Repository fehlt. Automatische Erstellung übersprungen.")
            return False

        answer = input("Repository jetzt erstellen? [J/n]: ").strip().lower()

        if answer in ("", "j") and self._create_repository():
            print("✓ Repository vorhanden")
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
            print("✓ Repository erstellt.")
            return True

        print(result.message)
        return False

    def run(self) -> None:
        self._print_header()

        status = True

        status &= self._check_config()
        status &= self._check_password()
        status &= self._check_programs()

        mountpoint = self._check_usb()

        if mountpoint is None:
            self._print_summary(False)
            return

        status &= self._check_repository(mountpoint)

        self._print_summary(status)