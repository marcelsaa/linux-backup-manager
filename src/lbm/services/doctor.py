import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from stat import S_IMODE

from lbm.backup.restic import ResticRepository
from lbm.core.config import AppConfig, ConfigLoader
from lbm.core.errors import ApplicationError, ConfigurationError
from lbm.core.state import BackupStateStore
from lbm.health.checks import HealthChecker
from lbm.services.language import LanguageService
from lbm.targets.usb import USBTarget
from lbm.ui.console import Console


class DoctorStatus(Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class DoctorResult:
    name: str
    status: DoctorStatus
    message: str


_SECTION_ORDER = ("config", "programs", "security", "targets", "repositories", "schedule")


@dataclass(frozen=True)
class DoctorDestination:
    name: str
    repository: ResticRepository | None
    reachable: bool


class DoctorService:
    """Run read-only diagnostics without attempting repairs."""

    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file
        self.language = LanguageService()

    def run(self) -> bool:
        sections: dict[str, list[DoctorResult]] = {key: [] for key in _SECTION_ORDER}
        config = self._check_config(sections["config"])
        restic_available = self._check_restic(sections["programs"])

        if config is None:
            self._append_config_dependent_skips(sections)
        else:
            self._check_password_file(config, sections["security"])
            destinations = self._check_targets(config, sections["targets"])
            self._check_repositories(destinations, restic_available, sections["repositories"])
            self._check_last_backup(config, sections["schedule"])
            self._check_timer(config, sections["schedule"])

        self._print(sections)
        return not any(
            result.status is DoctorStatus.ERROR
            for lst in sections.values()
            for result in lst
        )

    def _check_config(self, results: list[DoctorResult]) -> AppConfig | None:
        loader = ConfigLoader(self.config_file)
        try:
            config = loader.load()
        except ConfigurationError as error:
            language = loader.detect_language() or LanguageService.default_language
            self.language = LanguageService(language)
            results.append(
                DoctorResult(
                    self._text("doctor.configuration"),
                    DoctorStatus.ERROR,
                    error.message,
                )
            )
            return None

        self.language = LanguageService(config.system.language)
        results.append(
            DoctorResult(
                self._text("doctor.configuration"),
                DoctorStatus.OK,
                str(self.config_file),
            )
        )
        return config

    def _check_restic(self, results: list[DoctorResult]) -> bool:
        try:
            result = HealthChecker(Path("unused"), self.language).check_restic()
        except (OSError, subprocess.SubprocessError) as error:
            results.append(
                DoctorResult(
                    self._text("doctor.restic"),
                    DoctorStatus.ERROR,
                    self._text(
                        "doctor.not_checkable",
                        error=self._first_line(str(error)),
                    ),
                )
            )
            return False
        status = DoctorStatus.OK if result.ok else DoctorStatus.ERROR
        results.append(
            DoctorResult(self._text("doctor.restic"), status, result.message)
        )
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
                    DoctorResult(
                        self._text("doctor.password_file"),
                        DoctorStatus.ERROR,
                        self._text("common.missing"),
                    )
                )
                return
            mode = S_IMODE(password_file.stat().st_mode)
        except OSError as error:
            results.append(
                DoctorResult(
                    self._text("doctor.password_file"),
                    DoctorStatus.ERROR,
                    self._text(
                        "doctor.not_checkable",
                        error=self._first_line(str(error)),
                    ),
                )
            )
            return

        if mode & 0o077 or not mode & 0o400:
            results.append(
                DoctorResult(
                    self._text("doctor.password_file"),
                    DoctorStatus.ERROR,
                    self._text(
                        "doctor.unsafe_permissions",
                        mode=f"{mode:04o}",
                        path=password_file,
                    ),
                )
            )
            return

        results.append(
            DoctorResult(
                self._text("doctor.password_file"),
                DoctorStatus.OK,
                self._text(
                    "doctor.password_present",
                    mode=f"{mode:04o}",
                    path=password_file,
                ),
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
                        self._text(
                            "doctor.not_checkable",
                            error=self._first_line(str(error)),
                        ),
                    )
                )
                destinations.append(DoctorDestination(name, None, False))
                info = None
            if info is not None:
                if not info.found:
                    results.append(
                        DoctorResult(
                            name,
                            DoctorStatus.ERROR,
                            self._text("doctor.not_found"),
                        )
                    )
                    destinations.append(DoctorDestination(name, None, False))
                elif info.mountpoint is None:
                    results.append(
                        DoctorResult(
                            name,
                            DoctorStatus.ERROR,
                            self._text("doctor.not_mounted"),
                        )
                    )
                    destinations.append(DoctorDestination(name, None, False))
                elif not info.writable:
                    results.append(
                        DoctorResult(
                            name,
                            DoctorStatus.ERROR,
                            self._text(
                                "doctor.mounted_not_writable",
                                path=info.mountpoint,
                            ),
                        )
                    )
                    destinations.append(DoctorDestination(name, None, False))
                else:
                    results.append(
                        DoctorResult(
                            name,
                            DoctorStatus.OK,
                            self._text("doctor.reachable_path", path=info.mountpoint),
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
                results.append(
                    DoctorResult(
                        name,
                        DoctorStatus.ERROR,
                        self._text("doctor.not_reachable"),
                    )
                )
                destinations.append(DoctorDestination(name, None, False))
            elif not os.access(mount_path, os.W_OK):
                results.append(
                    DoctorResult(
                        name,
                        DoctorStatus.ERROR,
                        self._text("doctor.not_writable"),
                    )
                )
                destinations.append(DoctorDestination(name, None, False))
            else:
                results.append(
                    DoctorResult(name, DoctorStatus.OK, self._text("doctor.reachable"))
                )
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
            name = self._text("doctor.repository", target=destination.name)
            if not destination.reachable or destination.repository is None:
                results.append(
                    DoctorResult(
                        name,
                        DoctorStatus.SKIPPED,
                        self._text("doctor.target_not_reachable"),
                    )
                )
                continue
            if not restic_available:
                results.append(
                    DoctorResult(
                        name,
                        DoctorStatus.SKIPPED,
                        self._text("doctor.restic_unavailable"),
                    )
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
            message = (
                self._text("doctor.repository_ready")
                if info.initialized
                else self._first_line(info.message) or self._text("common.unknown")
            )
            results.append(DoctorResult(name, status, message))

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
                    self._text("doctor.last_backup"),
                    DoctorStatus.ERROR,
                    self._text(
                        "doctor.not_checkable",
                        error=self._first_line(str(error)),
                    ),
                )
            )
            return
        if completed_at is None:
            results.append(
                DoctorResult(
                    self._text("doctor.last_backup"),
                    DoctorStatus.WARNING,
                    self._text("doctor.no_success_time"),
                )
            )
            return

        now = datetime.now(UTC)
        delta = now - completed_at
        timestamp = completed_at.astimezone().strftime("%d.%m.%Y %H:%M:%S %Z")
        age = self._format_age(delta)
        overdue = (
            config.schedule.enabled
            and delta.total_seconds() > config.schedule.interval_days * 86400
        )
        if overdue:
            results.append(DoctorResult(
                self._text("doctor.last_backup"),
                DoctorStatus.WARNING,
                self._text("doctor.last_backup_overdue", timestamp=timestamp, age=age),
            ))
        else:
            results.append(DoctorResult(
                self._text("doctor.last_backup"), DoctorStatus.OK, f"{timestamp} ({age})"
            ))

    def _check_timer(self, config: AppConfig, results: list[DoctorResult]) -> None:
        if not config.schedule.enabled:
            results.append(DoctorResult(
                self._text("doctor.timer"),
                DoctorStatus.SKIPPED,
                self._text("doctor.timer_not_configured"),
            ))
            return
        if shutil.which("systemctl") is None:
            results.append(DoctorResult(
                self._text("doctor.timer"),
                DoctorStatus.WARNING,
                self._text("doctor.timer_systemd_missing"),
            ))
            return
        enabled = self._systemctl_check("is-enabled", "linux-backup-manager-daily.timer")
        active = self._systemctl_check("is-active", "linux-backup-manager-daily.timer")
        if enabled and active:
            results.append(DoctorResult(
                self._text("doctor.timer"), DoctorStatus.OK, self._text("doctor.timer_active")
            ))
        elif enabled:
            results.append(DoctorResult(
                self._text("doctor.timer"),
                DoctorStatus.WARNING,
                self._text("doctor.timer_enabled_not_active"),
            ))
        else:
            results.append(DoctorResult(
                self._text("doctor.timer"),
                DoctorStatus.WARNING,
                self._text("doctor.timer_not_installed"),
            ))

    def _systemctl_check(self, *args: str) -> bool:
        try:
            result = subprocess.run(
                ["systemctl", "--user", *args],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False

    def _format_age(self, delta: timedelta) -> str:
        total_seconds = int(delta.total_seconds())
        if total_seconds < 3600:
            return self._text("common.age_minutes", minutes=max(1, total_seconds // 60))
        if total_seconds < 86400:
            return self._text("common.age_hours", hours=total_seconds // 3600)
        return self._text("common.age_days", days=delta.days)

    def _append_config_dependent_skips(
        self, sections: dict[str, list[DoctorResult]]
    ) -> None:
        skip_msg = self._text("doctor.config_not_loadable")
        sections["security"].append(
            DoctorResult(self._text("doctor.password_file"), DoctorStatus.SKIPPED, skip_msg)
        )
        sections["targets"].append(
            DoctorResult(self._text("doctor.backup_targets"), DoctorStatus.SKIPPED, skip_msg)
        )
        sections["repositories"].append(
            DoctorResult(self._text("doctor.repositories"), DoctorStatus.SKIPPED, skip_msg)
        )
        sections["schedule"].append(
            DoctorResult(self._text("doctor.last_backup"), DoctorStatus.SKIPPED, skip_msg)
        )
        sections["schedule"].append(
            DoctorResult(self._text("doctor.timer"), DoctorStatus.SKIPPED, skip_msg)
        )

    def _print(self, sections: dict[str, list[DoctorResult]]) -> None:
        colors = {
            DoctorStatus.OK: Console.GREEN,
            DoctorStatus.WARNING: Console.YELLOW,
            DoctorStatus.ERROR: Console.RED,
            DoctorStatus.SKIPPED: "",
        }
        symbols = {
            DoctorStatus.OK: "✓",
            DoctorStatus.WARNING: "!",
            DoctorStatus.ERROR: "✗",
            DoctorStatus.SKIPPED: "-",
        }
        section_titles = {
            "config": self._text("doctor.section_config"),
            "programs": self._text("doctor.section_programs"),
            "security": self._text("doctor.section_security"),
            "targets": self._text("doctor.section_targets"),
            "repositories": self._text("doctor.section_repositories"),
            "schedule": self._text("doctor.section_schedule"),
        }

        title = self._text("doctor.title")
        print(title)
        print("=" * len(title))

        for key, section_results in sections.items():
            if not section_results:
                continue
            label = section_titles[key]
            print(f"\n── {label} {'─' * max(0, 48 - len(label) - 4)}")
            for result in section_results:
                color = colors[result.status]
                reset = Console.RESET if color else ""
                symbol = symbols[result.status]
                status_text = self._text(f"doctor.status.{result.status.value}")
                print(f"{color}{symbol}{reset} {result.name:<28} {status_text}: {result.message}")

        all_results = [r for lst in sections.values() for r in lst]
        counts = {s: sum(1 for r in all_results if r.status is s) for s in DoctorStatus}
        print()
        print(self._text(
            "doctor.summary",
            ok=counts[DoctorStatus.OK],
            warnings=counts[DoctorStatus.WARNING],
            errors=counts[DoctorStatus.ERROR],
            skipped=counts[DoctorStatus.SKIPPED],
        ))
        print()
        label = self._text("common.overall_status")
        if counts[DoctorStatus.ERROR]:
            Console.error(f"{label}: {self._text('doctor.status.error')}")
        elif counts[DoctorStatus.WARNING]:
            Console.warning(f"{label}: {self._text('doctor.status.warning')}")
        else:
            Console.success(f"{label}: {self._text('doctor.status.ok')}")
        print(self._text("doctor.no_changes"))

    def _text(self, key: str, **values: object) -> str:
        return self.language.translate(key, **values)

    @staticmethod
    def _first_line(message: str) -> str:
        return message.strip().splitlines()[0] if message.strip() else ""
