import os
import re
import subprocess
from dataclasses import dataclass
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