import hashlib
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from installer import (
    Artifact,
    Installer,
    InstallerError,
    InstallMode,
    Layout,
    TimerState,
    read_artifact,
)


def completed(
    returncode: int = 0, stdout: str = "", stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], returncode, stdout, stderr)


def artifact(tmp_path: Path, version: str = "1.1.0rc3") -> Artifact:
    wheel = tmp_path / "candidate.whl"
    wheel.write_bytes(b"wheel")
    return Artifact(wheel, version, hashlib.sha256(b"wheel").hexdigest())


def create_wheel(tmp_path: Path, version: str = "1.1.0rc3") -> Path:
    wheel = tmp_path / "linux_backup_manager.whl"
    metadata = f"Name: linux-backup-manager\nVersion: {version}\n"
    with ZipFile(wheel, "w", ZIP_DEFLATED) as archive:
        archive.writestr(
            f"linux_backup_manager-{version}.dist-info/METADATA",
            metadata,
        )
    return wheel


def test_read_artifact_verifies_hash_and_metadata(tmp_path: Path) -> None:
    wheel = create_wheel(tmp_path)
    digest = hashlib.sha256(wheel.read_bytes()).hexdigest()

    result = read_artifact(wheel, digest)

    assert result.version == "1.1.0rc3"
    assert result.sha256 == digest


def test_read_artifact_rejects_wrong_hash(tmp_path: Path) -> None:
    wheel = create_wheel(tmp_path)

    with pytest.raises(InstallerError, match="mismatch"):
        read_artifact(wheel, "0" * 64)


def test_detects_fresh_installation(tmp_path: Path) -> None:
    installer = Installer(Layout(tmp_path), artifact(tmp_path), Path("python3"))

    assert installer.detect() == (InstallMode.FRESH, None, None)


def test_detects_supported_legacy_upgrade(tmp_path: Path) -> None:
    layout = Layout(tmp_path)
    python = layout.legacy_venv / "bin/python"
    python.parent.mkdir(parents=True)
    python.touch()
    layout.config.parent.mkdir(parents=True)
    layout.config.touch()
    runner = Mock(return_value=completed(stdout="1.0.1\n"))

    installer = Installer(layout, artifact(tmp_path), Path("python3"), runner)

    assert installer.detect() == (InstallMode.UPGRADE, "1.0.1", python)


def test_detects_current_version_from_versioned_launcher(tmp_path: Path) -> None:
    layout = Layout(tmp_path)
    command = layout.versions / "1.1.0rc3/bin/backup-manager"
    python = command.parent / "python"
    command.parent.mkdir(parents=True)
    command.touch()
    python.touch()
    layout.launcher.parent.mkdir(parents=True)
    layout.launcher.symlink_to(command)
    runner = Mock(return_value=completed(stdout="1.1.0rc3\n"))

    installer = Installer(layout, artifact(tmp_path), Path("python3"), runner)

    assert installer.detect() == (InstallMode.CURRENT, "1.1.0rc3", python)


def test_active_versioned_launcher_wins_over_preserved_legacy_venv(
    tmp_path: Path,
) -> None:
    layout = Layout(tmp_path)
    legacy_python = layout.legacy_venv / "bin/python"
    legacy_python.parent.mkdir(parents=True)
    legacy_python.touch()
    current_command = layout.versions / "1.1.0rc3/bin/backup-manager"
    current_python = current_command.parent / "python"
    current_command.parent.mkdir(parents=True)
    current_command.touch()
    current_python.touch()
    layout.launcher.parent.mkdir(parents=True)
    layout.launcher.symlink_to(current_command)

    def runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        version = "1.1.0rc3" if command[0] == str(current_python) else "1.0.1"
        return completed(stdout=f"{version}\n")

    installer = Installer(layout, artifact(tmp_path), Path("python3"), runner)

    assert installer.detect() == (InstallMode.CURRENT, "1.1.0rc3", current_python)


def test_partial_installation_is_refused(tmp_path: Path) -> None:
    layout = Layout(tmp_path)
    layout.config.parent.mkdir(parents=True)
    layout.config.touch()
    installer = Installer(
        layout,
        artifact(tmp_path),
        Path("python3"),
        runner=Mock(return_value=completed()),
    )

    with pytest.raises(InstallerError, match="incomplete"):
        installer.execute(dry_run=False, assume_yes=True)


def test_dry_run_does_not_create_files(tmp_path: Path) -> None:
    layout = Layout(tmp_path)
    installer = Installer(layout, artifact(tmp_path), Path("python3"))

    assert installer.execute(dry_run=True, assume_yes=True) is InstallMode.FRESH
    assert not layout.data_root.exists()


def test_backup_preserves_password_permissions(tmp_path: Path) -> None:
    layout = Layout(tmp_path)
    layout.password.parent.mkdir(parents=True)
    layout.password.write_text("secret\n", encoding="utf-8")
    layout.password.chmod(0o600)
    installer = Installer(layout, artifact(tmp_path), Path("python3"))

    backup = installer._backup_operational_files()

    assert (backup / "restic.pass").stat().st_mode & 0o777 == 0o600


def test_failed_cutover_restores_old_launcher(tmp_path: Path) -> None:
    layout = Layout(tmp_path)
    old_python = layout.legacy_venv / "bin/python"
    old_command = old_python.parent / "backup-manager"
    old_command.parent.mkdir(parents=True)
    old_python.touch()
    old_command.touch()
    layout.launcher.parent.mkdir(parents=True)
    layout.launcher.symlink_to(old_command)
    installer = Installer(
        layout,
        artifact(tmp_path),
        Path("python3"),
        runner=Mock(return_value=completed()),
    )
    files_before = installer._operational_fingerprints()
    backup = installer._backup_operational_files()
    new_command = layout.versions / "new/bin/backup-manager"
    new_command.parent.mkdir(parents=True)
    new_command.touch()
    installer._switch_launcher(new_command)

    installer._rollback(
        backup,
        old_python,
        timer_state=(),
        files_before=files_before,
        existing_timer_names=(),
    )

    assert layout.launcher.resolve() == old_command.resolve()


def test_failed_prepare_removes_partial_environment(tmp_path: Path) -> None:
    layout = Layout(tmp_path)

    def runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        if command[-2:] == ["pip", "check"]:
            return completed(returncode=1, stderr="broken dependency")
        if command[1:3] == ["-m", "venv"]:
            (Path(command[-1]) / "bin").mkdir(parents=True)
        return completed()

    installer = Installer(layout, artifact(tmp_path), Path("python3"), runner)

    with pytest.raises(InstallerError, match="broken dependency"):
        installer._prepare_version()

    assert not (layout.versions / "1.1.0rc3").exists()


def test_timer_state_records_enabled_and_active_individually(tmp_path: Path) -> None:
    def runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        enabled = command[2] == "is-enabled" and command[-1].endswith("daily.timer")
        active = command[2] == "is-active" and command[-1].endswith("due.timer")
        return completed(returncode=0 if enabled or active else 1)

    installer = Installer(Layout(tmp_path), artifact(tmp_path), Path("python3"), runner)

    assert installer._timer_state() == (
        TimerState("linux-backup-manager-daily.timer", enabled=True, active=False),
        TimerState("linux-backup-manager-due.timer", enabled=False, active=True),
    )


def test_preflight_rejects_old_python_before_other_checks(tmp_path: Path) -> None:
    runner = Mock(return_value=completed(stdout="3.11\n"))
    installer = Installer(Layout(tmp_path), artifact(tmp_path), Path("python3"), runner)

    with pytest.raises(InstallerError, match="3.12 or newer"):
        installer._preflight(None)

    assert runner.call_count == 1


def test_preflight_rejects_unavailable_restic(tmp_path: Path) -> None:
    def runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        if command[:2] == ["restic", "version"]:
            return completed(returncode=127, stderr="restic not found")
        return completed(stdout="3.12\n")

    installer = Installer(Layout(tmp_path), artifact(tmp_path), Path("python3"), runner)

    with pytest.raises(InstallerError, match="restic not found"):
        installer._preflight(None)


def test_preflight_rejects_insufficient_space(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    usage = SimpleNamespace(total=1, used=1, free=0)
    monkeypatch.setattr(shutil, "disk_usage", lambda path: usage)
    runner = Mock(side_effect=[completed(stdout="3.12\n"), completed()])
    installer = Installer(
        Layout(tmp_path), artifact(tmp_path), Path("python3"), runner, min_free_bytes=1
    )

    with pytest.raises(InstallerError, match="Insufficient free space"):
        installer._preflight(None)


def test_desktop_entry_created_when_user_confirms(tmp_path: Path) -> None:
    layout = Layout(tmp_path)
    installer = Installer(layout, artifact(tmp_path), Path("python3"))

    with patch("builtins.input", return_value="y"):
        installer._offer_desktop_entry(assume_yes=False)

    assert layout.desktop_entry.is_file()
    content = layout.desktop_entry.read_text()
    assert "Terminal=true" in content
    assert str(layout.launcher) in content
    assert layout.desktop_entry.stat().st_mode & 0o644 == 0o644


def test_desktop_entry_not_created_when_user_declines(tmp_path: Path) -> None:
    layout = Layout(tmp_path)
    installer = Installer(layout, artifact(tmp_path), Path("python3"))

    with patch("builtins.input", return_value="n"):
        installer._offer_desktop_entry(assume_yes=False)

    assert not layout.desktop_entry.exists()


def test_desktop_entry_created_with_assume_yes(tmp_path: Path) -> None:
    layout = Layout(tmp_path)
    installer = Installer(layout, artifact(tmp_path), Path("python3"))

    installer._offer_desktop_entry(assume_yes=True)

    assert layout.desktop_entry.is_file()


def test_desktop_icon_created_when_desktop_dir_exists(tmp_path: Path) -> None:
    layout = Layout(tmp_path)
    layout.desktop.mkdir(parents=True)
    installer = Installer(layout, artifact(tmp_path), Path("python3"))

    with patch("builtins.input", side_effect=["y", "y"]):
        installer._offer_desktop_entry(assume_yes=False)

    assert layout.desktop_icon.is_file()
    assert layout.desktop_icon.stat().st_mode & 0o111


def test_desktop_icon_skipped_when_desktop_dir_missing(tmp_path: Path) -> None:
    layout = Layout(tmp_path)
    installer = Installer(layout, artifact(tmp_path), Path("python3"))

    with patch("builtins.input", side_effect=["y", "y"]):
        installer._offer_desktop_entry(assume_yes=False)

    assert layout.desktop_entry.is_file()
    assert not layout.desktop_icon.exists()


def test_desktop_icon_not_created_with_assume_yes(tmp_path: Path) -> None:
    layout = Layout(tmp_path)
    layout.desktop.mkdir(parents=True)
    installer = Installer(layout, artifact(tmp_path), Path("python3"))

    installer._offer_desktop_entry(assume_yes=True)

    assert layout.desktop_entry.is_file()
    assert not layout.desktop_icon.exists()


def test_desktop_content_uses_launcher_path(tmp_path: Path) -> None:
    layout = Layout(tmp_path)
    installer = Installer(layout, artifact(tmp_path), Path("python3"))

    content = installer._desktop_content()

    assert f"Exec={layout.launcher}" in content
    assert "Terminal=true" in content
    assert "Type=Application" in content


def test_failed_upgrade_restores_exact_operational_state(tmp_path: Path) -> None:
    layout = Layout(tmp_path)
    old_python = layout.legacy_venv / "bin/python"
    old_command = old_python.parent / "backup-manager"
    old_command.parent.mkdir(parents=True)
    old_python.touch()
    old_command.touch()
    layout.config.parent.mkdir(parents=True)
    layout.config.write_text("original config\n", encoding="utf-8")
    layout.password.write_text("original password\n", encoding="utf-8")
    layout.password.chmod(0o600)
    layout.unit_dir.mkdir(parents=True)
    for name in Installer.UNIT_NAMES:
        (layout.unit_dir / name).write_text(f"old {name}\n", encoding="utf-8")
    layout.launcher.parent.mkdir(parents=True)
    layout.launcher.symlink_to(old_command)
    original_timers = (
        TimerState(Installer.TIMER_NAMES[0], enabled=True, active=True),
        TimerState(Installer.TIMER_NAMES[1], enabled=False, active=False),
    )

    class FailureInstaller(Installer):
        current_timers = original_timers

        def _timer_state(self) -> tuple[TimerState, ...]:
            return self.current_timers

        def _repository_signature(self, python: Path) -> str:
            return "unchanged-repository"

        def _prepare_version(self) -> Path:
            target = self.layout.versions / self.artifact.version
            (target / "bin").mkdir(parents=True)
            (target / "bin/backup-manager").touch()
            return target

        def _stop_timers(self) -> None:
            self.current_timers = tuple(
                TimerState(item.name, enabled=False, active=False)
                for item in self.current_timers
            )

        def _apply_timer_state(self, states: tuple[TimerState, ...]) -> None:
            self.current_timers = states

        def _run_checked(
            self, command: list[str], *, env: dict[str, str] | None = None
        ) -> subprocess.CompletedProcess[str]:
            if command[-1] == "schedule-install":
                self.layout.config.write_text("damaged config\n", encoding="utf-8")
                self.layout.password.write_text("damaged password\n", encoding="utf-8")
                for name in self.UNIT_NAMES:
                    (self.layout.unit_dir / name).write_text("new unit\n", encoding="utf-8")
                raise InstallerError("injected cutover failure")
            return completed()

    installer = FailureInstaller(layout, artifact(tmp_path), Path("python3"))
    files_before = installer._operational_fingerprints()

    with pytest.raises(InstallerError, match="injected cutover failure"):
        installer._upgrade(old_python)

    assert installer._operational_fingerprints() == files_before
    assert installer._timer_state() == original_timers
    assert not layout.versions.exists()
    assert not layout.backup_root.exists()
