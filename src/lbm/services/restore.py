from pathlib import Path

from lbm.core.config import AppConfig
from lbm.services.language import LanguageService
from lbm.services.repository import RepositoryProvider
from lbm.utils.prompts import is_yes


class RestoreService:
    def __init__(
        self,
        config: AppConfig,
        target: Path | None = None,
        repository_provider: RepositoryProvider | None = None,
    ) -> None:
        self.language = LanguageService(config.system.language)
        self.target = target
        self.repository_provider = repository_provider or RepositoryProvider(config)

    def run(self) -> bool:
        restic = self.repository_provider.get()
        if restic is None:
            return False

        snapshots = restic.snapshots()
        if not snapshots:
            print(self._text("maintenance.no_snapshots"))
            return False

        newest_first = list(reversed(snapshots))
        heading = self._text("restore.available_snapshots")
        print(heading)
        print("-" * len(heading))
        for index, snapshot in enumerate(newest_first, start=1):
            print(f"{index}) {snapshot.snapshot_id} {snapshot.time}")

        selection = input("\n" + self._text("restore.select_snapshot")).strip()
        try:
            index = int(selection)
        except ValueError:
            print(self._text("restore.invalid_input"))
            return False

        if index < 1 or index > len(newest_first):
            print(self._text("restore.snapshot_not_exists"))
            return False

        snapshot = newest_first[index - 1]
        target = self.target or self._ask_target(snapshot.snapshot_id)
        print()
        print(self._text("restore.selected_snapshot"))
        print(self._text("restore.id", value=snapshot.snapshot_id))
        print(self._text("restore.date", value=snapshot.time))
        print(self._text("restore.host", value=snapshot.host))
        print()
        print(self._text("restore.target_directory", path=target))

        if target.exists() and any(target.iterdir()):
            warning = input(self._text("restore.nonempty_target"))
            if not is_yes(warning, self._text("common.yes_short")):
                print(self._text("common.cancelled"))
                return False

        if not is_yes(input(self._text("restore.start")), self._text("common.yes_short")):
            print(self._text("common.cancelled"))
            return False

        result = restic.restore(snapshot.snapshot_id, target)
        print()
        if result.ok:
            print(self._text("restore.success"))
        else:
            print(self._text("restore.failed"))
            print(result.message)
        return result.ok

    def _ask_target(self, snapshot_id: str) -> Path:
        default = Path.home() / "lbm-restore" / snapshot_id
        value = input(self._text("restore.target_prompt", default=default)).strip()
        return Path(value).expanduser() if value else default

    def _text(self, key: str, **values: object) -> str:
        return self.language.translate(key, **values)
