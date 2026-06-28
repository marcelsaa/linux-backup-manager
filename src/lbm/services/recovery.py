from datetime import datetime
from pathlib import Path
from stat import S_IMODE

from lbm import __version__
from lbm.core.config import AppConfig
from lbm.core.errors import RecoverySheetError
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


class RecoverySheetService:
    """Create a password-free recovery sheet with restrictive permissions."""

    def __init__(self, config: AppConfig, config_file: Path) -> None:
        self.config = config
        self.config_file = config_file
        self.password_file = Path(config.paths.password_file).expanduser()

    def run(self) -> bool:
        print("Linux Backup Manager Recovery Sheet")
        print("===================================")
        print()
        Console.warning("Das Recovery Sheet enthält absichtlich kein Passwort.")
        Console.info(
            "Es ersetzt keine getrennt und geschützt aufbewahrte Passwortkopie."
        )

        target = self._ask_target()
        if target.exists():
            answer = input(f"Datei existiert bereits: {target}. Überschreiben? [j/N]: ")
            if answer.strip().lower() != "j":
                Console.warning("Recovery Sheet wurde nicht überschrieben.")
                return False

        self._write(target, self._render())
        Console.success(f"Recovery Sheet erstellt: {target}")
        Console.info("Bitte ausdrucken oder an einem getrennten, geschützten Ort speichern.")
        return True

    def _ask_target(self) -> Path:
        default = Path.home() / "linux-backup-manager-recovery.txt"
        value = input(f"Ausgabedatei [{default}]: ").strip()
        return Path(value).expanduser() if value else default

    def _write(self, target: Path, content: str) -> None:
        temporary = target.with_name(f".{target.name}.tmp")
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary.write_text(content, encoding="utf-8")
            temporary.chmod(0o600)
            temporary.replace(target)
            target.chmod(0o600)
        except OSError as error:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            raise RecoverySheetError(
                "Recovery Sheet konnte nicht sicher gespeichert werden.",
                hint=f"Bitte Ausgabepfad und Schreibrechte prüfen: {target}",
            ) from error

    def _render(self) -> str:
        generated = datetime.now().astimezone().isoformat(timespec="seconds")
        lines = [
            "LINUX BACKUP MANAGER – RECOVERY SHEET",
            "=====================================",
            "",
            "WICHTIG: Dieses Dokument enthält KEIN Repository-Passwort.",
            "Ohne Passwort oder geschützte Passwortdatei sind die Backups unzugänglich.",
            "",
            "SYSTEM",
            "------",
            f"Erstellt: {generated}",
            f"Linux Backup Manager: {__version__}",
            f"Host: {self.config.system.host_name}",
            "",
            "WICHTIGE DATEIEN",
            "----------------",
            f"Konfiguration: {self.config_file}",
            f"Konfigurationskopie: {self.config_file}.bak",
            f"Passwortdatei: {self.password_file}",
            "",
            "REPOSITORY-ZIELE",
            "-----------------",
            *self._target_lines(),
            "",
            "EXTERNE VORSORGE – MANUELL AUSFÜLLEN",
            "------------------------------------",
            "Aufbewahrungsort der Passwortkopie: ______________________________",
            "Aufbewahrungsort der Konfigurationskopie: _________________________",
            "Datum des letzten erfolgreichen Restore-Tests: ____________________",
            "Notizen: __________________________________________________________",
            "",
            "NOTFALLABLAUF",
            "-------------",
            "1. Python 3.12+, Restic und Linux Backup Manager installieren.",
            "2. USB- oder NAS-Backup-Ziel einhängen.",
            "3. Konfiguration und geschützte Passwortdatei wiederherstellen.",
            f"4. Dateirechte setzen: chmod 600 {self.password_file}",
            "5. Zugriff prüfen: backup-manager health",
            "6. Snapshots anzeigen: backup-manager snapshots",
            "7. Repository prüfen: backup-manager check",
            "8. Restore starten: backup-manager restore",
            "",
            "Dieses Sheet getrennt vom Rechner und Backup-Repository aufbewahren.",
            "Wer Repository und Passwort besitzt, kann die Backup-Inhalte lesen.",
            "",
        ]
        return "\n".join(lines)

    def _target_lines(self) -> list[str]:
        lines: list[str] = []
        usb = self.config.targets.usb
        if usb.enabled:
            lines.extend(
                [
                    f"USB-Dateisystemlabel: {usb.label}",
                    f"USB-Repository-Pfad: {usb.repository_path}",
                ]
            )

        nas = self.config.targets.nas
        if nas.enabled:
            repository = Path(nas.mount_path).expanduser() / nas.repository_path
            lines.append(f"NAS-Repository: {repository}")
        return lines
