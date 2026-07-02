from lbm.core.config import AppConfig
from lbm.services.language import LanguageService
from lbm.services.repository import RepositoryProvider
from lbm.ui.console import Console
from lbm.utils.prompts import is_yes


class RepositoryMaintenanceService:
    def __init__(
        self,
        config: AppConfig,
        repository_provider: RepositoryProvider | None = None,
    ) -> None:
        self.config = config
        self.language = LanguageService(config.system.language)
        self.repository_provider = repository_provider or RepositoryProvider(config)

    def init_repository(self) -> None:
        restic = self.repository_provider.get()
        if restic is None:
            return
        if restic.check().initialized:
            print(self._text("maintenance.repository_exists"))
            return

        print(self._text("maintenance.create_at", path=restic.repository))
        yes_short = self._text("common.yes_short")
        if not is_yes(input(self._text("maintenance.continue_prompt")), yes_short):
            print(self._text("common.cancelled"))
            return

        result = restic.init_repository()
        if result.initialized:
            print(self._text("maintenance.repository_created"))
        else:
            print(self._text("maintenance.create_failed"))
            print(result.message)

    def snapshots(self) -> None:
        restic = self.repository_provider.get()
        if restic is None:
            return
        snapshots = restic.snapshots()
        if not snapshots:
            print(self._text("maintenance.no_snapshots"))
            return

        title = self._text("app.title")
        print(title)
        print("=" * len(title))
        print()
        heading = self._text("maintenance.snapshots")
        print(heading)
        print("-" * len(heading))
        date_label = self._text("maintenance.date")
        host_label = self._text("maintenance.host")
        print(f"{'':<2}{'ID':<8} {date_label:<20} {host_label}")
        print("-" * 45)
        for index, snapshot in enumerate(reversed(snapshots)):
            marker = "*" if index == 0 else " "
            print(f"{marker} {snapshot.snapshot_id:<8} {snapshot.time:<20} {snapshot.host}")
        print()
        print(self._text("maintenance.snapshot_count", count=len(snapshots)))

    def stats(self) -> None:
        restic = self.repository_provider.get()
        if restic is None:
            return
        stats = restic.stats()
        title = self._text("app.title")
        print(title)
        print("=" * len(title))
        print()
        heading = self._text("maintenance.statistics")
        print(heading)
        print("-" * len(heading))
        self._line("maintenance.snapshots", stats.snapshot_count)
        self._line("maintenance.first_snapshot", stats.first_snapshot)
        self._line("maintenance.last_snapshot", stats.last_snapshot)
        self._line("maintenance.host", stats.host)

    def check(self) -> None:
        restic = self.repository_provider.get()
        if restic is None:
            return
        Console.info(self._text("maintenance.checking"))
        print()
        result = restic.check_repository()
        if result.initialized:
            Console.success(self._text("maintenance.check_success"))
        else:
            Console.error(self._text("maintenance.check_failed"))
            Console.error(result.message)

    def forget(self) -> None:
        restic = self.repository_provider.get()
        if restic is None:
            return

        retention = self.config.retention
        heading = self._text("maintenance.forget_dry_run")
        print(heading)
        print("-" * len(heading))
        dry_run = restic.forget_dry_run(
            keep_daily=retention.keep_daily,
            keep_weekly=retention.keep_weekly,
            keep_monthly=retention.keep_monthly,
            keep_yearly=retention.keep_yearly,
        )
        print(dry_run if dry_run else self._text("maintenance.none_deleted"))
        print()
        yes_short = self._text("common.yes_short")
        if not is_yes(input(self._text("maintenance.delete_snapshots")), yes_short):
            print(self._text("common.cancelled"))
            return

        result = restic.forget(
            keep_daily=retention.keep_daily,
            keep_weekly=retention.keep_weekly,
            keep_monthly=retention.keep_monthly,
            keep_yearly=retention.keep_yearly,
        )
        print()
        print(result if result else self._text("maintenance.forget_complete"))

    def prune(self) -> None:
        restic = self.repository_provider.get()
        if restic is None:
            return
        print(self._text("maintenance.optimizing"))
        print()
        if not is_yes(input(self._text("maintenance.start_prune")), self._text("common.yes_short")):
            print(self._text("common.cancelled"))
            return
        result = restic.prune()
        print()
        print(result if result else self._text("maintenance.prune_complete"))

    def _line(self, key: str, value: object) -> None:
        print(f"{self._text(key):.<22} {value}")

    def _text(self, key: str, **values: object) -> str:
        return self.language.translate(key, **values)
