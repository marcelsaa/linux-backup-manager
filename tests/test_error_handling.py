from pathlib import Path
from unittest.mock import patch

import pytest

from lbm.backup.restic import ResticRepository
from lbm.cli.error_handler import ErrorHandler
from lbm.core.config import ConfigLoader
from lbm.core.errors import ConfigurationError, ExternalCommandError


def test_missing_config_is_wrapped_as_configuration_error(tmp_path: Path) -> None:
    config_file = tmp_path / "missing.yaml"

    with pytest.raises(ConfigurationError) as raised:
        ConfigLoader(config_file).load()

    assert raised.value.message == "Konfigurationsdatei nicht gefunden."
    assert "backup-manager setup" in (raised.value.hint or "")


def test_invalid_yaml_is_wrapped_as_configuration_error(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text("system: [", encoding="utf-8")

    with pytest.raises(ConfigurationError) as raised:
        ConfigLoader(config_file).load()

    assert raised.value.message == "Konfigurationsdatei ist ungültig."


def test_validation_errors_contain_field_details(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text("system: {}\n", encoding="utf-8")

    with pytest.raises(ConfigurationError) as raised:
        ConfigLoader(config_file).load()

    assert raised.value.message == "Konfigurationsdatei ist unvollständig oder ungültig."
    assert any("system.host_name" in detail for detail in raised.value.details)


def test_missing_restic_is_not_reported_as_a_config_error() -> None:
    repository = ResticRepository(Path("/tmp/repo"), Path("/tmp/password"))

    with (
        patch("lbm.backup.restic.subprocess.run", side_effect=FileNotFoundError),
        pytest.raises(ExternalCommandError) as raised,
    ):
        repository.check()

    assert raised.value.message == "Restic konnte nicht gestartet werden."


def test_error_handler_renders_message_hint_and_details(capsys) -> None:
    error = ConfigurationError(
        "Konfiguration fehlerhaft.",
        hint="Datei prüfen.",
        details=["backup.paths: Field required"],
    )

    ErrorHandler.show(error)

    output = capsys.readouterr().out
    assert "Konfiguration fehlerhaft." in output
    assert "Datei prüfen." in output
    assert "backup.paths: Field required" in output
