from datetime import UTC, datetime, timedelta

from lbm.services.language import LanguageService
from lbm.services.status import format_backup_age


def test_format_backup_age_returns_none_without_a_backup() -> None:
    assert format_backup_age(None, LanguageService("de")) is None


def test_format_backup_age_reports_minutes_for_a_short_delta() -> None:
    last_backup = datetime.now(UTC) - timedelta(minutes=5)

    result = format_backup_age(last_backup, LanguageService("de"))

    assert result is not None
    assert "Minute" in result


def test_format_backup_age_reports_hours_for_a_medium_delta() -> None:
    last_backup = datetime.now(UTC) - timedelta(hours=3)

    result = format_backup_age(last_backup, LanguageService("de"))

    assert result is not None
    assert "Stunde" in result


def test_format_backup_age_reports_days_for_a_large_delta() -> None:
    last_backup = datetime.now(UTC) - timedelta(days=5)

    result = format_backup_age(last_backup, LanguageService("de"))

    assert result is not None
    assert "Tag" in result


def test_format_backup_age_is_localized_in_english() -> None:
    last_backup = datetime.now(UTC) - timedelta(hours=2)

    result = format_backup_age(last_backup, LanguageService("en"))

    assert result is not None
    assert "hour" in result
