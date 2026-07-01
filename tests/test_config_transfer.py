from pathlib import Path
from unittest.mock import patch

import yaml

from lbm.services.config_transfer import ConfigExportService, ConfigImportService


def _write_minimal_config(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump({
            "system": {"host_name": "test", "language": "de"},
            "paths": {"log_dir": "logs", "state_dir": "state", "password_file": "~/.lbm/pw"},
            "backup": {"paths": ["/home/test"], "excludes": []},
            "targets": {
                "usb": {"enabled": True, "label": "TestUSB", "repository_path": "restic/default"},
                "nas": {
                    "enabled": False, "mount_path": "/mnt/nas", "repository_path": "restic/nas"
                },
            },
            "retention": {
                "keep_daily": 14, "keep_weekly": 8, "keep_monthly": 12, "keep_yearly": 3
            },
            "schedule": {
                "enabled": True, "daily_time": "20:00", "interval_days": 1, "boot_delay_minutes": 5
            },
        }),
        encoding="utf-8",
    )


def test_export_writes_config_to_destination(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    _write_minimal_config(config_file)
    destination = tmp_path / "exported.yaml"

    service = ConfigExportService(config_file)
    with patch("builtins.input", return_value=str(destination)):
        result = service.run()

    assert result is True
    assert destination.is_file()
    assert destination.read_text(encoding="utf-8") == config_file.read_text(encoding="utf-8")


def test_export_asks_overwrite_when_destination_exists(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    _write_minimal_config(config_file)
    destination = tmp_path / "exported.yaml"
    destination.write_text("old content", encoding="utf-8")

    service = ConfigExportService(config_file)
    with patch("builtins.input", side_effect=[str(destination), "j"]):
        result = service.run()

    assert result is True
    assert destination.read_text(encoding="utf-8") != "old content"


def test_export_skips_when_overwrite_declined(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    _write_minimal_config(config_file)
    destination = tmp_path / "exported.yaml"
    destination.write_text("old content", encoding="utf-8")

    service = ConfigExportService(config_file)
    with patch("builtins.input", side_effect=[str(destination), "n"]):
        result = service.run()

    assert result is False
    assert destination.read_text(encoding="utf-8") == "old content"


def test_export_returns_false_when_no_source_config(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"

    service = ConfigExportService(config_file)
    result = service.run()

    assert result is False


def test_import_copies_and_validates_config(tmp_path: Path) -> None:
    source = tmp_path / "source.yaml"
    _write_minimal_config(source)
    config_file = tmp_path / "subdir" / "config.yaml"

    service = ConfigImportService(config_file)
    with patch("builtins.input", return_value=str(source)):
        result = service.run()

    assert result is True
    assert config_file.is_file()


def test_import_returns_false_when_source_not_found(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    source = tmp_path / "nonexistent.yaml"

    service = ConfigImportService(config_file)
    with patch("builtins.input", return_value=str(source)):
        result = service.run()

    assert result is False


def test_import_returns_false_on_invalid_config(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    source = tmp_path / "invalid.yaml"
    # Both targets disabled – fails the TargetsConfig model_validator
    source.write_text(
        yaml.safe_dump({
            "system": {"host_name": "test"},
            "paths": {"log_dir": "logs", "state_dir": "state", "password_file": "~/.lbm/pw"},
            "backup": {"paths": [], "excludes": []},
            "targets": {
                "usb": {"enabled": False, "label": "USB", "repository_path": "restic/default"},
                "nas": {"enabled": False},
            },
        }),
        encoding="utf-8",
    )

    service = ConfigImportService(config_file)
    with patch("builtins.input", return_value=str(source)):
        result = service.run()

    assert result is False


def test_import_creates_backup_of_existing_config(tmp_path: Path) -> None:
    source = tmp_path / "source.yaml"
    _write_minimal_config(source)
    config_file = tmp_path / "config.yaml"
    _write_minimal_config(config_file)

    service = ConfigImportService(config_file)
    with patch("builtins.input", return_value=str(source)):
        result = service.run()

    assert result is True
    backup = Path(str(config_file) + ".bak")
    assert backup.is_file()
