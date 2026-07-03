from pathlib import Path

from lbm.services.language import LanguageService
from lbm.ui.console import Console

_TAIL_LINES = 40
_DEFAULT_LOG_FILE = Path.home() / ".local" / "state" / "lbm" / "backup-manager.log"


class LogViewerService:
    """Show the location and most recent entries of the application log file."""

    def __init__(self, language: LanguageService, log_file: Path | None = None) -> None:
        self.language = language
        self.log_file = log_file or _DEFAULT_LOG_FILE

    def run(self) -> None:
        Console.headline(self._text("logs.path", path=str(self.log_file)))
        lines = self._read_lines()
        if not lines:
            print(self._text("logs.empty"))
            return
        tail = lines[-_TAIL_LINES:]
        print(self._text("logs.tail_hint", count=len(tail)))
        print()
        for line in tail:
            print(line)

    def _read_lines(self) -> list[str]:
        try:
            return self.log_file.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return []

    def _text(self, key: str, **values: object) -> str:
        return self.language.translate(key, **values)
