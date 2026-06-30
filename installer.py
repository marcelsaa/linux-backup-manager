#!/usr/bin/env python3
"""Safe fresh-install and 1.0.1 upgrade orchestrator for Linux Backup Manager."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from email.parser import Parser
from enum import Enum
from pathlib import Path
from zipfile import ZipFile


class InstallerError(RuntimeError):
    pass


class InstallMode(Enum):
    FRESH = "fresh"
    UPGRADE = "upgrade"
    CURRENT = "current"
    PARTIAL = "partial"


@dataclass(frozen=True)
class Artifact:
    path: Path
    version: str
    sha256: str


@dataclass(frozen=True)
class Layout:
    home: Path

    @property
    def data_root(self) -> Path:
        return self.home / ".local/share/linux-backup-manager"

    @property
    def legacy_venv(self) -> Path:
        return self.data_root / "venv"

    @property
    def versions(self) -> Path:
        return self.data_root / "versions"

    @property
    def launcher(self) -> Path:
        return self.home / ".local/bin/backup-manager"

    @property
    def config(self) -> Path:
        return self.home / ".config/linux-backup-manager/config.yaml"

    @property
    def password(self) -> Path:
        return self.home / ".config/linux-backup-manager/restic.pass"

    @property
    def unit_dir(self) -> Path:
        return self.home / ".config/systemd/user"

    @property
    def backup_root(self) -> Path:
        return self.data_root / "upgrade-backups"


Run = Callable[..., subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class TimerState:
    name: str
    enabled: bool
    active: bool


class Installer:
    TIMER_NAMES = (
        "linux-backup-manager-daily.timer",
        "linux-backup-manager-due.timer",
    )
    UNIT_NAMES = (
        "linux-backup-manager-daily.service",
        "linux-backup-manager-daily.timer",
        "linux-backup-manager-due.service",
        "linux-backup-manager-due.timer",
    )

    def __init__(
        self,
        layout: Layout,
        artifact: Artifact,
        python: Path,
        runner: Run = subprocess.run,
        min_free_bytes: int = 250 * 1024 * 1024,
    ) -> None:
        self.layout = layout
        self.artifact = artifact
        self.python = python
        self.runner = runner
        self.min_free_bytes = min_free_bytes

    def detect(self) -> tuple[InstallMode, str | None, Path | None]:
        python = self._installed_python()
        signals = (
            self.layout.launcher.exists()
            or self.layout.launcher.is_symlink()
            or self.layout.config.exists()
            or any((self.layout.unit_dir / name).exists() for name in self.UNIT_NAMES)
        )
        if python is None:
            return (InstallMode.PARTIAL if signals else InstallMode.FRESH, None, None)

        version = self._installed_version(python)
        if version is None:
            return InstallMode.PARTIAL, None, python
        if version == self.artifact.version:
            return InstallMode.CURRENT, version, python
        if version == "1.0.1" and self.layout.config.is_file():
            return InstallMode.UPGRADE, version, python
        return InstallMode.PARTIAL, version, python

    def execute(self, *, dry_run: bool, assume_yes: bool) -> InstallMode:
        mode, version, old_python = self.detect()
        print(f"Detected mode: {mode.value}")
        if version:
            print(f"Installed version: {version}")
        print(f"Candidate version: {self.artifact.version}")

        if mode is InstallMode.PARTIAL:
            raise InstallerError(
                "Installation state is incomplete or unsupported; no changes were made."
            )
        if mode is InstallMode.CURRENT:
            print("The requested version is already installed; no changes are required.")
            return mode
        assert mode in (InstallMode.FRESH, InstallMode.UPGRADE)
        self._preflight(old_python if mode is InstallMode.UPGRADE else None)
        if dry_run:
            print("Dry run complete; no changes were made.")
            return mode
        if not assume_yes:
            answer = input(f"Proceed with {mode.value}? [y/j/N]: ").strip().lower()
            if answer not in {"y", "yes", "j", "ja"}:
                raise InstallerError("Installation cancelled; no changes were made.")

        if mode is InstallMode.FRESH:
            self._fresh_install()
        else:
            assert old_python is not None
            self._upgrade(old_python)
        return mode

    def _installed_python(self) -> Path | None:
        if self.layout.launcher.is_symlink():
            target = self.layout.launcher.resolve(strict=False)
            candidate = target.parent / "python"
            if candidate.is_file():
                return candidate
        legacy = self.layout.legacy_venv / "bin/python"
        if legacy.is_file():
            return legacy
        return None

    def _installed_version(self, python: Path) -> str | None:
        result = self.runner(
            [
                str(python),
                "-c",
                "from importlib.metadata import version; print(version('linux-backup-manager'))",
            ],
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "HOME": str(self.layout.home)},
            timeout=30,
        )
        return result.stdout.strip() if result.returncode == 0 else None

    def _fresh_install(self) -> None:
        target = self._prepare_version()
        try:
            self._switch_launcher(target / "bin/backup-manager")
        except Exception:
            self._remove_target(target)
            raise
        print("Fresh installation completed. Run 'backup-manager setup' next.")

    def _upgrade(self, old_python: Path) -> None:
        timer_state = self._timer_state()
        files_before = self._operational_fingerprints()
        repository_before = self._repository_signature(old_python)
        had_units = any((self.layout.unit_dir / name).exists() for name in self.UNIT_NAMES)
        existing_timer_names = tuple(
            name for name in self.TIMER_NAMES if (self.layout.unit_dir / name).exists()
        )
        manage_timers = had_units or any(item.enabled or item.active for item in timer_state)
        target = self._prepare_version()
        new_command = target / "bin/backup-manager"
        backup: Path | None = None
        cutover_started = False
        try:
            backup = self._backup_operational_files()
            self._run_checked(
                [
                    str(target / "bin/python"),
                    "-c",
                    (
                        "from pathlib import Path; "
                        "from lbm.services.doctor import DoctorService; "
                        "raise SystemExit(0 if DoctorService("
                        "Path('~/.config/linux-backup-manager/config.yaml').expanduser()"
                        ").run() else 1)"
                    ),
                ],
                env={**os.environ, "HOME": str(self.layout.home)},
            )
            cutover_started = True
            if manage_timers:
                self._stop_timers()
            self._switch_launcher(new_command)
            if manage_timers:
                self._run_checked(
                    [str(new_command), "schedule-install"],
                    env={**os.environ, "HOME": str(self.layout.home)},
                )
                self._apply_timer_state(timer_state)
        except Exception as upgrade_error:
            if cutover_started:
                assert backup is not None
                try:
                    self._rollback(
                        backup,
                        old_python,
                        timer_state,
                        files_before,
                        existing_timer_names,
                    )
                    self._verify_rollback(
                        files_before,
                        timer_state,
                        repository_before,
                        old_python,
                    )
                except Exception as rollback_error:
                    raise InstallerError(
                        "CRITICAL: upgrade failed and automatic rollback could not "
                        f"restore the exact operational state. Recovery data: {backup}\n"
                        f"Upgrade error: {upgrade_error}\nRollback error: {rollback_error}"
                    ) from rollback_error
            if backup is not None:
                self._remove_backup(backup)
            self._remove_target(target)
            raise
        assert backup is not None
        print(f"Upgrade completed. Rollback data: {backup}")

    def _prepare_version(self) -> Path:
        target = self.layout.versions / self.artifact.version
        if target.exists():
            raise InstallerError(f"Target environment already exists: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        environment = {**os.environ, "HOME": str(self.layout.home)}
        try:
            self._run_checked([str(self.python), "-m", "venv", str(target)])
            python = target / "bin/python"
            self._run_checked(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "--no-input",
                    "--no-cache-dir",
                    str(self.artifact.path),
                ],
                env=environment,
            )
            self._run_checked([str(python), "-m", "pip", "check"], env=environment)
            result = self._run_checked(
                [
                    str(python),
                    "-c",
                    (
                        "from importlib.metadata import version; "
                        "print(version('linux-backup-manager'))"
                    ),
                ],
                env=environment,
            )
            if result.stdout.strip() != self.artifact.version:
                raise InstallerError("Installed command reports an unexpected version.")
        except Exception:
            self._remove_target(target)
            raise
        return target

    def _backup_operational_files(self) -> Path:
        timestamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
        target = self.layout.backup_root / timestamp
        try:
            target.mkdir(parents=True, mode=0o700)
            target.chmod(0o700)
            for source in (self.layout.config, self.layout.password):
                if source.exists():
                    shutil.copy2(source, target / source.name)
            units = target / "systemd-user"
            units.mkdir(mode=0o700)
            for name in self.UNIT_NAMES:
                source = self.layout.unit_dir / name
                if source.exists():
                    shutil.copy2(source, units / name)
            if self.layout.launcher.is_symlink():
                (target / "launcher-target.txt").write_text(
                    os.readlink(self.layout.launcher) + "\n", encoding="utf-8"
                )
            elif self.layout.launcher.exists():
                shutil.copy2(self.layout.launcher, target / "backup-manager")
        except Exception:
            self._remove_backup(target)
            raise
        return target

    def _timer_state(self) -> tuple[TimerState, ...]:
        states: list[TimerState] = []
        for name in self.TIMER_NAMES:
            enabled = (
                self.runner(
                    ["systemctl", "--user", "is-enabled", name],
                    capture_output=True,
                    text=True,
                    check=False,
                ).returncode
                == 0
            )
            active = self.runner(
                ["systemctl", "--user", "is-active", name],
                capture_output=True,
                text=True,
                check=False,
            ).returncode == 0
            states.append(TimerState(name, enabled, active))
        return tuple(states)

    def _stop_timers(self) -> None:
        self._run_checked(
            ["systemctl", "--user", "disable", "--now", *self.TIMER_NAMES]
        )

    def _switch_launcher(self, command: Path) -> None:
        self.layout.launcher.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.layout.launcher.with_name(".backup-manager.tmp")
        temporary.unlink(missing_ok=True)
        temporary.symlink_to(command)
        temporary.replace(self.layout.launcher)

    def _rollback(
        self,
        backup: Path,
        old_python: Path,
        timer_state: tuple[TimerState, ...],
        files_before: dict[str, tuple[object, ...]],
        existing_timer_names: tuple[str, ...],
    ) -> None:
        del old_python
        for path in (self.layout.config, self.layout.password):
            before = files_before[str(path)]
            source = backup / path.name
            if before[0] == "file":
                shutil.copy2(source, path)
            else:
                path.unlink(missing_ok=True)

        units = backup / "systemd-user"
        self.layout.unit_dir.mkdir(parents=True, exist_ok=True)
        for name in self.UNIT_NAMES:
            destination = self.layout.unit_dir / name
            destination.unlink(missing_ok=True)
            source = units / name
            if source.exists():
                shutil.copy2(source, destination)

        launcher_before = files_before[str(self.layout.launcher)]
        self.layout.launcher.unlink(missing_ok=True)
        if launcher_before[0] == "symlink":
            self.layout.launcher.symlink_to(str(launcher_before[1]))
        elif launcher_before[0] == "file":
            shutil.copy2(backup / "backup-manager", self.layout.launcher)

        self._run_checked(["systemctl", "--user", "daemon-reload"])
        self._apply_timer_state(
            tuple(item for item in timer_state if item.name in existing_timer_names)
        )

    def _apply_timer_state(self, states: tuple[TimerState, ...]) -> None:
        for state in states:
            self._run_checked(
                [
                    "systemctl",
                    "--user",
                    "enable" if state.enabled else "disable",
                    state.name,
                ]
            )
            self._run_checked(
                [
                    "systemctl",
                    "--user",
                    "start" if state.active else "stop",
                    state.name,
                ]
            )

    def _preflight(self, old_python: Path | None) -> None:
        print("Running preflight checks...")
        if not self.layout.home.is_dir():
            raise InstallerError(f"Home directory does not exist: {self.layout.home}")
        version = self._run_checked(
            [
                str(self.python),
                "-c",
                "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')",
            ]
        ).stdout.strip()
        try:
            major, minor = (int(part) for part in version.split(".", maxsplit=1))
        except ValueError as error:
            raise InstallerError(f"Could not determine Python version: {version}") from error
        if (major, minor) < (3, 12):
            raise InstallerError(f"Python 3.12 or newer is required; found {version}.")

        self._run_checked(["restic", "version"])
        required_paths = [self.layout.data_root, self.layout.launcher.parent]
        if old_python is not None:
            required_paths.extend((self.layout.config.parent, self.layout.unit_dir))
        for path in required_paths:
            parent = self._nearest_existing_parent(path)
            if not parent.is_dir() or not os.access(parent, os.W_OK | os.X_OK):
                raise InstallerError(f"Target directory is not writable: {parent}")

        storage_parent = self._nearest_existing_parent(self.layout.data_root)
        free = shutil.disk_usage(storage_parent).free
        if free < self.min_free_bytes:
            required_mib = self.min_free_bytes // (1024 * 1024)
            free_mib = free // (1024 * 1024)
            raise InstallerError(
                f"Insufficient free space: {free_mib} MiB available, "
                f"{required_mib} MiB required."
            )
        if old_python is not None:
            self._repository_signature(old_python)
        print("Preflight checks passed.")

    @staticmethod
    def _nearest_existing_parent(path: Path) -> Path:
        candidate = path
        while not candidate.exists():
            if candidate == candidate.parent:
                break
            candidate = candidate.parent
        return candidate

    def _repository_signature(self, python: Path) -> str:
        script = """
import hashlib
import json
from pathlib import Path
from lbm.core.config import ConfigLoader
from lbm.services.repository import RepositoryProvider

config = ConfigLoader(Path('~/.config/linux-backup-manager/config.yaml').expanduser()).load()
destinations = RepositoryProvider(config).get_all()
expected = int(config.targets.usb.enabled) + int(config.targets.nas.enabled)
if len(destinations) != expected:
    raise SystemExit('not every configured repository target is reachable')
state = []
for destination in destinations:
    import os
    import subprocess
    result = subprocess.run(
        ['restic', 'snapshots', '--json'],
        env={
            **os.environ,
            'RESTIC_REPOSITORY': str(destination.repository.repository),
            'RESTIC_PASSWORD_FILE': str(destination.repository.password_file),
        },
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or 'repository is not reachable')
    snapshots = json.loads(result.stdout)
    state.append((str(destination.repository.repository), snapshots))
payload = json.dumps(state, sort_keys=True, separators=(',', ':')).encode()
print('LBM_REPOSITORIES=' + hashlib.sha256(payload).hexdigest())
"""
        result = self._run_checked(
            [str(python), "-c", script],
            env={**os.environ, "HOME": str(self.layout.home)},
        )
        marker = "LBM_REPOSITORIES="
        signatures = [
            line.removeprefix(marker)
            for line in result.stdout.splitlines()
            if line.startswith(marker)
        ]
        if len(signatures) != 1:
            raise InstallerError("Repository preflight returned no reliable state signature.")
        return signatures[0]

    def _operational_fingerprints(self) -> dict[str, tuple[object, ...]]:
        paths = [self.layout.config, self.layout.password, self.layout.launcher]
        paths.extend(self.layout.unit_dir / name for name in self.UNIT_NAMES)
        fingerprints: dict[str, tuple[object, ...]] = {}
        for path in paths:
            key = str(path)
            if path.is_symlink():
                fingerprints[key] = ("symlink", os.readlink(path))
            elif path.is_file():
                stat = path.stat()
                fingerprints[key] = (
                    "file",
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    stat.st_mode & 0o7777,
                    stat.st_uid,
                    stat.st_gid,
                )
            elif path.exists():
                fingerprints[key] = ("other",)
            else:
                fingerprints[key] = ("missing",)
        return fingerprints

    def _verify_rollback(
        self,
        files_before: dict[str, tuple[object, ...]],
        timers_before: tuple[TimerState, ...],
        repository_before: str,
        old_python: Path,
    ) -> None:
        if self._operational_fingerprints() != files_before:
            raise InstallerError("configuration, password, launcher or unit files differ")
        if self._timer_state() != timers_before:
            raise InstallerError("systemd timer state differs")
        if self._repository_signature(old_python) != repository_before:
            raise InstallerError("repository snapshot state differs")

    def _remove_backup(self, backup: Path) -> None:
        shutil.rmtree(backup, ignore_errors=True)
        try:
            self.layout.backup_root.rmdir()
        except OSError:
            pass

    def _remove_target(self, target: Path) -> None:
        shutil.rmtree(target, ignore_errors=True)
        try:
            self.layout.versions.rmdir()
        except OSError:
            pass
        try:
            self.layout.data_root.rmdir()
        except OSError:
            pass

    def _run_checked(
        self,
        command: list[str],
        *,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        try:
            result = self.runner(
                command,
                capture_output=True,
                text=True,
                check=False,
                env=env,
                timeout=60,
            )
        except subprocess.TimeoutExpired as error:
            raise InstallerError(f"Command timed out: {' '.join(command)}") from error
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or "unknown error"
            raise InstallerError(f"Command failed: {' '.join(command)}\n{message}")
        return result


def read_artifact(path: Path, expected_sha256: str) -> Artifact:
    if not path.is_file():
        raise InstallerError(f"Wheel not found: {path}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected_sha256.lower():
        raise InstallerError(f"Wheel SHA-256 mismatch: {digest}")
    try:
        with ZipFile(path) as wheel:
            metadata_name = next(
                name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")
            )
            metadata = Parser().parsestr(wheel.read(metadata_name).decode("utf-8"))
    except (OSError, StopIteration, UnicodeError) as error:
        raise InstallerError("Wheel metadata could not be read.") from error
    if metadata["Name"] != "linux-backup-manager" or not metadata["Version"]:
        raise InstallerError("Wheel is not a Linux Backup Manager artifact.")
    return Artifact(path.resolve(), metadata["Version"], digest)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        artifact = read_artifact(args.wheel, args.sha256)
        installer = Installer(Layout(args.home.expanduser()), artifact, args.python)
        installer.execute(dry_run=args.dry_run, assume_yes=args.yes)
    except (InstallerError, OSError, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    except EOFError:
        print("ERROR: Input ended; no further changes were made.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nERROR: Interrupted by user.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
