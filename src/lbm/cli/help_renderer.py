import argparse

from lbm.services.language import LanguageService
from lbm.ui.console import Console

COMMANDS: tuple[str, ...] = (
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
    "change-password",
    "settings",
    "export-config",
    "import-config",
)

OPTIONS: tuple[tuple[str, str], ...] = (
    ("-h, --help", "cli.options.help"),
    ("--non-interactive", "cli.non_interactive_help"),
    ("--version", "cli.options.version"),
)


def print_help(parser: argparse.ArgumentParser) -> None:
    print(parser.format_usage())
    _print_language_block("de", Console.CYAN)
    print()
    _print_language_block("en", Console.MAGENTA)


def _print_language_block(language: str, color: str) -> None:
    service = LanguageService(language)
    heading = service.translate(f"cli.help.heading_{language}")
    width = max(len(name) for name in COMMANDS) + 2

    lines = [heading, ""]
    for command in COMMANDS:
        description = service.translate(f"cli.commands.{command}.description")
        lines.append(f"  {command:<{width}}{description}")

    option_width = max(len(flag) for flag, _ in OPTIONS) + 2
    lines.append("")
    for flag, key in OPTIONS:
        lines.append(f"  {flag:<{option_width}}{service.translate(key)}")

    print(f"{color}" + "\n".join(lines) + f"{Console.RESET}")
