import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class ResticRepositoryInfo:
    initialized: bool
    message: str

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

    def check(self) -> ResticRepositoryInfo:
        result = subprocess.run(
            [
                "restic",
                "snapshots",
            ],
            env={
                **os.environ,
                "RESTIC_REPOSITORY": str(self.repository),
                "RESTIC_PASSWORD_FILE": str(self.password_file),
            },
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return ResticRepositoryInfo(
                True,
                "Repository vorhanden",
            )

        return ResticRepositoryInfo(
            False,
            result.stderr.strip(),
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
        result = subprocess.run(
            [
                "restic",
                "init",
            ],
            env={
                **os.environ,
                "RESTIC_REPOSITORY": str(self.repository),
                "RESTIC_PASSWORD_FILE": str(self.password_file),
            },
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return ResticRepositoryInfo(True, "Repository erfolgreich erstellt")

        return ResticRepositoryInfo(False, result.stderr.strip())
    
    def backup(self, paths: list[Path], excludes: list[str]) -> BackupResult:
        command = ["restic", "backup"]

        for exclude in excludes:
            command.extend(["--exclude", exclude])

        command.extend(str(path) for path in paths)

        result = subprocess.run(
            command,
            env={
                **os.environ,
                "RESTIC_REPOSITORY": str(self.repository),
                "RESTIC_PASSWORD_FILE": str(self.password_file),
            },
            capture_output=True,
            text=True,
        )

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
        result = subprocess.run(
            [
                "restic",
                "snapshots",
                "--json",
            ],
            env={
                **os.environ,
                "RESTIC_REPOSITORY": str(self.repository),
                "RESTIC_PASSWORD_FILE": str(self.password_file),
            },
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return []

        data = json.loads(result.stdout)

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
        return datetime.fromisoformat(timestamp).strftime(
            "%d.%m.%Y %H:%M:%S"
        )
    
    def restore(
        self,
        snapshot_id: str,
        target: Path,
    ) -> BackupResult:

        result = subprocess.run(
            [
                "restic",
                "restore",
                snapshot_id,
                "--target",
                str(target),
            ],
            env={
                **os.environ,
                "RESTIC_REPOSITORY": str(self.repository),
                "RESTIC_PASSWORD_FILE": str(self.password_file),
            },
            capture_output=True,
            text=True,
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
        result = subprocess.run(
            [
                "restic",
                "check",
            ],
            env={
                **os.environ,
                "RESTIC_REPOSITORY": str(self.repository),
                "RESTIC_PASSWORD_FILE": str(self.password_file),
            },
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return ResticRepositoryInfo(
                initialized=True,
                message="Repository-Prüfung erfolgreich.",
            )

        return ResticRepositoryInfo(
            initialized=False,
            message=result.stderr.strip(),
        )
    
    def forget_dry_run(
        self,
        keep_daily: int,
        keep_weekly: int,
        keep_monthly: int,
        keep_yearly: int,
    ) -> str:
        result = subprocess.run(
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
            ],
            env={
                **os.environ,
                "RESTIC_REPOSITORY": str(self.repository),
                "RESTIC_PASSWORD_FILE": str(self.password_file),
            },
            capture_output=True,
            text=True,
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
        result = subprocess.run(
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
            ],
            env={
                **os.environ,
                "RESTIC_REPOSITORY": str(self.repository),
                "RESTIC_PASSWORD_FILE": str(self.password_file),
            },
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return result.stderr.strip()

        return result.stdout.strip()
    
    def prune(self) -> str:
        result = subprocess.run(
            [
                "restic",
                "prune",
            ],
            env={
                **os.environ,
                "RESTIC_REPOSITORY": str(self.repository),
                "RESTIC_PASSWORD_FILE": str(self.password_file),
            },
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return result.stderr.strip()

        return result.stdout.strip()    