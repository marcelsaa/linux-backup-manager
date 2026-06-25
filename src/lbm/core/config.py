from pathlib import Path
import os

PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_DIR / "backup.conf"

def load_config():
    config = {}

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Konfigurationsdatei fehlt: {CONFIG_FILE}")

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()

            value = os.path.expandvars(
                value.strip().strip('"').strip("'")
            )

            config[key] = value

    return config
