import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from lbm.services.language import LanguageService


@dataclass
class HealthResult:
    name: str
    ok: bool
    message: str


class HealthChecker:
    def __init__(
        self,
        password_file: Path,
        language: LanguageService | None = None,
    ) -> None:
        self.password_file = password_file.expanduser()
        self.language = language or LanguageService()

    def run(self) -> list[HealthResult]:
        results = [
            self.check_python(),
            self.check_restic(),
            self.check_password_file(),
        ]
        return results

    def check_python(self) -> HealthResult:
        version = platform.python_version()
        return HealthResult(self._text("health.python"), True, version)

    def check_restic(self) -> HealthResult:
        return self.check_command(self._text("health.restic"), "restic", ["version"])

    def check_password_file(self) -> HealthResult:
        found = self.password_file.exists()
        return HealthResult(
            self._text("health.password_file"),
            found,
            str(self.password_file) if found else self._text("common.missing"),
        )

    def check_command(self, name: str, command: str, args: list[str]) -> HealthResult:
        if shutil.which(command) is None:
            return HealthResult(name, False, self._text("common.missing"))

        result = subprocess.run(
            [command, *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )

        output = result.stdout.strip() or result.stderr.strip()
        first_line = output.splitlines()[0] if output else self._text("common.found")

        return HealthResult(name, result.returncode == 0, first_line)

    def _text(self, key: str) -> str:
        language = getattr(self, "language", None) or LanguageService()
        return language.translate(key)
