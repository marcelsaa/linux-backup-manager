import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ResticRepositoryInfo:
    initialized: bool
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