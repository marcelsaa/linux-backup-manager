import argparse
import logging

import yaml
from pydantic import ValidationError

from lbm import __version__
from lbm.core.application import Application
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

    except FileNotFoundError:
        Console.error("Konfigurationsdatei nicht gefunden.")
        Console.info(
            "Bitte führen Sie zuerst 'backup-manager setup' aus."
        )

    except yaml.YAMLError:
        Console.error("Konfigurationsdatei ist ungültig.")
        Console.info(
            "Bitte prüfen Sie die YAML-Syntax in config/config.yaml."
        )

    except ValidationError as error:
        Console.error("Konfigurationsdatei ist unvollständig oder ungültig.")
        
        for err in error.errors():
            field = ".".join(str(x) for x in err["loc"])
            Console.info(f"{field}: {err['msg']}")

    except IsADirectoryError:
        Console.error("Konfigurationspfad ist ein Verzeichnis, keine Datei.")
        Console.info(
            "Erwartet wird die Datei config/config.yaml."
        )

    except PermissionError:
        Console.error("Konfigurationsdatei kann nicht gelesen werden.")
        Console.info(
            "Bitte prüfen Sie die Dateirechte von config/config.yaml."
        )
