from pathlib import Path

from lbm.core.config import AppConfig
from lbm.health.checks import HealthChecker


class HealthService:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def run(self) -> None:
        checker = HealthChecker(
            Path(self.config.paths.password_file),
            self.config.targets.usb.label,
            self.config.targets.usb.repository_path,
        )

        print("Linux Backup Manager")
        print("====================")
        print()
        print("Health Check")
        print("------------")

        results = checker.run()
        for result in results:
            symbol = "✓" if result.ok else "✗"
            print(f"{symbol} {result.name:<16} {result.message}")

        print()
        print(f"Gesamtstatus........ {'OK' if all(result.ok for result in results) else 'FEHLER'}")
