import argparse
import logging
import os
from pathlib import Path

from lbm import __version__
from lbm.cli.error_handler import ErrorHandler
from lbm.core.application import Application
from lbm.core.config import ConfigLoader
from lbm.core.errors import ApplicationError
from lbm.log_config import setup_logging
from lbm.services.language import LanguageService
from lbm.ui.console import Console


class CommandLineInterface:
    """Kommandozeilenschnittstelle für LBM."""

    def __init__(self) -> None:
        self.application: Application | None = None

    def run(self) -> bool:
        language = _configured_language()
        parser = argparse.ArgumentParser(
            prog="backup-manager",
            description=language.translate("cli.description"),
        )

        parser.add_argument(
            "command",
            nargs="?",
            default="status",
            choices=[
                "status",
                "health",
                "doctor",
                "recovery-info",
                "recovery-sheet",
                "init",
                "backup",
                "backup-if-due",
                "backup-scheduled",
                "snapshots",
                "restore",
                "stats",
                "check",
                "forget",
                "prune",
                "setup",
                "schedule-install",
                "schedule-status",
                "schedule-remove",
            ],
            help=language.translate("cli.command_help"),
        )

        parser.add_argument(
            "--non-interactive",
            action="store_true",
            help=language.translate("cli.non_interactive_help"),
        )

        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {__version__}",
        )

        args = parser.parse_args()

        if self.application is None:
            self.application = Application()

        if args.command == "setup":
            return self.application.setup(
                interactive=not args.non_interactive,
            )

        command_methods = {
            "status": self.application.status,
            "health": self.application.health,
            "doctor": self.application.doctor,
            "recovery-info": self.application.recovery_info,
            "recovery-sheet": self.application.recovery_sheet,
            "init": self.application.init_repository,
            "backup": self.application.backup,
            "backup-if-due": self.application.backup_if_due,
            "backup-scheduled": self.application.backup_scheduled,
            "snapshots": self.application.snapshots,
            "restore": self.application.restore,
            "stats": self.application.stats,
            "check": self.application.check,
            "forget": self.application.forget,
            "prune": self.application.prune,
            "schedule-install": self.application.schedule_install,
            "schedule-status": self.application.schedule_status,
            "schedule-remove": self.application.schedule_remove,
        }
        result = command_methods[args.command]()
        return result is not False


def main() -> int:
    setup_logging()
    logging.info("Linux Backup Manager gestartet.")

    try:
        cli = CommandLineInterface()
        return 0 if cli.run() else 1

    except ApplicationError as error:
        ErrorHandler.show(error)
        return 1

    except KeyboardInterrupt:
        print()
        Console.warning(_configured_language().translate("cli.interrupted"))
        return 130

    except EOFError:
        print()
        Console.warning(_configured_language().translate("cli.input_ended"))
        return 1


def _configured_language() -> LanguageService:
    configured_file = os.environ.get("LBM_CONFIG_FILE")
    config_file = (
        Path(configured_file).expanduser()
        if configured_file
        else Path("~/.config/linux-backup-manager/config.yaml").expanduser()
    )
    try:
        config = ConfigLoader(config_file).load()
    except ApplicationError:
        return LanguageService()
    return LanguageService(config.system.language)
