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
    ) -> None:
        self.config_file = config_file
        self.password_file = password_file.expanduser()
        self.usb_label = usb_label
        self.repository_path = repository_path

    def _check_program(self, program: str, name: str) -> None:
        if which(program):
            print(f"✓ {name} installiert")
        else:
            print(f"✗ {name} fehlt")

    def _create_password_file(self) -> bool:
        print()

        password = getpass("Neues Repository-Passwort: ")
        confirmation = getpass("Passwort wiederholen: ")

        if password != confirmation:
            print("Passwörter stimmen nicht überein.")
            return False

        self.password_file.parent.mkdir(parents=True, exist_ok=True)
        self.password_file.write_text(password)

        self.password_file.chmod(0o600)

        print("✓ Passwortdatei erstellt.")

        return True

    def run(self) -> None:
        print("Linux Backup Manager Setup")
        print("==========================")
        print()
        print("Willkommen zum Einrichtungsassistenten.")
        print()

        if self.config_file.exists():
            print("✓ config.yaml vorhanden")
        else:
            print("✗ config.yaml fehlt")
        
        if self.password_file.exists():
            print("✓ Passwortdatei vorhanden")
        else:
            print("✗ Passwortdatei fehlt")
            answer = input("Passwortdatei jetzt erstellen? [J/n]: ").strip().lower()

            if answer in ("", "j"):
                self._create_password_file()
            else:
                print("Passwortdatei wurde nicht erstellt.")
        
        self._check_program("restic", "Restic")
        self._check_program("timeshift", "Timeshift")

        usb = USBTarget(self.usb_label)
        info = usb.probe()
        if info.found:
            print(f"✓ USB-Laufwerk '{self.usb_label}' gefunden")
        else:
            print(f"✗ USB-Laufwerk '{self.usb_label}' nicht gefunden")
        usb = USBTarget(self.usb_label)
        info = usb.probe()

        if info.found and info.mountpoint:
            repository = Path(info.mountpoint) / self.repository_path

            restic = ResticRepository(
                repository,
                self.password_file,
            )

            if restic.check().initialized:
                print("✓ Repository vorhanden")
            else:
                print("✗ Repository fehlt")