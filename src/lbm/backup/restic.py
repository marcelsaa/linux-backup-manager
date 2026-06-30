import json
import os
import re
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
    
    def _parse_backup_output(self, output: str) -> BackupResult:
        snapshot_match = re.search(r"snapshot\s+([a-f0-9]+)\s+saved", output)
        files_match = re.search(
            r"Files:\s+(\d+)\s+new,\s+(\d+)\s+changed,\s+(\d+)\s+unmodified",
            output,
        )
        processed_match = re.search(
            r"processed\s+(\d+)\s+files,\s+(.+?)\s+in\s+(.+)",
            output,
        )

        return BackupResult(
            ok=True,
            snapshot_id=snapshot_match.group(1) if snapshot_match else None,
            files_new=int(files_match.group(1)) if files_match else 0,
            files_changed=int(files_match.group(2)) if files_match else 0,
            files_unmodified=int(files_match.group(3)) if files_match else 0,
            processed_files=int(processed_match.group(1)) if processed_match else 0,
            processed_size=processed_match.group(2) if processed_match else "unbekannt",
            duration=processed_match.group(3) if processed_match else "unbekannt",
            message=output.strip(),
        )

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
        command = ["restic", "backup"]

        for exclude in excludes:
            command.extend(["--exclude", exclude])

        command.extend(str(path) for path in paths)

        result = self._run(command)

        if result.returncode == 0:
            return self._parse_backup_output(result.stdout)

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
