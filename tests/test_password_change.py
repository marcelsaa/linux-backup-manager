from pathlib import Path
from unittest.mock import Mock, patch

from lbm.core.config import AppConfig
from lbm.services.password import PasswordChangeService
from lbm.services.repository import RepositoryDestination


def make_config(tmp_path: Path) -> AppConfig:
    password_file = tmp_path / "restic.pass"
    password_file.write_text("old-secret\n", encoding="utf-8")
    password_file.chmod(0o600)
    return AppConfig.model_validate(
        {
            "system": {"host_name": "test-host"},
            "paths": {
                "log_dir": "logs",
                "state_dir": "state",
                "password_file": str(password_file),
            },
            "backup": {"paths": ["/home/test"], "excludes": []},
            "targets": {"usb": {"enabled": True, "label": "X", "repository_path": "r"}},
            "retention": {"keep_daily": 14, "keep_weekly": 8, "keep_monthly": 12, "keep_yearly": 3},
        }
    )


def make_repo(change_ok: bool = True) -> Mock:
    repo = Mock()
    repo.change_password.return_value = change_ok
    return repo


def test_change_password_updates_all_repositories(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    repo1, repo2 = make_repo(), make_repo()
    provider = Mock()
    provider.get_all.return_value = [
        RepositoryDestination("USB", repo1),
        RepositoryDestination("NAS", repo2),
    ]

    with (
        patch("getpass.getpass", return_value="new-secret"),
        patch("builtins.input", return_value="n"),
    ):
        result = PasswordChangeService(config, tmp_path / "config.yaml", provider).run()

    assert result is True
    repo1.change_password.assert_called_once()
    repo2.change_password.assert_called_once()


def test_change_password_updates_password_file_on_success(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    provider = Mock()
    provider.get_all.return_value = [RepositoryDestination("USB", make_repo())]

    with (
        patch("getpass.getpass", return_value="new-secret"),
        patch("builtins.input", return_value="n"),
    ):
        PasswordChangeService(config, tmp_path / "config.yaml", provider).run()

    password_file = Path(config.paths.password_file)
    assert password_file.read_text(encoding="utf-8") == "new-secret\n"
    assert password_file.stat().st_mode & 0o777 == 0o600


def test_change_password_aborts_on_mismatch(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    provider = Mock()
    provider.get_all.return_value = [RepositoryDestination("USB", make_repo())]

    with patch("getpass.getpass", side_effect=["new-secret", "wrong-confirm"]):
        result = PasswordChangeService(config, tmp_path / "config.yaml", provider).run()

    assert result is False
    provider.get_all.assert_not_called()
    assert Path(config.paths.password_file).read_text(encoding="utf-8") == "old-secret\n"


def test_change_password_aborts_on_empty_password(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    provider = Mock()

    with patch("getpass.getpass", return_value=""):
        result = PasswordChangeService(config, tmp_path / "config.yaml", provider).run()

    assert result is False
    provider.get_all.assert_not_called()


def test_change_password_aborts_when_no_destination_reachable(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    provider = Mock()
    provider.get_all.return_value = []

    with patch("getpass.getpass", return_value="new-secret"):
        result = PasswordChangeService(config, tmp_path / "config.yaml", provider).run()

    assert result is False


def test_change_password_reports_partial_when_second_repo_fails(
    tmp_path: Path, capsys
) -> None:
    config = make_config(tmp_path)
    provider = Mock()
    provider.get_all.return_value = [
        RepositoryDestination("USB", make_repo(change_ok=True)),
        RepositoryDestination("NAS", make_repo(change_ok=False)),
    ]

    with patch("getpass.getpass", return_value="new-secret"):
        result = PasswordChangeService(config, tmp_path / "config.yaml", provider).run()

    assert result is False
    output = capsys.readouterr().out
    assert "USB" in output
    assert Path(config.paths.password_file).read_text(encoding="utf-8") == "old-secret\n"


def test_change_password_does_not_update_file_when_repo_fails(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    provider = Mock()
    provider.get_all.return_value = [RepositoryDestination("USB", make_repo(change_ok=False))]

    with patch("getpass.getpass", return_value="new-secret"):
        PasswordChangeService(config, tmp_path / "config.yaml", provider).run()

    assert Path(config.paths.password_file).read_text(encoding="utf-8") == "old-secret\n"


def test_change_password_offers_recovery_sheet_after_success(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    provider = Mock()
    provider.get_all.return_value = [RepositoryDestination("USB", make_repo())]

    with (
        patch("getpass.getpass", return_value="new-secret"),
        patch("builtins.input", return_value="j"),
        patch("lbm.services.password.RecoverySheetService.run") as mock_sheet,
    ):
        PasswordChangeService(config, tmp_path / "config.yaml", provider).run()

    mock_sheet.assert_called_once()


def test_change_password_skips_recovery_sheet_when_declined(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    provider = Mock()
    provider.get_all.return_value = [RepositoryDestination("USB", make_repo())]

    with (
        patch("getpass.getpass", return_value="new-secret"),
        patch("builtins.input", return_value="n"),
        patch("lbm.services.password.RecoverySheetService.run") as mock_sheet,
    ):
        PasswordChangeService(config, tmp_path / "config.yaml", provider).run()

    mock_sheet.assert_not_called()


def test_restic_repository_change_password_uses_key_passwd(tmp_path: Path) -> None:
    from lbm.backup.restic import ResticRepository

    password_file = tmp_path / "restic.pass"
    password_file.write_text("secret\n", encoding="utf-8")
    new_pw_file = tmp_path / "new.pass"
    new_pw_file.write_text("new\n", encoding="utf-8")
    repo = ResticRepository(tmp_path / "repo", password_file)

    with patch("lbm.backup.restic.subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        result = repo.change_password(new_pw_file)

    assert result is True
    args = mock_run.call_args[0][0]
    assert args[:3] == ["restic", "key", "passwd"]
    assert "--new-password-file" in args
    assert str(new_pw_file) in args
    assert mock_run.call_args[1].get("shell") is None
