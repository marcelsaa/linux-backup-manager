from pathlib import Path

from lbm.core.config import AppConfig
from lbm.health.checks import HealthChecker, HealthResult
from lbm.services.repository import RepositoryProvider


class HealthService:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def run(self) -> None:
        checker = HealthChecker(Path(self.config.paths.password_file))

        print("Linux Backup Manager")
        print("====================")
        print()
        print("Health Check")
        print("------------")

        results = checker.run()
        destinations = RepositoryProvider(self.config).get_all()
        enabled_count = int(self.config.targets.usb.enabled) + int(
            self.config.targets.nas.enabled
        )
        if len(destinations) != enabled_count:
            results.append(
                HealthResult("Backup-Ziele", False, "Nicht alle Ziele sind verfügbar")
            )
        for destination in destinations:
            repository = destination.repository.check()
            results.append(
                HealthResult(
                    destination.name,
                    repository.initialized,
                    repository.message,
                )
            )
        for result in results:
            symbol = "✓" if result.ok else "✗"
            print(f"{symbol} {result.name:<16} {result.message}")

        print()
        print(f"Gesamtstatus........ {'OK' if all(result.ok for result in results) else 'FEHLER'}")
