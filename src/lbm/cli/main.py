import argparse
import logging

import yaml
from pydantic import ValidationError

from lbm.core.application import Application
from lbm.log_config import setup_logging
from lbm.ui.console import Console


class CommandLineInterface:
    """Kommandozeilenschnittstelle für LBM."""

    def __init__(self) -> None:
        self.application = Application()

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

        args = parser.parse_args()

        if args.command == "status":
            self.application.status() 
        elif args.command == "health":
            self.application.health()
        elif args.command == "init":
            self.application.init_repository()
        elif args.command == "backup":
            self.application.backup()
        elif args.command == "snapshots":
            self.application.snapshots()
        elif args.command == "restore":
            self.application.restore()
        elif args.command == "stats":
            self.application.stats()
        elif args.command == "check":
            self.application.check()
        elif args.command == "forget":
            self.application.forget()
        elif args.command == "prune":
            self.application.prune()
        elif args.command == "setup":
            self.application.setup(
                interactive=not args.yes,
            )
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
    