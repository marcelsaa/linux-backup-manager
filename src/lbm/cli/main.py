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
            ],
            help="auszuführender Befehl"
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
def main() -> None:
    cli = CommandLineInterface()
    cli.run()
