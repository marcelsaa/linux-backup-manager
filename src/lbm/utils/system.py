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

def unmount(path: Path) -> bool:
    command = "fusermount" if command_exists("fusermount") else "umount"
    args = [command, "-u", str(path)] if command == "fusermount" else [command, str(path)]
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=10, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0

def open_in_file_manager(path: Path) -> bool:
    if not command_exists("xdg-open"):
        return False
    try:
        subprocess.Popen(
            ["xdg-open", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return False
    return True
