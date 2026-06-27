from pathlib import Path
from unittest.mock import Mock, patch

from lbm.backup.restic import ResticRepository


def test_backup_uses_argument_list_without_shell() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    fake_result = Mock()
    fake_result.returncode = 0
    fake_result.stdout = """
Files:           1 new,     0 changed,     0 unmodified
processed 1 files, 10 B in 0:00
snapshot abc123 saved
"""
    fake_result.stderr = ""

    with patch("lbm.backup.restic.subprocess.run", return_value=fake_result) as run_mock:
        repository.backup(
            paths=[Path("/tmp/source; rm -rf root")],
            excludes=["$(whoami)"],
        )

    args, kwargs = run_mock.call_args

    assert isinstance(args[0], list)
    assert kwargs.get("shell") is None
    assert "/tmp/source; rm -rf root" in args[0]
    assert "$(whoami)" in args[0]

def test_parse_backup_output() -> None:
    repository = ResticRepository(
        repository=Path("/tmp/repo"),
        password_file=Path("/tmp/password"),
    )

    output = """
repository 123 opened (version 2, compression level auto)

Files:           5 new,     2 changed,   100 unmodified
Dirs:            1 new,     0 changed,    20 unmodified
Added to the repository: 25.123 MiB (10.000 MiB stored)

processed 107 files, 125.123 MiB in 0:08
snapshot abcdef12 saved
"""

    result = repository._parse_backup_output(output)

    assert result.ok is True
    assert result.snapshot_id == "abcdef12"
    assert result.files_new == 5
    assert result.files_changed == 2
    assert result.files_unmodified == 100
    assert result.processed_files == 107
    assert result.processed_size == "125.123 MiB"
    assert result.duration == "0:08"

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