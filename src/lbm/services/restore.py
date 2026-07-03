import subprocess
import tempfile
import time
from pathlib import Path

from lbm.backup.restic import ResticRepository, SnapshotInfo
from lbm.core.config import AppConfig
from lbm.services.language import LanguageService
from lbm.services.repository import RepositoryProvider
from lbm.utils.prompts import is_yes
from lbm.utils.system import open_in_file_manager, unmount

_MOUNT_READY_TIMEOUT_SECONDS = 10
_MOUNT_POLL_INTERVAL_SECONDS = 0.2


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

        snapshot = self._select_snapshot(restic)
        if snapshot is None:
            return False

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

    def run_mount(self) -> bool:
        restic = self.repository_provider.get()
        if restic is None:
            return False

        snapshot = self._select_snapshot(restic)
        if snapshot is None:
            return False

        return self._mount_and_browse(restic, snapshot)

    def _select_snapshot(self, restic: ResticRepository) -> SnapshotInfo | None:
        snapshots = restic.snapshots()
        if not snapshots:
            print(self._text("maintenance.no_snapshots"))
            return None

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
            return None

        if index < 1 or index > len(newest_first):
            print(self._text("restore.snapshot_not_exists"))
            return None

        return newest_first[index - 1]

    def _ask_target(self, snapshot_id: str) -> Path:
        default = Path.home() / "lbm-restore" / snapshot_id
        value = input(self._text("restore.target_prompt", default=default)).strip()
        return Path(value).expanduser() if value else default

    def _mount_and_browse(self, restic: ResticRepository, snapshot: SnapshotInfo) -> bool:
        mountpoint = Path(tempfile.mkdtemp(prefix="lbm-restore-"))
        process: subprocess.Popen[str] | None = None
        try:
            process = restic.start_mount(mountpoint)
            snapshot_path = self._wait_for_mount(mountpoint, snapshot.snapshot_id, process)
            if snapshot_path is None:
                return False

            print()
            print(self._text("restore.mount_ready", path=str(snapshot_path)))
            if not open_in_file_manager(snapshot_path):
                print(self._text("restore.mount_no_file_manager"))

            input(self._text("restore.mount_prompt"))
            return True
        finally:
            self._unmount(mountpoint, process)

    def _wait_for_mount(
        self,
        mountpoint: Path,
        snapshot_id: str,
        process: subprocess.Popen[str],
    ) -> Path | None:
        snapshot_path = mountpoint / "ids" / snapshot_id
        deadline = time.monotonic() + _MOUNT_READY_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            if snapshot_path.is_dir():
                return snapshot_path
            if process.poll() is not None:
                stderr = process.stderr.read() if process.stderr else ""
                print(self._text("restore.mount_failed", error=stderr.strip()))
                return None
            time.sleep(_MOUNT_POLL_INTERVAL_SECONDS)

        print(self._text("restore.mount_timeout"))
        return None

    def _unmount(self, mountpoint: Path, process: subprocess.Popen[str] | None) -> None:
        if process is not None and process.poll() is None:
            unmount(mountpoint)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.terminate()
        try:
            mountpoint.rmdir()
        except OSError:
            pass

    def _text(self, key: str, **values: object) -> str:
        return self.language.translate(key, **values)
