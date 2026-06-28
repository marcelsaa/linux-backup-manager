from unittest.mock import Mock, patch

from lbm.cli.main import CommandLineInterface, main
from lbm.core.errors import ConfigurationError


def test_non_interactive_setup_is_forwarded_to_application() -> None:
    application = Mock()
    application.setup.return_value = True
    cli = CommandLineInterface()
    cli.application = application

    with patch("sys.argv", ["backup-manager", "setup", "--non-interactive"]):
        cli.run()

    application.setup.assert_called_once_with(interactive=False)


def test_main_returns_nonzero_for_an_application_error() -> None:
    with (
        patch("lbm.cli.main.setup_logging"),
        patch(
            "lbm.cli.main.CommandLineInterface.run",
            side_effect=ConfigurationError("invalid config"),
        ),
    ):
        exit_code = main()

    assert exit_code == 1


def test_main_returns_nonzero_when_noninteractive_setup_is_incomplete() -> None:
    with (
        patch("lbm.cli.main.setup_logging"),
        patch("lbm.cli.main.CommandLineInterface.run", return_value=False),
    ):
        exit_code = main()

    assert exit_code == 1
