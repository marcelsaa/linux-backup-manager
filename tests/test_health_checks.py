from pathlib import Path
from unittest.mock import Mock, patch

from lbm.backup.restic import ResticRepositoryInfo
from lbm.core.config import AppConfig
from lbm.health.checks import HealthChecker
from lbm.services.health import HealthService


def test_check_command_reports_a_nonzero_exit_code_as_failure() -> None:
    process = Mock(returncode=1, stdout="", stderr="command failed")
    checker = HealthChecker.__new__(HealthChecker)

    with (
        patch("lbm.health.checks.shutil.which", return_value="/usr/bin/tool"),
        patch("lbm.health.checks.subprocess.run", return_value=process),
    ):
        result = checker.check_command("Tool", "tool", ["--version"])

    assert result.ok is False
    assert result.message == "command failed"


def test_health_service_supports_a_nas_only_configuration(
    tmp_path: Path,
    capsys,
) -> None:
    password_file = tmp_path / "password"
    password_file.write_text("secret", encoding="utf-8")
    config = AppConfig.model_validate(
        {
            "system": {"host_name": "test"},
            "paths": {
                "log_dir": "logs",
                "state_dir": "state",
                "password_file": str(password_file),
            },
            "backup": {"paths": [str(tmp_path)], "excludes": []},
            "targets": {
                "usb": {
                    "enabled": False,
                    "label": "unused",
                    "repository_path": "unused",
                },
                "nas": {
                    "enabled": True,
                    "mount_path": str(tmp_path),
                    "repository_path": "repository",
                },
            },
            "retention": {
                "keep_daily": 7,
                "keep_weekly": 4,
                "keep_monthly": 3,
                "keep_yearly": 1,
            },
        }
    )

    with (
        patch("lbm.services.health.HealthChecker.run", return_value=[]),
        patch(
            "lbm.backup.restic.ResticRepository.check",
            return_value=ResticRepositoryInfo(True, "Repository vorhanden"),
        ),
    ):
        HealthService(config).run()

    output = capsys.readouterr().out
    assert f"NAS: {tmp_path}" in output
    assert "Gesamtstatus........ OK" in output
