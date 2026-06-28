from datetime import UTC, datetime, timedelta
from pathlib import Path

from lbm.core.state import BackupStateStore


def test_backup_is_due_when_no_success_was_recorded(tmp_path: Path) -> None:
    state = BackupStateStore(tmp_path)

    assert state.is_due(24, datetime(2026, 6, 28, 20, tzinfo=UTC)) is True


def test_backup_becomes_due_after_24_hours(tmp_path: Path) -> None:
    state = BackupStateStore(tmp_path)
    completed = datetime(2026, 6, 27, 20, tzinfo=UTC)
    state.record_success(completed)

    assert state.is_due(24, completed + timedelta(hours=23)) is False
    assert state.is_due(24, completed + timedelta(hours=24)) is True
    assert state.last_successful_backup() == completed


def test_invalid_state_is_treated_as_due(tmp_path: Path) -> None:
    state = BackupStateStore(tmp_path)
    state.state_file.write_text("not-json", encoding="utf-8")

    assert state.is_due(24) is True


def test_scheduled_backup_uses_calendar_day_interval(tmp_path: Path) -> None:
    state = BackupStateStore(tmp_path)
    completed = datetime(2026, 6, 27, 20, 1, tzinfo=UTC)
    state.record_success(completed)

    assert state.is_scheduled_due(1, datetime(2026, 6, 28, 20, tzinfo=UTC)) is True
    assert state.is_scheduled_due(7, datetime(2026, 7, 3, 20, tzinfo=UTC)) is False
    assert state.is_scheduled_due(7, datetime(2026, 7, 4, 20, tzinfo=UTC)) is True
