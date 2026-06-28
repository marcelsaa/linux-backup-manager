import subprocess
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, patch

from lbm.backup.restic import ResticRepositoryInfo
from lbm.core.config import ConfigLoader
from lbm.core.state import BackupStateStore
from lbm.health.checks import HealthResult
from lbm.services.doctor import DoctorService
from lbm.targets.usb import USBTargetInfo


def write_config(tmp_path: Path, password_file: Path) -> Path:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        f"""
system:
  host_name: test-host
paths:
  log_dir: logs
  state_dir: {tmp_path / 'state'}
  password_file: {password_file}
targets:
  usb:
    enabled: true
    label: LinuxBackup
    repository_path: restic/test-host
backup:
  paths:
    - /home/test/Documents
  excludes: []
retention:
  keep_daily: 14
  keep_weekly: 8
  keep_monthly: 12
  keep_yearly: 3
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return config_file


def available_usb(tmp_path: Path) -> USBTargetInfo:
    return USBTargetInfo(
        found=True,
        label="LinuxBackup",
        mountpoint=tmp_path / "usb",
        fsavail="100G",
        fsuse_percent="10%",
        writable=True,
    )


def test_doctor_reports_a_complete_healthy_environment(
    tmp_path: Path,
    capsys,
) -> None:
    password_file = tmp_path / "restic.pass"
    password_file.write_text("secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    config_file = write_config(tmp_path, password_file)
    (tmp_path / "usb").mkdir()
    BackupStateStore(tmp_path / "state").record_success(
        datetime(2026, 6, 28, 18, 30, tzinfo=UTC)
    )

    with (
        patch(
            "lbm.services.doctor.HealthChecker.check_restic",
            return_value=HealthResult("Restic", True, "restic 0.17.3"),
        ),
        patch("lbm.services.doctor.USBTarget.probe", return_value=available_usb(tmp_path)),
        patch(
            "lbm.services.doctor.ResticRepository.check",
            return_value=ResticRepositoryInfo(True, "Repository vorhanden"),
        ),
    ):
        successful = DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert successful is True
    assert "Konfiguration" in output and "OK" in output
    assert "Rechte 0600" in output
    assert "USB: LinuxBackup" in output
    assert "Repository USB: LinuxBackup" in output
    assert "28.06.2026" in output
    assert "Gesamtstatus............... OK" in output
    assert "keine Reparaturen" in output


def test_doctor_reports_invalid_config_and_skips_dependent_checks(
    tmp_path: Path,
    capsys,
) -> None:
    config_file = tmp_path / "invalid.yaml"
    config_file.write_text("invalid: [", encoding="utf-8")

    with patch(
        "lbm.services.doctor.HealthChecker.check_restic",
        return_value=HealthResult("Restic", True, "restic 0.17.3"),
    ):
        successful = DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert successful is False
    assert "Konfiguration" in output and "FEHLER" in output
    assert "Passwortdatei" in output and "ÜBERSPRUNGEN" in output
    assert "Gesamtstatus............... FEHLER" in output


def test_doctor_rejects_overly_permissive_password_file(
    tmp_path: Path,
    capsys,
) -> None:
    password_file = tmp_path / "restic.pass"
    password_file.write_text("secret\n", encoding="utf-8")
    password_file.chmod(0o644)
    config_file = write_config(tmp_path, password_file)

    with (
        patch(
            "lbm.services.doctor.HealthChecker.check_restic",
            return_value=HealthResult("Restic", False, "fehlt"),
        ),
        patch(
            "lbm.services.doctor.USBTarget.probe",
            return_value=available_usb(tmp_path),
        ),
    ):
        successful = DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert successful is False
    assert "Rechte 0644" in output
    assert "Restic nicht verfügbar" in output


def test_doctor_reports_an_unreachable_target_and_skips_repository(
    tmp_path: Path,
    capsys,
) -> None:
    password_file = tmp_path / "restic.pass"
    password_file.write_text("secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    config_file = write_config(tmp_path, password_file)

    with (
        patch(
            "lbm.services.doctor.HealthChecker.check_restic",
            return_value=HealthResult("Restic", True, "restic 0.17.3"),
        ),
        patch(
            "lbm.services.doctor.USBTarget.probe",
            return_value=USBTargetInfo(False, "LinuxBackup", None, None, None, False),
        ),
    ):
        successful = DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert successful is False
    assert "USB: LinuxBackup" in output and "nicht gefunden" in output
    assert "Repository USB: LinuxBackup" in output
    assert "Ziel nicht erreichbar" in output


def test_doctor_uses_only_read_only_repository_operation(tmp_path: Path) -> None:
    password_file = tmp_path / "restic.pass"
    password_file.write_text("secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    config_file = write_config(tmp_path, password_file)
    repository = Mock()
    repository.check.return_value = ResticRepositoryInfo(True, "Repository vorhanden")

    with (
        patch(
            "lbm.services.doctor.HealthChecker.check_restic",
            return_value=HealthResult("Restic", True, "restic 0.17.3"),
        ),
        patch("lbm.services.doctor.USBTarget.probe", return_value=available_usb(tmp_path)),
        patch("lbm.services.doctor.ResticRepository", return_value=repository),
    ):
        DoctorService(config_file).run()

    repository.check.assert_called_once_with(timeout_seconds=30)
    repository.init_repository.assert_not_called()
    repository.backup.assert_not_called()
    repository.forget.assert_not_called()
    repository.prune.assert_not_called()


def test_doctor_supports_a_nas_only_configuration(
    tmp_path: Path,
    capsys,
) -> None:
    password_file = tmp_path / "restic.pass"
    password_file.write_text("secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    config_file = write_config(tmp_path, password_file)
    config = ConfigLoader(config_file).load()
    config.targets.usb.enabled = False
    config.targets.nas.enabled = True
    config.targets.nas.mount_path = str(tmp_path / "nas")
    config.targets.nas.repository_path = "restic/test-host"
    (tmp_path / "nas").mkdir()

    with (
        patch("lbm.services.doctor.ConfigLoader.load", return_value=config),
        patch(
            "lbm.services.doctor.HealthChecker.check_restic",
            return_value=HealthResult("Restic", True, "restic 0.17.3"),
        ),
        patch(
            "lbm.services.doctor.ResticRepository.check",
            return_value=ResticRepositoryInfo(True, "Repository vorhanden"),
        ),
    ):
        successful = DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert successful is True
    assert f"NAS: {tmp_path / 'nas'}" in output
    assert "Repository NAS:" in output


def test_doctor_reports_a_repository_timeout(tmp_path: Path, capsys) -> None:
    password_file = tmp_path / "restic.pass"
    password_file.write_text("secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    config_file = write_config(tmp_path, password_file)

    with (
        patch(
            "lbm.services.doctor.HealthChecker.check_restic",
            return_value=HealthResult("Restic", True, "restic 0.17.3"),
        ),
        patch("lbm.services.doctor.USBTarget.probe", return_value=available_usb(tmp_path)),
        patch(
            "lbm.services.doctor.ResticRepository.check",
            side_effect=subprocess.TimeoutExpired("restic snapshots", 30),
        ),
    ):
        successful = DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert successful is False
    assert "Repository USB: LinuxBackup" in output
    assert "timed out after 30 seconds" in output
