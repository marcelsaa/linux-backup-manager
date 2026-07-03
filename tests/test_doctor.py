import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from lbm.backup.restic import ResticRepositoryInfo
from lbm.core.config import ConfigLoader
from lbm.core.state import BackupStateStore
from lbm.health.checks import HealthResult
from lbm.services.doctor import DoctorService
from lbm.services.language import LanguageService
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
    assert "Gesamtstatus: OK" in output
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
    assert "Gesamtstatus: FEHLER" in output


def test_doctor_reports_incomplete_english_config_in_english(
    tmp_path: Path,
    capsys,
) -> None:
    config_file = tmp_path / "incomplete.yaml"
    config_file.write_text("system:\n  language: en\n", encoding="utf-8")

    with patch(
        "lbm.services.doctor.HealthChecker.check_restic",
        return_value=HealthResult("Restic", True, "restic 0.17.3"),
    ):
        successful = DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert successful is False
    assert "Configuration" in output and "ERROR" in output
    assert "Password file" in output and "SKIPPED" in output
    assert "Overall status: ERROR" in output
    # ConfigLoader's own error message stays hardcoded German (known technical debt)


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


def write_config_with_schedule(tmp_path: Path, password_file: Path) -> Path:
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
schedule:
  enabled: true
  daily_time: "20:00"
  interval_days: 1
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return config_file


def test_doctor_last_backup_shows_age(tmp_path: Path, capsys) -> None:
    password_file = tmp_path / "restic.pass"
    password_file.write_text("secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    config_file = write_config(tmp_path, password_file)
    (tmp_path / "usb").mkdir()
    BackupStateStore(tmp_path / "state").record_success(datetime(2026, 6, 30, 8, 0, tzinfo=UTC))

    with (
        patch(
            "lbm.services.doctor.HealthChecker.check_restic",
            return_value=HealthResult("Restic", True, "restic 0.17.3"),
        ),
        patch("lbm.services.doctor.USBTarget.probe", return_value=available_usb(tmp_path)),
        patch(
            "lbm.services.doctor.ResticRepository.check",
            return_value=ResticRepositoryInfo(True, "ok"),
        ),
    ):
        DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert "30.06.2026" in output
    assert "vor" in output


def test_doctor_last_backup_overdue_shows_warning(tmp_path: Path, capsys) -> None:
    password_file = tmp_path / "restic.pass"
    password_file.write_text("secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    config_file = write_config_with_schedule(tmp_path, password_file)
    (tmp_path / "usb").mkdir()
    BackupStateStore(tmp_path / "state").record_success(datetime(2026, 6, 27, 10, 0, tzinfo=UTC))

    with (
        patch(
            "lbm.services.doctor.HealthChecker.check_restic",
            return_value=HealthResult("Restic", True, "restic 0.17.3"),
        ),
        patch("lbm.services.doctor.USBTarget.probe", return_value=available_usb(tmp_path)),
        patch(
            "lbm.services.doctor.ResticRepository.check",
            return_value=ResticRepositoryInfo(True, "ok"),
        ),
        patch.object(DoctorService, "_systemctl_check", return_value=True),
    ):
        DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert "überfällig" in output
    assert "WARNUNG" in output


def test_doctor_timer_ok_when_enabled_and_active(tmp_path: Path, capsys) -> None:
    password_file = tmp_path / "restic.pass"
    password_file.write_text("secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    config_file = write_config_with_schedule(tmp_path, password_file)
    (tmp_path / "usb").mkdir()

    with (
        patch(
            "lbm.services.doctor.HealthChecker.check_restic",
            return_value=HealthResult("Restic", True, "restic 0.17.3"),
        ),
        patch("lbm.services.doctor.USBTarget.probe", return_value=available_usb(tmp_path)),
        patch(
            "lbm.services.doctor.ResticRepository.check",
            return_value=ResticRepositoryInfo(True, "ok"),
        ),
        patch.object(DoctorService, "_systemctl_check", return_value=True),
    ):
        DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert "aktiv und geplant" in output
    assert "Backup-Timer" in output


def test_doctor_timer_warning_when_not_installed(tmp_path: Path, capsys) -> None:
    password_file = tmp_path / "restic.pass"
    password_file.write_text("secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    config_file = write_config_with_schedule(tmp_path, password_file)
    (tmp_path / "usb").mkdir()

    with (
        patch(
            "lbm.services.doctor.HealthChecker.check_restic",
            return_value=HealthResult("Restic", True, "restic 0.17.3"),
        ),
        patch("lbm.services.doctor.USBTarget.probe", return_value=available_usb(tmp_path)),
        patch(
            "lbm.services.doctor.ResticRepository.check",
            return_value=ResticRepositoryInfo(True, "ok"),
        ),
        patch.object(DoctorService, "_systemctl_check", return_value=False),
    ):
        DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert "Timer nicht installiert" in output
    assert "WARNUNG" in output


def test_doctor_timer_skipped_when_schedule_disabled(tmp_path: Path, capsys) -> None:
    password_file = tmp_path / "restic.pass"
    password_file.write_text("secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    config_file = write_config(tmp_path, password_file)  # schedule.enabled=False by default
    (tmp_path / "usb").mkdir()

    with (
        patch(
            "lbm.services.doctor.HealthChecker.check_restic",
            return_value=HealthResult("Restic", True, "restic 0.17.3"),
        ),
        patch("lbm.services.doctor.USBTarget.probe", return_value=available_usb(tmp_path)),
        patch(
            "lbm.services.doctor.ResticRepository.check",
            return_value=ResticRepositoryInfo(True, "ok"),
        ),
    ):
        DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert "Backup-Timer" in output
    assert "nicht konfiguriert" in output
    assert "ÜBERSPRUNGEN" in output


def _make_doctor_with_language(lang: str = "de") -> DoctorService:
    service = DoctorService.__new__(DoctorService)
    service.language = LanguageService(lang)
    return service


def test_doctor_format_age_returns_minutes_for_short_delta() -> None:
    assert "Minute" in _make_doctor_with_language()._format_age(timedelta(seconds=90))


def test_doctor_format_age_returns_hours_for_medium_delta() -> None:
    assert "Stunde" in _make_doctor_with_language()._format_age(timedelta(hours=3))


def test_doctor_format_age_returns_days_for_large_delta() -> None:
    assert "Tag" in _make_doctor_with_language()._format_age(timedelta(days=5))


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


def test_doctor_output_has_section_headers(tmp_path: Path, capsys) -> None:
    password_file = tmp_path / "restic.pass"
    password_file.write_text("secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    config_file = write_config(tmp_path, password_file)
    (tmp_path / "usb").mkdir()

    with (
        patch(
            "lbm.services.doctor.HealthChecker.check_restic",
            return_value=HealthResult("Restic", True, "restic 0.17.3"),
        ),
        patch("lbm.services.doctor.USBTarget.probe", return_value=available_usb(tmp_path)),
        patch(
            "lbm.services.doctor.ResticRepository.check",
            return_value=ResticRepositoryInfo(True, "ok"),
        ),
    ):
        DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert "── Konfiguration" in output
    assert "── Programme" in output
    assert "── Sicherheit" in output
    assert "── Backup-Ziele" in output
    assert "── Repositories" in output
    assert "── Zeitplan" in output


def test_doctor_summary_line_shows_counts(tmp_path: Path, capsys) -> None:
    password_file = tmp_path / "restic.pass"
    password_file.write_text("secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    config_file = write_config(tmp_path, password_file)
    (tmp_path / "usb").mkdir()

    with (
        patch(
            "lbm.services.doctor.HealthChecker.check_restic",
            return_value=HealthResult("Restic", True, "restic 0.17.3"),
        ),
        patch("lbm.services.doctor.USBTarget.probe", return_value=available_usb(tmp_path)),
        patch(
            "lbm.services.doctor.ResticRepository.check",
            return_value=ResticRepositoryInfo(True, "ok"),
        ),
    ):
        DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert "OK ·" in output
    assert "Warnung(en)" in output
    assert "Fehler" in output
    assert "Übersprungen" in output


def test_doctor_overall_status_warning_when_backup_overdue(tmp_path: Path, capsys) -> None:
    password_file = tmp_path / "restic.pass"
    password_file.write_text("secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    config_file = write_config_with_schedule(tmp_path, password_file)
    (tmp_path / "usb").mkdir()
    BackupStateStore(tmp_path / "state").record_success(datetime(2026, 6, 1, 10, 0, tzinfo=UTC))

    with (
        patch(
            "lbm.services.doctor.HealthChecker.check_restic",
            return_value=HealthResult("Restic", True, "restic 0.17.3"),
        ),
        patch("lbm.services.doctor.USBTarget.probe", return_value=available_usb(tmp_path)),
        patch(
            "lbm.services.doctor.ResticRepository.check",
            return_value=ResticRepositoryInfo(True, "ok"),
        ),
        patch.object(DoctorService, "_systemctl_check", return_value=True),
    ):
        result = DoctorService(config_file).run()

    output = capsys.readouterr().out
    assert result is True  # only warnings, no errors
    assert "Gesamtstatus: WARNUNG" in output
