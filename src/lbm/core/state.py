import json
from datetime import UTC, datetime, timedelta
from pathlib import Path


class BackupStateStore:
    def __init__(self, state_dir: Path) -> None:
        self.state_file = state_dir / "backup-state.json"

    @classmethod
    def from_config(cls, state_dir: str) -> "BackupStateStore":
        path = Path(state_dir).expanduser()
        if not path.is_absolute():
            path = Path.home() / ".local" / "state" / "linux-backup-manager"
        return cls(path)

    def record_success(self, completed_at: datetime | None = None) -> None:
        completed_at = completed_at or datetime.now(UTC)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.state_file.with_suffix(".tmp")
        temporary.write_text(
            json.dumps({"last_successful_backup": completed_at.isoformat()}) + "\n",
            encoding="utf-8",
        )
        temporary.chmod(0o600)
        temporary.replace(self.state_file)

    def last_successful_backup(self) -> datetime | None:
        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            value = datetime.fromisoformat(data["last_successful_backup"])
        except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            return None
        return value if value.tzinfo else value.replace(tzinfo=UTC)

    def is_due(self, max_age_hours: int, now: datetime | None = None) -> bool:
        last_backup = self.last_successful_backup()
        if last_backup is None:
            return True
        now = now or datetime.now(UTC)
        return now - last_backup >= timedelta(hours=max_age_hours)

    def is_scheduled_due(self, interval_days: int, now: datetime | None = None) -> bool:
        last_backup = self.last_successful_backup()
        if last_backup is None:
            return True
        now = now or datetime.now(UTC)
        local_now = now.astimezone()
        local_last = last_backup.astimezone()
        return (local_now.date() - local_last.date()).days >= interval_days
