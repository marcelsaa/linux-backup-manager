import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from lbm.core.errors import ExternalCommandError


class RepositoryStatus(Enum):
    READY = "ready"
    MISSING = "missing"
    WRONG_PASSWORD = "wrong_password"
    ERROR = "error"


@dataclass
class ResticRepositoryInfo:
    initialized: bool
    message: str
    status: RepositoryStatus = RepositoryStatus.ERROR

@dataclass
class BackupResult:
    ok: bool
    snapshot_id: str | None
    files_new: int
    files_changed: int
    files_unmodified: int
    processed_files: int
    processed_size: str
    duration: str
    message: str

@dataclass
class SnapshotInfo:
    snapshot_id: str
    time: str
    host: str
    paths: list[str]

@dataclass
class RepositoryStats:
    snapshot_count: int
    first_snapshot: str
    last_snapshot: str
    host: str

class ResticRepository:
    def __init__(
        self,
        repository: Path,
        password_file: Path,
    ) -> None:
        self.repository = repository
        self.password_file = password_file.expanduser()

    def _run(
        self,
        command: list[str],
        timeout_seconds: float | None = None,
    ) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                command,
                env={
                    **os.environ,
                    "RESTIC_REPOSITORY": str(self.repository),
                    "RESTIC_PASSWORD_FILE": str(self.password_file),
                },
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
        except FileNotFoundError as error:
            raise ExternalCommandError(
                "Restic konnte nicht gestartet werden.",
                hint="Bitte installieren Sie Restic und prüfen Sie den PATH.",
            ) from error

    def check(self, timeout_seconds: float | None = None) -> ResticRepositoryInfo:
        result = self._run(["restic", "snapshots"], timeout_seconds)

        if result.returncode == 0:
            return ResticRepositoryInfo(
                True,
                "Repository vorhanden",
                RepositoryStatus.READY,
            )

        message = result.stderr.strip()
        normalized_message = message.lower()
        if "wrong password" in normalized_message or "no key found" in normalized_message:
            status = RepositoryStatus.WRONG_PASSWORD
        elif "permission denied" in normalized_message:
            status = RepositoryStatus.ERROR
        elif not (self.repository / "config").is_file():
            status = RepositoryStatus.MISSING
        else:
            status = RepositoryStatus.ERROR

        return ResticRepositoryInfo(
            False,
            message,
            status,
        )
    
    def _parse_backup_json(self, output: str) -> BackupResult:
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if data.get("message_type") != "summary":
                continue
            return BackupResult(
                ok=True,
                snapshot_id=data.get("snapshot_id"),
                files_new=int(data.get("files_new", 0)),
                files_changed=int(data.get("files_changed", 0)),
                files_unmodified=int(data.get("files_unmodified", 0)),
                processed_files=int(data.get("total_files_processed", 0)),
                processed_size=self._format_bytes(int(data.get("total_bytes_processed", 0))),
                duration=self._format_duration(float(data.get("total_duration", 0))),
                message=output.strip(),
            )
        return BackupResult(
            ok=True,
            snapshot_id=None,
            files_new=0,
            files_changed=0,
            files_unmodified=0,
            processed_files=0,
            processed_size="",
            duration="",
            message=output.strip(),
        )

    @staticmethod
    def _format_bytes(n: int) -> str:
        if n < 1024:
            return f"{n} B"
        if n < 1024 ** 2:
            return f"{n / 1024:.3f} KiB"
        if n < 1024 ** 3:
            return f"{n / 1024 ** 2:.3f} MiB"
        return f"{n / 1024 ** 3:.3f} GiB"

    @staticmethod
    def _format_duration(seconds: float) -> str:
        total = int(seconds)
        return f"{total // 60}:{total % 60:02d}"

    def init_repository(self) -> ResticRepositoryInfo:
        result = self._run(["restic", "init"])

        if result.returncode == 0:
            return ResticRepositoryInfo(
                True,
                "Repository erfolgreich erstellt",
                RepositoryStatus.READY,
            )

        return ResticRepositoryInfo(
            False,
            result.stderr.strip(),
            RepositoryStatus.ERROR,
        )
    
    def backup(self, paths: list[Path], excludes: list[str]) -> BackupResult:
        command = ["restic", "backup", "--json"]

        for exclude in excludes:
            command.extend(["--exclude", exclude])

        command.extend(str(path) for path in paths)

        result = self._run(command)

        if result.returncode == 0:
            return self._parse_backup_json(result.stdout)

        return BackupResult(
            ok=False,
            snapshot_id=None,
            files_new=0,
            files_changed=0,
            files_unmodified=0,
            processed_files=0,
            processed_size="unbekannt",
            duration="unbekannt",
            message=result.stderr.strip(),
        )
    
    def snapshots(self) -> list[SnapshotInfo]:
        result = self._run(["restic", "snapshots", "--json"])

        if result.returncode != 0:
            return []

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            return []

        return [
            SnapshotInfo(
                snapshot_id=item.get("short_id", item.get("id", "")),
                time=self._format_timestamp(
                    item.get("time", "")
                ),
                host=item.get("hostname", ""),
                paths=item.get("paths", []),
            )
            for item in data
        ]
    
    def _format_timestamp(self, timestamp: str) -> str:
        try:
            return datetime.fromisoformat(timestamp).strftime(
                "%d.%m.%Y %H:%M:%S"
            )
        except ValueError:
            return timestamp
    
    def restore(
        self,
        snapshot_id: str,
        target: Path,
    ) -> BackupResult:

        result = self._run(
            [
                "restic",
                "restore",
                snapshot_id,
                "--target",
                str(target),
            ]
        )

        if result.returncode == 0:
            return BackupResult(
                ok=True,
                snapshot_id=snapshot_id,
                files_new=0,
                files_changed=0,
                files_unmodified=0,
                processed_files=0,
                processed_size="",
                duration="",
                message="Restore erfolgreich.",
            )

        return BackupResult(
            ok=False,
            snapshot_id=snapshot_id,
            files_new=0,
            files_changed=0,
            files_unmodified=0,
            processed_files=0,
            processed_size="",
            duration="",
            message=result.stderr.strip(),
        )

    def start_mount(self, mountpoint: Path) -> subprocess.Popen[str]:
        # restic mount blocks in the foreground until the caller unmounts it, so it must be
        # started with Popen rather than the blocking _run() used by every other command.
        try:
            return subprocess.Popen(
                ["restic", "mount", str(mountpoint)],
                env={
                    **os.environ,
                    "RESTIC_REPOSITORY": str(self.repository),
                    "RESTIC_PASSWORD_FILE": str(self.password_file),
                },
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except FileNotFoundError as error:
            raise ExternalCommandError(
                "Restic konnte nicht gestartet werden.",
                hint="Bitte installieren Sie Restic und prüfen Sie den PATH.",
            ) from error

    def stats(self) -> RepositoryStats:
        snapshots = self.snapshots()

        if not snapshots:
            return RepositoryStats(
                snapshot_count=0,
                first_snapshot="-",
                last_snapshot="-",
                host="-",
            )

        return RepositoryStats(
            snapshot_count=len(snapshots),
            first_snapshot=snapshots[0].time,
            last_snapshot=snapshots[-1].time,
            host=snapshots[-1].host,
        )
    
    def check_repository(self) -> ResticRepositoryInfo:
        result = self._run(["restic", "check"])

        if result.returncode == 0:
            return ResticRepositoryInfo(
                initialized=True,
                message="Repository-Prüfung erfolgreich.",
                status=RepositoryStatus.READY,
            )

        return ResticRepositoryInfo(
            initialized=False,
            message=result.stderr.strip(),
            status=RepositoryStatus.ERROR,
        )
    
    def forget_dry_run(
        self,
        keep_daily: int,
        keep_weekly: int,
        keep_monthly: int,
        keep_yearly: int,
    ) -> str:
        result = self._run(
            [
                "restic",
                "forget",
                "--keep-daily",
                str(keep_daily),
                "--keep-weekly",
                str(keep_weekly),
                "--keep-monthly",
                str(keep_monthly),
                "--keep-yearly",
                str(keep_yearly),
                "--dry-run",
            ]
        )

        if result.returncode != 0:
            return result.stderr.strip()

        return result.stdout.strip()
    
    def forget(
        self,
        keep_daily: int,
        keep_weekly: int,
        keep_monthly: int,
        keep_yearly: int,
    ) -> str:
        result = self._run(
            [
                "restic",
                "forget",
                "--keep-daily",
                str(keep_daily),
                "--keep-weekly",
                str(keep_weekly),
                "--keep-monthly",
                str(keep_monthly),
                "--keep-yearly",
                str(keep_yearly),
            ]
        )

        if result.returncode != 0:
            return result.stderr.strip()

        return result.stdout.strip()
    
    def prune(self) -> str:
        result = self._run(["restic", "prune"])

        if result.returncode != 0:
            return result.stderr.strip()

        return result.stdout.strip()

    def change_password(self, new_password_file: Path) -> bool:
        result = self._run(
            ["restic", "key", "passwd", "--new-password-file", str(new_password_file)]
        )
        return result.returncode == 0

    def cleanup(
        self,
        keep_daily: int,
        keep_weekly: int,
        keep_monthly: int,
        keep_yearly: int,
    ) -> bool:
        forget = self._run(
            [
                "restic",
                "forget",
                "--keep-daily", str(keep_daily),
                "--keep-weekly", str(keep_weekly),
                "--keep-monthly", str(keep_monthly),
                "--keep-yearly", str(keep_yearly),
            ]
        )
        if forget.returncode != 0:
            return False
        prune = self._run(["restic", "prune"])
        return prune.returncode == 0
