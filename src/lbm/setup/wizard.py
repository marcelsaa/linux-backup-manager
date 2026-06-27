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
        print("Linux Backup Manager Setup")
        print("==========================")
        print()
        print("Willkommen zum Einrichtungsassistenten.")
        print()

        all_ok = True

        if self.config_file.exists():
            print("✓ config.yaml vorhanden")
        else:
            print("✗ config.yaml fehlt")
            all_ok = False

        if self.password_file.exists():
            print("✓ Passwortdatei vorhanden")
        else:
            print("✗ Passwortdatei fehlt")
            all_ok = False

            if not self.interactive:
                print("Passwortdatei fehlt. Automatische Erstellung übersprungen.")
            else:
                answer = input("Passwortdatei jetzt erstellen? [J/n]: ").strip().lower()

                if answer in ("", "j"):
                    if self._create_password_file():
                        print("✓ Passwortdatei vorhanden")
                    else:
                        all_ok = False
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
            all_ok = False
            print()
            print("Setup abgeschlossen, es bestehen noch offene Punkte.")
            return

        if info.mountpoint:
            repository = Path(info.mountpoint) / self.repository_path

            restic = ResticRepository(
                repository,
                self.password_file,
            )

            if restic.check().initialized:
                print("✓ Repository vorhanden")
            else:
                print("✗ Repository fehlt")
                all_ok = False

                if not self.interactive:
                    print("Repository fehlt. Automatische Erstellung übersprungen.")
                else:
                    answer = input("Repository jetzt erstellen? [J/n]: ").strip().lower()

                    if answer in ("", "j"):
                        if self._create_repository():
                            print("✓ Repository vorhanden")
                        else:
                            all_ok = False
                    else:
                        print("Repository wurde nicht erstellt.")
        else:
            print("✗ USB-Laufwerk ist nicht eingehängt")
            all_ok = False

        print()

        if all_ok:
            print("System ist vollständig eingerichtet.")
        else:
            print("Setup abgeschlossen, es bestehen noch offene Punkte.")