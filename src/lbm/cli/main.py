import argparse

from lbm.core.application import Application


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
    cli = CommandLineInterface()
    cli.run()
