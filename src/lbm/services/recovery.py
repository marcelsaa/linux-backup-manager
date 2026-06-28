from datetime import datetime
from pathlib import Path
from stat import S_IMODE

from lbm import __version__
from lbm.core.config import AppConfig
from lbm.core.errors import RecoverySheetError
from lbm.services.language import LanguageService
from lbm.ui.console import Console


class RecoveryInfoService:
    """Display recovery-critical metadata without reading repository secrets."""

    def __init__(self, config: AppConfig, config_file: Path) -> None:
        self.config = config
        self.config_file = config_file
        self.password_file = Path(config.paths.password_file).expanduser()
        self.language = LanguageService(config.system.language)

    def run(self) -> None:
        print(self._text("app.title"))
        heading = self._text("recovery_info.heading")
        print(heading)
        print("=" * len(heading))
        print()
        Console.warning(self._text("recovery_info.password_not_recoverable"))
        print(self._text("recovery_info.password_required"))

        self._print_files()
        self._print_targets()
        self._print_recovery_steps()

    def _print_files(self) -> None:
        print()
        self._heading("recovery_info.important_files")
        self._line("recovery_info.configuration", self.config_file)
        self._line("recovery_info.password_file", self.password_file)
        self._line("recovery_info.password_status", self._password_status())
        self._line("recovery_info.config_copy", f"{self.config_file}.bak")

    def _password_status(self) -> str:
        try:
            mode = S_IMODE(self.password_file.stat().st_mode)
        except FileNotFoundError:
            return self._text("common.missing_upper")
        except OSError:
            return self._text("recovery_info.not_checkable")
        return self._text("recovery_info.present_permissions", mode=f"{mode:04o}")

    def _print_targets(self) -> None:
        print()
        self._heading("recovery_info.configured_targets")

        usb = self.config.targets.usb
        if usb.enabled:
            self._line("recovery_info.usb_label", usb.label)
            self._line("recovery_info.usb_repository", usb.repository_path)

        nas = self.config.targets.nas
        if nas.enabled:
            repository = Path(nas.mount_path).expanduser() / nas.repository_path
            self._line("recovery_info.nas_repository", repository)

    def _print_recovery_steps(self) -> None:
        print()
        self._heading("recovery_info.emergency_steps")
        for number in range(1, 8):
            print(
                self._text(
                    f"recovery_info.step_{number}",
                    password_file=self.password_file,
                )
            )
        print()
        Console.info(self._text("recovery_info.store_separately"))

    def _heading(self, key: str) -> None:
        heading = self._text(key)
        print(heading)
        print("-" * len(heading))

    def _line(self, key: str, value: object) -> None:
        print(f"{self._text(key):.<21} {value}")

    def _text(self, key: str, **values: object) -> str:
        return self.language.translate(key, **values)


class RecoverySheetService:
    """Create a password-free recovery sheet with restrictive permissions."""

    def __init__(self, config: AppConfig, config_file: Path) -> None:
        self.config = config
        self.config_file = config_file
        self.password_file = Path(config.paths.password_file).expanduser()
        self.language = LanguageService(config.system.language)

    def run(self) -> bool:
        title = self._text("recovery_sheet.title")
        print(title)
        print("=" * len(title))
        print()
        Console.warning(self._text("recovery_sheet.no_password"))
        Console.info(self._text("recovery_sheet.not_password_backup"))

        target = self._ask_target()
        if target.exists():
            answer = input(self._text("recovery_sheet.overwrite", path=target))
            if not self._is_yes(answer):
                Console.warning(self._text("recovery_sheet.not_overwritten"))
                return False

        self._write(target, self._render())
        Console.success(self._text("recovery_sheet.created", path=target))
        Console.info(self._text("recovery_sheet.store_safely"))
        return True

    def _ask_target(self) -> Path:
        default = Path.home() / "linux-backup-manager-recovery.txt"
        value = input(self._text("recovery_sheet.output_file", default=default)).strip()
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
                self._text("recovery_sheet.write_failed"),
                hint=self._text("recovery_sheet.write_hint", path=target),
            ) from error

    def _render(self) -> str:
        generated = datetime.now().astimezone().isoformat(timespec="seconds")
        lines = [
            self._text("recovery_sheet.document.title"),
            "=" * len(self._text("recovery_sheet.document.title")),
            "",
            self._text("recovery_sheet.document.warning"),
            self._text("recovery_sheet.document.password_required"),
            "",
            self._text("recovery_sheet.document.system"),
            "-" * len(self._text("recovery_sheet.document.system")),
            self._text("recovery_sheet.document.created", value=generated),
            self._text("recovery_sheet.document.version", value=__version__),
            self._text("recovery_sheet.document.host", value=self.config.system.host_name),
            "",
            self._text("recovery_sheet.document.files"),
            "-" * len(self._text("recovery_sheet.document.files")),
            self._text("recovery_sheet.document.configuration", value=self.config_file),
            self._text("recovery_sheet.document.config_copy", value=f"{self.config_file}.bak"),
            self._text("recovery_sheet.document.password_file", value=self.password_file),
            "",
            self._text("recovery_sheet.document.targets"),
            "-" * len(self._text("recovery_sheet.document.targets")),
            *self._target_lines(),
            "",
            self._text("recovery_sheet.document.external_records"),
            "-" * len(self._text("recovery_sheet.document.external_records")),
            self._text("recovery_sheet.document.password_copy_location"),
            self._text("recovery_sheet.document.config_copy_location"),
            self._text("recovery_sheet.document.restore_test_date"),
            self._text("recovery_sheet.document.notes"),
            "",
            self._text("recovery_sheet.document.emergency_steps"),
            "-" * len(self._text("recovery_sheet.document.emergency_steps")),
            *[
                self._text(
                    f"recovery_sheet.document.step_{number}",
                    password_file=self.password_file,
                )
                for number in range(1, 9)
            ],
            "",
            self._text("recovery_sheet.document.keep_separate"),
            self._text("recovery_sheet.document.access_warning"),
            "",
        ]
        return "\n".join(lines)

    def _target_lines(self) -> list[str]:
        lines: list[str] = []
        usb = self.config.targets.usb
        if usb.enabled:
            lines.extend(
                [
                    self._text("recovery_sheet.document.usb_label", value=usb.label),
                    self._text(
                        "recovery_sheet.document.usb_repository",
                        value=usb.repository_path,
                    ),
                ]
            )

        nas = self.config.targets.nas
        if nas.enabled:
            repository = Path(nas.mount_path).expanduser() / nas.repository_path
            lines.append(
                self._text("recovery_sheet.document.nas_repository", value=repository)
            )
        return lines

    def _is_yes(self, answer: str) -> bool:
        return answer.strip().lower() in {"j", "y", self._text("common.yes_short")}

    def _text(self, key: str, **values: object) -> str:
        return self.language.translate(key, **values)
