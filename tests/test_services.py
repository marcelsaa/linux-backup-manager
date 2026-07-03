from pathlib import Path
from unittest.mock import Mock, patch

from lbm.backup.restic import BackupResult, MigrationResult, ResticRepositoryInfo, SnapshotInfo
from lbm.core.application import Application
from lbm.core.config import AppConfig
from lbm.core.state import BackupStateStore
from lbm.services.backup import BackupService
from lbm.services.repository import RepositoryDestination, RepositoryProvider
from lbm.services.repository_maintenance import RepositoryMaintenanceService
from lbm.services.restore import RestoreService
from lbm.targets.usb import USBTargetInfo


def make_config() -> AppConfig:
    return AppConfig.model_validate(
        {
            "system": {"host_name": "test-host"},
            "paths": {
                "log_dir": "logs",
                "state_dir": "state",
                "password_file": "/tmp/restic.pass",
            },
            "backup": {
                "paths": ["/home/test/Documents"],
                "excludes": ["/home/test/.cache"],
            },
            "targets": {
                "usb": {
                    "enabled": True,
                    "label": "LinuxBackup",
                    "repository_path": "restic/test-host",
                }
            },
            "retention": {
                "keep_daily": 14,
                "keep_weekly": 8,
                "keep_monthly": 12,
                "keep_yearly": 3,
            },
        }
    )


def test_repository_provider_resolves_usb_repository() -> None:
    usb_info = USBTargetInfo(
        found=True,
        label="LinuxBackup",
        mountpoint=Path("/media/LinuxBackup"),
        fsavail="100G",
        fsuse_percent="10%",
        writable=True,
    )

    with patch("lbm.services.repository.USBTarget.probe", return_value=usb_info):
        repository = RepositoryProvider(make_config()).get()

    assert repository is not None
    assert repository.repository == Path("/media/LinuxBackup/restic/test-host")
    assert repository.password_file == Path("/tmp/restic.pass")


def test_backup_service_passes_configured_paths_to_repository() -> None:
    restic = Mock()
    restic.check.return_value = ResticRepositoryInfo(True, "Repository vorhanden")
    restic.backup.return_value = BackupResult(
        ok=True,
        snapshot_id="abc123",
        files_new=1,
        files_changed=0,
        files_unmodified=2,
        processed_files=3,
        processed_size="1 MiB",
        duration="0:01",
        message="ok",
    )
    provider = Mock()
    provider.get_all.return_value = [RepositoryDestination("USB", restic)]

    BackupService(make_config(), provider).run()

    restic.backup.assert_called_once_with(
        [Path("/home/test/Documents")],
        ["/home/test/.cache"],
    )


def test_cleanup_runs_after_successful_backup() -> None:
    restic = Mock()
    restic.check.return_value = ResticRepositoryInfo(True, "ok")
    restic.backup.return_value = BackupResult(True, "abc123", 1, 0, 0, 1, "1 B", "0:01", "ok")
    restic.cleanup.return_value = True
    provider = Mock()
    provider.get_all.return_value = [RepositoryDestination("USB", restic)]

    BackupService(make_config(), provider).run()

    restic.cleanup.assert_called_once_with(14, 8, 12, 3)


def test_cleanup_uses_configured_retention_values() -> None:
    restic = Mock()
    restic.check.return_value = ResticRepositoryInfo(True, "ok")
    restic.backup.return_value = BackupResult(True, "abc123", 1, 0, 0, 1, "1 B", "0:01", "ok")
    restic.cleanup.return_value = True
    provider = Mock()
    provider.get_all.return_value = [RepositoryDestination("USB", restic)]
    config = make_config()
    config.retention.keep_daily = 7
    config.retention.keep_weekly = 4
    config.retention.keep_monthly = 6
    config.retention.keep_yearly = 1

    BackupService(config, provider).run()

    restic.cleanup.assert_called_once_with(7, 4, 6, 1)


def test_cleanup_skipped_after_failed_backup() -> None:
    restic = Mock()
    restic.check.return_value = ResticRepositoryInfo(True, "ok")
    restic.backup.return_value = BackupResult(False, None, 0, 0, 0, 0, "0 B", "0:00", "error")
    provider = Mock()
    provider.get_all.return_value = [RepositoryDestination("USB", restic)]

    BackupService(make_config(), provider).run()

    restic.cleanup.assert_not_called()


def test_cleanup_runs_per_destination_independently() -> None:
    ok_repo = Mock()
    ok_repo.check.return_value = ResticRepositoryInfo(True, "ok")
    ok_repo.backup.return_value = BackupResult(True, "snap1", 1, 0, 0, 1, "1 B", "0:01", "ok")
    ok_repo.cleanup.return_value = True
    fail_repo = Mock()
    fail_repo.check.return_value = ResticRepositoryInfo(True, "ok")
    fail_repo.backup.return_value = BackupResult(False, None, 0, 0, 0, 0, "0 B", "0:00", "err")
    provider = Mock()
    provider.get_all.return_value = [
        RepositoryDestination("USB", ok_repo),
        RepositoryDestination("NAS", fail_repo),
    ]

    BackupService(make_config(), provider).run()

    ok_repo.cleanup.assert_called_once()
    fail_repo.cleanup.assert_not_called()


def test_retention_config_defaults() -> None:
    from lbm.core.config import RetentionConfig

    r = RetentionConfig()
    assert r.keep_daily == 14
    assert r.keep_weekly == 8
    assert r.keep_monthly == 12
    assert r.keep_yearly == 3


def test_repository_provider_supports_a_mounted_nas(tmp_path: Path) -> None:
    config = make_config()
    config.targets.usb.enabled = False
    config.targets.nas.enabled = True
    config.targets.nas.mount_path = str(tmp_path)
    config.targets.nas.repository_path = "restic/test-host"

    destinations = RepositoryProvider(config).get_all()

    assert len(destinations) == 1
    assert destinations[0].name == f"NAS: {tmp_path}"
    assert destinations[0].repository.repository == tmp_path / "restic/test-host"


def test_backup_service_runs_for_every_available_destination() -> None:
    first_repository = Mock()
    first_repository.check.return_value = ResticRepositoryInfo(True, "ok")
    first_repository.backup.return_value = BackupResult(
        True, "first", 1, 0, 0, 1, "1 B", "0:01", "ok"
    )
    second_repository = Mock()
    second_repository.check.return_value = ResticRepositoryInfo(True, "ok")
    second_repository.backup.return_value = BackupResult(
        True, "second", 1, 0, 0, 1, "1 B", "0:01", "ok"
    )
    provider = Mock()
    provider.get_all.return_value = [
        RepositoryDestination("USB", first_repository),
        RepositoryDestination("NAS", second_repository),
    ]

    BackupService(make_config(), provider).run()

    first_repository.backup.assert_called_once()
    second_repository.backup.assert_called_once()


def test_repository_provider_prompts_when_multiple_destinations_are_available() -> None:
    first_repository = Mock()
    second_repository = Mock()
    provider = RepositoryProvider(make_config())

    with (
        patch.object(
            provider,
            "get_all",
            return_value=[
                RepositoryDestination("USB", first_repository),
                RepositoryDestination("NAS", second_repository),
            ],
        ),
        patch("builtins.input", return_value="2"),
    ):
        selected = provider.get()

    assert selected is second_repository


def test_forget_stops_after_dry_run_when_user_declines() -> None:
    restic = Mock()
    restic.forget_dry_run.return_value = "snapshot abc123"
    provider = Mock()
    provider.get.return_value = restic

    with patch("builtins.input", return_value="n"):
        RepositoryMaintenanceService(make_config(), provider).forget()

    restic.forget_dry_run.assert_called_once()
    restic.forget.assert_not_called()


def test_setup_does_not_require_an_existing_config(monkeypatch) -> None:
    monkeypatch.setenv("LBM_CONFIG_FILE", "/tmp/lbm-test-config.yaml")
    application = Application()

    with patch("lbm.core.application.SetupService") as setup_service:
        application.setup(interactive=False)

    setup_service.assert_called_once_with(Path("/tmp/lbm-test-config.yaml"))
    setup_service.return_value.run.assert_called_once_with(interactive=False)
    assert application.config is None


def test_successful_backup_records_state(tmp_path: Path) -> None:
    application = Application()
    application.config = make_config()
    application.config.paths.state_dir = str(tmp_path)

    with patch("lbm.core.application.BackupService.run", return_value=True):
        assert application.backup() is True

    assert (tmp_path / "backup-state.json").is_file()


def test_backup_if_due_skips_a_recent_backup(tmp_path: Path) -> None:
    application = Application()
    application.config = make_config()
    application.config.paths.state_dir = str(tmp_path)
    state = BackupStateStore(tmp_path)
    state.record_success()

    with patch("lbm.core.application.BackupService.run") as backup:
        assert application.backup_if_due() is True

    backup.assert_not_called()


def test_failed_backup_does_not_record_success(tmp_path: Path) -> None:
    application = Application()
    application.config = make_config()
    application.config.paths.state_dir = str(tmp_path)

    with patch("lbm.core.application.BackupService.run", return_value=False):
        assert application.backup() is False

    assert not (tmp_path / "backup-state.json").exists()


def test_restore_prompts_for_a_user_target(tmp_path: Path) -> None:
    repository = Mock()
    repository.snapshots.return_value = [
        SnapshotInfo("abc123", "28.06.2026 12:00:00", "test-host", ["/tmp/source"])
    ]
    repository.restore.return_value = BackupResult(
        True, "abc123", 0, 0, 0, 0, "", "", "Restore erfolgreich."
    )
    provider = Mock()
    provider.get.return_value = repository
    target = tmp_path / "restore"

    with patch("builtins.input", side_effect=["1", str(target), "j"]):
        result = RestoreService(make_config(), repository_provider=provider).run()

    assert result is True
    repository.restore.assert_called_once_with("abc123", target)


def test_restore_failure_is_propagated(tmp_path: Path) -> None:
    repository = Mock()
    repository.snapshots.return_value = [
        SnapshotInfo("abc123", "28.06.2026 12:00:00", "test-host", ["/tmp/source"])
    ]
    repository.restore.return_value = BackupResult(
        False, "abc123", 0, 0, 0, 0, "", "", "Fatal: restore failed"
    )
    provider = Mock()
    provider.get.return_value = repository
    target = tmp_path / "restore"

    with patch("builtins.input", side_effect=["1", str(target), "j"]):
        result = RestoreService(make_config(), repository_provider=provider).run()

    assert result is False


def test_migrate_copies_snapshots_between_two_targets() -> None:
    source_repo = Mock()
    target_repo = Mock()
    target_repo.check.return_value = ResticRepositoryInfo(True, "ok")
    target_repo.copy_from.return_value = MigrationResult(True, "copied")
    provider = Mock()
    provider.get_all.return_value = [
        RepositoryDestination("USB", source_repo),
        RepositoryDestination("NAS", target_repo),
    ]

    with patch("builtins.input", side_effect=["1", "1", "j"]):
        result = RepositoryMaintenanceService(make_config(), provider).migrate()

    assert result is True
    target_repo.copy_from.assert_called_once_with(source_repo)
    target_repo.init_repository.assert_not_called()


def test_migrate_initializes_an_uninitialized_destination_first() -> None:
    source_repo = Mock()
    target_repo = Mock()
    target_repo.check.return_value = ResticRepositoryInfo(False, "missing")
    target_repo.init_repository.return_value = ResticRepositoryInfo(True, "created")
    target_repo.copy_from.return_value = MigrationResult(True, "copied")
    provider = Mock()
    provider.get_all.return_value = [
        RepositoryDestination("USB", source_repo),
        RepositoryDestination("NAS", target_repo),
    ]

    with patch("builtins.input", side_effect=["1", "1", "j"]):
        result = RepositoryMaintenanceService(make_config(), provider).migrate()

    assert result is True
    target_repo.init_repository.assert_called_once_with()
    target_repo.copy_from.assert_called_once_with(source_repo)


def test_migrate_requires_at_least_two_targets() -> None:
    provider = Mock()
    provider.get_all.return_value = [RepositoryDestination("USB", Mock())]

    result = RepositoryMaintenanceService(make_config(), provider).migrate()

    assert result is False


def test_migrate_stops_when_user_declines_confirmation() -> None:
    source_repo = Mock()
    target_repo = Mock()
    provider = Mock()
    provider.get_all.return_value = [
        RepositoryDestination("USB", source_repo),
        RepositoryDestination("NAS", target_repo),
    ]

    with patch("builtins.input", side_effect=["1", "1", "n"]):
        result = RepositoryMaintenanceService(make_config(), provider).migrate()

    assert result is False
    target_repo.copy_from.assert_not_called()


def test_migrate_failure_is_reported() -> None:
    source_repo = Mock()
    target_repo = Mock()
    target_repo.check.return_value = ResticRepositoryInfo(True, "ok")
    target_repo.copy_from.return_value = MigrationResult(False, "Fatal: wrong password")
    provider = Mock()
    provider.get_all.return_value = [
        RepositoryDestination("USB", source_repo),
        RepositoryDestination("NAS", target_repo),
    ]

    with patch("builtins.input", side_effect=["1", "1", "j"]):
        result = RepositoryMaintenanceService(make_config(), provider).migrate()

    assert result is False
