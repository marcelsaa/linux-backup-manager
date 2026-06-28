import argparse
import logging

from lbm import __version__
from lbm.cli.error_handler import ErrorHandler
from lbm.core.application import Application
from lbm.core.errors import ApplicationError
from lbm.log_config import setup_logging
from lbm.ui.console import Console


class CommandLineInterface:
    """Kommandozeilenschnittstelle für LBM."""

    def __init__(self) -> None:
        self.application: Application | None = None

    def run(self) -> None:
        parser = argparse.ArgumentParser(
            prog="backup-manager",
            description="Linux Backup Manager"
        )

        parser.add_argument(
            "command",
            nargs="?",
            default="status",
            choices=[
                "status",
                "health",
                "init",
                "backup",
                "snapshots",
                "restore",
                "stats",
                "check",
                "forget",
                "prune",
                "setup",
            ],
            help="auszuführender Befehl",
        )

        parser.add_argument(
            "--yes",
            action="store_true",
            help="Alle Rückfragen automatisch bestätigen.",
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
            self.application.setup(
                interactive=not args.yes,
            )
            return

        command_methods = {
            "status": self.application.status,
            "health": self.application.health,
            "init": self.application.init_repository,
            "backup": self.application.backup,
            "snapshots": self.application.snapshots,
            "restore": self.application.restore,
            "stats": self.application.stats,
            "check": self.application.check,
            "forget": self.application.forget,
            "prune": self.application.prune,
        }
        command_methods[args.command]()


def main() -> None:
    setup_logging()
    logging.info("Linux Backup Manager gestartet.")

    try:
        cli = CommandLineInterface()
        cli.run()

    except ApplicationError as error:
        ErrorHandler.show(error)

    except KeyboardInterrupt:
        print()
        Console.warning("Vorgang durch Benutzer abgebrochen.")
