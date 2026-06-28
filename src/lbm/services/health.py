from pathlib import Path

from lbm.core.config import AppConfig
from lbm.health.checks import HealthChecker, HealthResult
from lbm.services.language import LanguageService
from lbm.services.repository import RepositoryProvider


class HealthService:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.language = LanguageService(config.system.language)

    def run(self) -> None:
        checker = HealthChecker(Path(self.config.paths.password_file), self.language)

        title = self.language.translate("app.title")
        print(title)
        print("=" * len(title))
        print()
        heading = self.language.translate("health.heading")
        print(heading)
        print("-" * len(heading))

        results = checker.run()
        destinations = RepositoryProvider(self.config).get_all()
        enabled_count = int(self.config.targets.usb.enabled) + int(
            self.config.targets.nas.enabled
        )
        if len(destinations) != enabled_count:
            results.append(
                HealthResult(
                    self.language.translate("health.backup_targets"),
                    False,
                    self.language.translate("health.not_all_targets_available"),
                )
            )
        for destination in destinations:
            repository = destination.repository.check()
            results.append(
                HealthResult(
                    destination.name,
                    repository.initialized,
                    self.language.translate("health.repository_ready")
                    if repository.initialized
                    else repository.message,
                )
            )
        for result in results:
            symbol = "✓" if result.ok else "✗"
            print(f"{symbol} {result.name:<16} {result.message}")

        print()
        overall = self.language.translate(
            "common.ok" if all(result.ok for result in results) else "common.error"
        )
        label = self.language.translate("common.overall_status")
        print(f"{label:.<20} {overall}")
