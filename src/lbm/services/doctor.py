import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from stat import S_IMODE

from lbm.backup.restic import ResticRepository
from lbm.core.config import AppConfig, ConfigLoader
from lbm.core.errors import ApplicationError, ConfigurationError
from lbm.core.state import BackupStateStore
from lbm.health.checks import HealthChecker
from lbm.targets.usb import USBTarget


class DoctorStatus(Enum):
    OK = "OK"
    WARNING = "WARNUNG"
    ERROR = "FEHLER"
    SKIPPED = "ÜBERSPRUNGEN"


@dataclass(frozen=True)
class DoctorResult:
    name: str
    status: DoctorStatus
    message: str


@dataclass(frozen=True)
class DoctorDestination:
    name: str
    repository: ResticRepository | None
    reachable: bool


class DoctorService:
    """Run read-only diagnostics without attempting repairs."""

    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file

    def run(self) -> bool:
        results: list[DoctorResult] = []
        config = self._check_config(results)
        restic_available = self._check_restic(results)

        if config is None:
            self._append_config_dependent_skips(results)
        else:
            self._check_password_file(config, results)
            destinations = self._check_targets(config, results)
            self._check_repositories(destinations, restic_available, results)
            self._check_last_backup(config, results)

        self._print(results)
        return not any(result.status is DoctorStatus.ERROR for result in results)

    def _check_config(self, results: list[DoctorResult]) -> AppConfig | None:
        try:
            config = ConfigLoader(self.config_file).load()
        except ConfigurationError as error:
            results.append(
                DoctorResult("Konfiguration", DoctorStatus.ERROR, error.message)
            )
            return None

        results.append(
            DoctorResult("Konfiguration", DoctorStatus.OK, str(self.config_file))
        )
        return config

    def _check_restic(self, results: list[DoctorResult]) -> bool:
        try:
            result = HealthChecker(Path("unused")).check_restic()
        except (OSError, subprocess.SubprocessError) as error:
            results.append(
                DoctorResult(
                    "Restic",
                    DoctorStatus.ERROR,
                    f"nicht prüfbar: {self._first_line(str(error))}",
                )
            )
            return False
        status = DoctorStatus.OK if result.ok else DoctorStatus.ERROR
        results.append(DoctorResult("Restic", status, result.message))
        return result.ok

    def _check_password_file(
        self,
        config: AppConfig,
        results: list[DoctorResult],
    ) -> None:
        password_file = Path(config.paths.password_file).expanduser()
        try:
            if not password_file.is_file():
                results.append(
                    DoctorResult("Passwortdatei", DoctorStatus.ERROR, "fehlt")
                )
                return
            mode = S_IMODE(password_file.stat().st_mode)
        except OSError as error:
            results.append(
                DoctorResult(
                    "Passwortdatei",
                    DoctorStatus.ERROR,
                    f"nicht prüfbar: {self._first_line(str(error))}",
                )
            )
            return

        if mode & 0o077 or not mode & 0o400:
            results.append(
                DoctorResult(
                    "Passwortdatei",
                    DoctorStatus.ERROR,
                    f"unsichere oder unplausible Rechte {mode:04o}: {password_file}",
                )
            )
            return

        results.append(
            DoctorResult(
                "Passwortdatei",
                DoctorStatus.OK,
                f"vorhanden, Rechte {mode:04o}: {password_file}",
            )
        )

    def _check_targets(
        self,
        config: AppConfig,
        results: list[DoctorResult],
    ) -> list[DoctorDestination]:
        destinations: list[DoctorDestination] = []
        password_file = Path(config.paths.password_file).expanduser()
        usb = config.targets.usb

        if usb.enabled:
            name = f"USB: {usb.label}"
            try:
                info = USBTarget(usb.label).probe()
            except OSError as error:
                results.append(
                    DoctorResult(
                        name,
                        DoctorStatus.ERROR,
                        f"nicht prüfbar: {self._first_line(str(error))}",
                    )
                )
                destinations.append(DoctorDestination(name, None, False))
                info = None
            if info is not None:
                if not info.found:
                    results.append(
                        DoctorResult(name, DoctorStatus.ERROR, "nicht gefunden")
                    )
                    destinations.append(DoctorDestination(name, None, False))
                elif info.mountpoint is None:
                    results.append(
                        DoctorResult(name, DoctorStatus.ERROR, "nicht eingehängt")
                    )
                    destinations.append(DoctorDestination(name, None, False))
                elif not info.writable:
                    results.append(
                        DoctorResult(
                            name,
                            DoctorStatus.ERROR,
                            f"eingehängt, aber nicht beschreibbar: {info.mountpoint}",
                        )
                    )
                    destinations.append(DoctorDestination(name, None, False))
                else:
                    results.append(
                        DoctorResult(
                            name,
                            DoctorStatus.OK,
                            f"erreichbar: {info.mountpoint}",
                        )
                    )
                    destinations.append(
                        DoctorDestination(
                            name,
                            ResticRepository(
                                info.mountpoint / usb.repository_path,
                                password_file,
                            ),
                            True,
                        )
                    )

        nas = config.targets.nas
        if nas.enabled:
            mount_path = Path(nas.mount_path).expanduser()
            name = f"NAS: {mount_path}"
            if not mount_path.is_dir():
                results.append(DoctorResult(name, DoctorStatus.ERROR, "nicht erreichbar"))
                destinations.append(DoctorDestination(name, None, False))
            elif not os.access(mount_path, os.W_OK):
                results.append(
                    DoctorResult(name, DoctorStatus.ERROR, "nicht beschreibbar")
                )
                destinations.append(DoctorDestination(name, None, False))
            else:
                results.append(DoctorResult(name, DoctorStatus.OK, "erreichbar"))
                destinations.append(
                    DoctorDestination(
                        name,
                        ResticRepository(
                            mount_path / nas.repository_path,
                            password_file,
                        ),
                        True,
                    )
                )

        return destinations

    def _check_repositories(
        self,
        destinations: list[DoctorDestination],
        restic_available: bool,
        results: list[DoctorResult],
    ) -> None:
        for destination in destinations:
            name = f"Repository {destination.name}"
            if not destination.reachable or destination.repository is None:
                results.append(
                    DoctorResult(name, DoctorStatus.SKIPPED, "Ziel nicht erreichbar")
                )
                continue
            if not restic_available:
                results.append(
                    DoctorResult(name, DoctorStatus.SKIPPED, "Restic nicht verfügbar")
                )
                continue

            try:
                info = destination.repository.check(timeout_seconds=30)
            except (ApplicationError, OSError, subprocess.SubprocessError) as error:
                message = getattr(error, "message", str(error))
                results.append(
                    DoctorResult(name, DoctorStatus.ERROR, self._first_line(message))
                )
                continue

            status = DoctorStatus.OK if info.initialized else DoctorStatus.ERROR
            results.append(
                DoctorResult(name, status, self._first_line(info.message) or "unbekannt")
            )

    def _check_last_backup(
        self,
        config: AppConfig,
        results: list[DoctorResult],
    ) -> None:
        try:
            completed_at = BackupStateStore.from_config(
                config.paths.state_dir
            ).last_successful_backup()
        except OSError as error:
            results.append(
                DoctorResult(
                    "Letztes Backup",
                    DoctorStatus.ERROR,
                    f"nicht prüfbar: {self._first_line(str(error))}",
                )
            )
            return
        if completed_at is None:
            results.append(
                DoctorResult(
                    "Letztes Backup",
                    DoctorStatus.WARNING,
                    "kein erfolgreicher Zeitpunkt gespeichert",
                )
            )
            return

        timestamp = completed_at.astimezone().strftime("%d.%m.%Y %H:%M:%S %Z")
        results.append(DoctorResult("Letztes Backup", DoctorStatus.OK, timestamp))

    def _append_config_dependent_skips(self, results: list[DoctorResult]) -> None:
        for name in ("Passwortdatei", "Backup-Ziele", "Repositories", "Letztes Backup"):
            results.append(
                DoctorResult(name, DoctorStatus.SKIPPED, "Konfiguration nicht ladbar")
            )

    def _print(self, results: list[DoctorResult]) -> None:
        symbols = {
            DoctorStatus.OK: "✓",
            DoctorStatus.WARNING: "!",
            DoctorStatus.ERROR: "✗",
            DoctorStatus.SKIPPED: "-",
        }
        print("Linux Backup Manager Doctor")
        print("===========================")
        print()
        for result in results:
            print(
                f"{symbols[result.status]} {result.name:<28} "
                f"{result.status.value}: {result.message}"
            )

        statuses = {result.status for result in results}
        if DoctorStatus.ERROR in statuses:
            overall = "FEHLER"
        elif DoctorStatus.WARNING in statuses:
            overall = "WARNUNG"
        else:
            overall = "OK"
        print()
        print(f"Gesamtstatus............... {overall}")
        print("Es wurden keine Reparaturen oder Konfigurationsänderungen durchgeführt.")

    @staticmethod
    def _first_line(message: str) -> str:
        return message.strip().splitlines()[0] if message.strip() else ""
