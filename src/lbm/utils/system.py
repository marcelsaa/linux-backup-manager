import shutil
import subprocess
from pathlib import Path


def command_exists(command):
    return shutil.which(command) is not None

def command_version(command, args):
    if not command_exists(command):
        return "nicht installiert"

    try:
        result = subprocess.run(
            [command] + args,
            text=True,
            capture_output=True,
            timeout=10,
            check=False
        )
        output = result.stdout.strip() or result.stderr.strip()
        return output.splitlines()[0] if output else "Version unbekannt"
    except Exception as error:
        return f"Fehler: {error}"

def path_exists(path):
    return Path(path).expanduser().exists()
