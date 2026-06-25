import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from lbm.targets.usb import USBTarget


@dataclass
class HealthResult:
    name: str
    ok: bool
    message: str


class HealthChecker:
    def __init__(self, password_file: Path, usb_label: str) -> None:
        self.password_file = password_file.expanduser()
        self.usb_label = usb_label

    def run(self) -> list[HealthResult]:
        results = [
            self.check_python(),
            self.check_restic(),
            self.check_timeshift(),
            self.check_password_file(),
        ]

        results.extend(self.check_usb_target())

        return results
    
    def check_usb_target(self) -> list[HealthResult]:
        usb = USBTarget(self.usb_label)
        info = usb.probe()

        if not info.found:
            return [
                HealthResult("USB", False, f"{self.usb_label} nicht gefunden"),
            ]

        if info.mountpoint is None:
            return [
                HealthResult("USB", False, f"{self.usb_label} nicht eingehängt"),
            ]

        return [
            HealthResult("USB-Label", True, info.label),
            HealthResult("USB-Mountpoint", True, info.mountpoint),
            HealthResult("USB-Speicher", True, info.fsavail or "unbekannt"),
            HealthResult("USB-Belegung", True, info.fsuse_percent or "unbekannt"),
            HealthResult("USB-schreibbar", info.writable, "ja" if info.writable else "nein"),
        ]

    def check_python(self) -> HealthResult:
        version = platform.python_version()
        return HealthResult("Python", True, version)

    def check_restic(self) -> HealthResult:
        return self.check_command("Restic", "restic", ["version"])

    def check_timeshift(self) -> HealthResult:
        return self.check_command("Timeshift", "timeshift", ["--version"])

    def check_password_file(self) -> HealthResult:
        found = self.password_file.exists()
        return HealthResult(
            "Passwortdatei",
            found,
            str(self.password_file) if found else "fehlt",
        )

    def check_command(self, name: str, command: str, args: list[str]) -> HealthResult:
        if shutil.which(command) is None:
            return HealthResult(name, False, "fehlt")

        result = subprocess.run(
            [command, *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )

        output = result.stdout.strip() or result.stderr.strip()
        first_line = output.splitlines()[0] if output else "gefunden"

        return HealthResult(name, True, first_line)