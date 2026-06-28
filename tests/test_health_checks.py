from unittest.mock import Mock, patch

from lbm.health.checks import HealthChecker


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
