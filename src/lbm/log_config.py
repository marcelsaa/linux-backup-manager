import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging() -> None:
    log_dir = Path.home() / ".local" / "state" / "lbm"
    log_dir.mkdir(parents=True, exist_ok=True)

    logfile = log_dir / "backup-manager.log"
    logfile.touch(exist_ok=True)
    logfile.chmod(0o640)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            RotatingFileHandler(
                logfile,
                maxBytes=1_000_000,
                backupCount=5,
                encoding="utf-8",
            ),
        ],
    )