from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from lbm.backup.restic import RepositoryStatus, ResticRepository
from lbm.core.errors import ExternalCommandError


def test_backup_uses_argument_list_without_shell() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 0
    fake_result.stdout = (
        '{"message_type":"summary","files_new":1,"files_changed":0,'
        '"files_unmodified":0,"total_files_processed":1,'
        '"total_bytes_processed":10,"total_duration":0.1,"snapshot_id":"abc123"}\n'
    )
    fake_result.stderr = ""

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result) as run_mock:
        repository.backup(
            paths=[Path("/tmp/source; rm -rf root")],
            excludes=["$(whoami)"],
        )

    args, kwargs = run_mock.call_args

    assert isinstance(args[0], list)
    assert kwargs.get("shell") is None
    assert "--json" in args[0]
    assert "/tmp/source; rm -rf root" in args[0]
    assert "$(whoami)" in args[0]


def test_parse_backup_json_extracts_all_fields() -> None:
    repository = ResticRepository(Path("/tmp/repo"), Path("/tmp/password"))
    output = (
        '{"message_type":"status","seconds_elapsed":0.1}\n'
        '{"message_type":"summary","files_new":5,"files_changed":2,'
        '"files_unmodified":100,"total_files_processed":107,'
        '"total_bytes_processed":10485760,"total_duration":8.0,'
        '"snapshot_id":"abcdef12"}\n'
    )
    result = repository._parse_backup_json(output)
    assert result.ok is True
    assert result.snapshot_id == "abcdef12"
    assert result.files_new == 5
    assert result.files_changed == 2
    assert result.files_unmodified == 100
    assert result.processed_files == 107
    assert result.processed_size == "10.000 MiB"
    assert result.duration == "0:08"


def test_parse_backup_json_fallback_when_no_summary() -> None:
    repository = ResticRepository(Path("/tmp/repo"), Path("/tmp/password"))
    result = repository._parse_backup_json("unexpected non-json output\n")
    assert result.ok is True
    assert result.snapshot_id is None
    assert result.files_new == 0


def test_format_bytes_converts_to_human_readable() -> None:
    repo = ResticRepository(Path("/tmp/repo"), Path("/tmp/pw"))
    assert repo._format_bytes(0) == "0 B"
    assert repo._format_bytes(512) == "512 B"
    assert repo._format_bytes(1024) == "1.000 KiB"
    assert repo._format_bytes(10485760) == "10.000 MiB"
    assert repo._format_bytes(1073741824) == "1.000 GiB"


def test_format_duration_formats_seconds() -> None:
    repo = ResticRepository(Path("/tmp/repo"), Path("/tmp/pw"))
    assert repo._format_duration(0.0) == "0:00"
    assert repo._format_duration(8.0) == "0:08"
    assert repo._format_duration(65.7) == "1:05"
    assert repo._format_duration(3661.0) == "61:01"

def test_backup_returns_failed_result_on_restic_error() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 1
    fake_result.stdout = ""
    fake_result.stderr = "Fatal: wrong password or no key found"

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.backup(
            paths=[Path("/tmp/source")],
            excludes=[],
        )

    assert result.ok is False
    assert result.snapshot_id is None
    assert result.message == "Fatal: wrong password or no key found"


def test_check_distinguishes_missing_repository(tmp_path: Path) -> None:
    repository = ResticRepository(tmp_path / "missing", tmp_path / "password")
    fake_result = Mock(returncode=1, stderr="Fatal: repository does not exist")

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.check()

    assert result.initialized is False
    assert result.status is RepositoryStatus.MISSING


def test_check_distinguishes_wrong_password(tmp_path: Path) -> None:
    repository_path = tmp_path / "repository"
    repository_path.mkdir()
    (repository_path / "config").write_text("repository config", encoding="utf-8")
    repository = ResticRepository(repository_path, tmp_path / "password")
    fake_result = Mock(returncode=1, stderr="Fatal: wrong password or no key found")

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.check()

    assert result.initialized is False
    assert result.status is RepositoryStatus.WRONG_PASSWORD


def test_check_preserves_other_repository_errors(tmp_path: Path) -> None:
    repository_path = tmp_path / "repository"
    repository_path.mkdir()
    (repository_path / "config").write_text("repository config", encoding="utf-8")
    repository = ResticRepository(repository_path, tmp_path / "password")
    fake_result = Mock(returncode=1, stderr="Fatal: repository is damaged")

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.check()

    assert result.initialized is False
    assert result.status is RepositoryStatus.ERROR

def test_snapshots_parses_restic_json() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 0
    fake_result.stdout = """
[
  {
    "short_id": "abc123",
    "time": "2026-06-27T12:30:00+02:00",
    "hostname": "blackpanther",
    "paths": ["/home/marcel"]
  }
]
"""
    fake_result.stderr = ""

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        snapshots = repository.snapshots()

    assert len(snapshots) == 1
    assert snapshots[0].snapshot_id == "abc123"
    assert snapshots[0].host == "blackpanther"
    assert snapshots[0].paths == ["/home/marcel"]

def test_snapshots_returns_empty_list_on_restic_error() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 1
    fake_result.stdout = ""
    fake_result.stderr = "Fatal: repository does not exist"

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        snapshots = repository.snapshots()

    assert snapshots == []

def test_snapshots_returns_empty_list_on_invalid_json() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 0
    fake_result.stdout = "this is not json"
    fake_result.stderr = ""

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        snapshots = repository.snapshots()

    assert snapshots == []

def test_snapshots_handles_invalid_timestamp() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 0
    fake_result.stdout = """
[
  {
    "short_id": "abc123",
    "time": "not-a-date",
    "hostname": "blackpanther",
    "paths": ["/home/marcel"]
  }
]
"""
    fake_result.stderr = ""

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        snapshots = repository.snapshots()

    assert len(snapshots) == 1
    assert snapshots[0].time == "not-a-date"

def test_restore_uses_argument_list_without_shell() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 0
    fake_result.stdout = ""
    fake_result.stderr = ""

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result) as run_mock:
        repository.restore(
            snapshot_id="$(whoami)",
            target=Path("/tmp/restore; rm -rf root"),
        )

    args, kwargs = run_mock.call_args

    assert isinstance(args[0], list)
    assert kwargs.get("shell") is None
    assert "$(whoami)" in args[0]
    assert "/tmp/restore; rm -rf root" in args[0]

def test_restore_returns_failed_result_on_restic_error() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 1
    fake_result.stdout = ""
    fake_result.stderr = "Fatal: unable to restore snapshot"

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.restore(
            snapshot_id="abc123",
            target=Path("/tmp/restore"),
        )

    assert result.ok is False
    assert result.snapshot_id == "abc123"
    assert result.message == "Fatal: unable to restore snapshot"


def test_restore_does_not_reclassify_lchown_error_as_success() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 1
    fake_result.stdout = ""
    fake_result.stderr = (
        "ignoring error for /tmp: lchown /tmp/restore/tmp: invalid argument\n"
        "Fatal: There were 1 errors"
    )

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.restore(
            snapshot_id="abc123",
            target=Path("/tmp/restore"),
        )

    assert result.ok is False
    assert result.message == fake_result.stderr

def test_start_mount_uses_argument_list_without_shell() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )
    fake_process = Mock()

    with patch("lbm.backup.restic.subprocess.Popen", return_value=fake_process) as popen_mock:
        result = repository.start_mount(Path("/tmp/mount; rm -rf root"))

    args, kwargs = popen_mock.call_args
    assert result is fake_process
    assert isinstance(args[0], list)
    assert kwargs.get("shell") is None
    assert "/tmp/mount; rm -rf root" in args[0]
    assert kwargs["env"]["RESTIC_REPOSITORY"] == "/tmp/repo"
    assert kwargs["env"]["RESTIC_PASSWORD_FILE"] == "/tmp/password"

def test_start_mount_raises_external_command_error_when_restic_missing() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    with (
        patch("lbm.backup.restic.subprocess.Popen", side_effect=FileNotFoundError),
        pytest.raises(ExternalCommandError),
    ):
        repository.start_mount(Path("/tmp/mount"))

def test_check_repository_returns_success() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 0
    fake_result.stdout = "no errors were found"
    fake_result.stderr = ""

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.check_repository()

    assert result.initialized is True
    assert result.message == "Repository-Prüfung erfolgreich."

def test_check_repository_returns_error_message() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 1
    fake_result.stdout = ""
    fake_result.stderr = "Fatal: repository is damaged"

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.check_repository()

    assert result.initialized is False
    assert result.message == "Fatal: repository is damaged"

def test_forget_dry_run_uses_argument_list_without_shell() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 0
    fake_result.stdout = "snapshots to remove: 0"
    fake_result.stderr = ""

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result) as run_mock:
        repository.forget_dry_run(
            keep_daily=7,
            keep_weekly=4,
            keep_monthly=6,
            keep_yearly=1,
        )

    args, kwargs = run_mock.call_args

    assert isinstance(args[0], list)
    assert kwargs.get("shell") is None
    assert "--dry-run" in args[0]
    assert "--keep-daily" in args[0]

def test_forget_dry_run_returns_error_message() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 1
    fake_result.stdout = ""
    fake_result.stderr = "Fatal: invalid policy"

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.forget_dry_run(
            keep_daily=7,
            keep_weekly=4,
            keep_monthly=6,
            keep_yearly=1,
        )

    assert result == "Fatal: invalid policy"

def test_forget_returns_stdout_on_success() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 0
    fake_result.stdout = "removed 2 snapshots"
    fake_result.stderr = ""

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.forget(
            keep_daily=7,
            keep_weekly=4,
            keep_monthly=6,
            keep_yearly=1,
        )

    assert result == "removed 2 snapshots"

def test_forget_returns_error_message() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 1
    fake_result.stdout = ""
    fake_result.stderr = "Fatal: forget failed"

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.forget(
            keep_daily=7,
            keep_weekly=4,
            keep_monthly=6,
            keep_yearly=1,
        )

    assert result == "Fatal: forget failed"

def test_prune_returns_stdout_on_success() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 0
    fake_result.stdout = "prune done"
    fake_result.stderr = ""

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.prune()

    assert result == "prune done"

def test_prune_returns_error_message() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 1
    fake_result.stdout = ""
    fake_result.stderr = "Fatal: prune failed"

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.prune()

    assert result == "Fatal: prune failed"

def test_init_repository_returns_success() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 0
    fake_result.stdout = "created restic repository"
    fake_result.stderr = ""

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.init_repository()

    assert result.initialized is True
    assert result.message == "Repository erfolgreich erstellt"

def test_init_repository_returns_error_message() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 1
    fake_result.stdout = ""
    fake_result.stderr = "Fatal: repository already exists"

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.init_repository()

    assert result.initialized is False
    assert result.message == "Fatal: repository already exists"

def test_check_returns_repository_present() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 0
    fake_result.stdout = ""
    fake_result.stderr = ""

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.check()

    assert result.initialized is True
    assert result.message == "Repository vorhanden"

def test_check_returns_repository_error() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 1
    fake_result.stdout = ""
    fake_result.stderr = "Fatal: repository not found"

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result):
        result = repository.check()

    assert result.initialized is False
    assert result.message == "Fatal: repository not found"
