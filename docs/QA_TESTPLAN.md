# Linux Backup Manager

# Quality Assurance Test Plan

**Version:** 1.1.0-rc1

---

# Purpose

This document defines the quality assurance process for the Linux Backup Manager before a public release.

Every release candidate should successfully pass all tests described in this document.

---

# Test Environment

The following environment has been used during development.

| Component        | Version     |
| ---------------- | ----------- |
| Linux Mint       | Current     |
| Python           | 3.12        |
| Restic           | Installed   |
| USB Backup Drive | LinuxBackup |

---

# Installation Tests

## Fresh Installation

Verify that a completely new user can install the application.

### Steps

* Build the wheel and source distribution using `python -m build`.
* Validate both artifacts using `python -m twine check dist/*`.
* Create a new virtual environment outside the project directory.
* Install the generated wheel, not the source checkout.
* Verify the installation and its dependencies.

```bash
python -m pip install dist/linux_backup_manager-<version>-py3-none-any.whl
backup-manager --version
python -m pip check
```

### Expected Result

* Installation succeeds.
* The correct application version is displayed.
* No dependency conflicts are reported.

---

# Setup Tests

Run:

```bash
backup-manager setup
```

Verify that:

* the configuration directory is created.
* the configuration file is created.
* the password file is created.
* password validation works.
* the USB backup device is detected.
* the repository is created automatically if required.

Run the setup wizard a second time.

### Expected Result

* Existing configuration is detected.
* Existing password file is detected.
* Existing repository is detected.
* No duplicate resources are created.
* The setup process remains idempotent.

---

# Backup Tests

Run:

```bash
backup-manager backup
```

Verify that:

* the backup completes successfully.
* a new snapshot is created.

---

# Snapshot Tests

Run:

```bash
backup-manager snapshots
```

Verify that:

* all snapshots are displayed.
* the newly created snapshot is listed.

---

# Repository Tests

Run:

```bash
backup-manager check
```

Verify that:

* the repository passes the integrity check.

Run:

```bash
backup-manager stats
```

Verify that:

* repository statistics are displayed correctly.

---

# Restore Tests

Run:

```bash
backup-manager restore
```

Verify that:

* snapshot selection works.
* the restore process completes successfully.
* restored files can be opened and used.

---

# Retention Tests

Run:

```bash
backup-manager forget
```

Verify that:

* the configured retention policy is applied correctly.

Run:

```bash
backup-manager prune
```

Verify that:

* unused repository data is removed successfully.

---

# Error Handling Tests

Verify the application's behaviour when:

* the configuration file is missing.
* the password file is missing.
* the repository password is incorrect.
* the USB backup device is missing.
* the repository does not exist.
* the repository is invalid.
* Restic is not installed.
* the configuration file contains invalid YAML.

### Expected Result

All error messages should be clear, understandable and provide actionable information.

---

# Internationalization Tests

Set `system.language` to `de` and then to `en`. Run:

```bash
backup-manager status
backup-manager health
backup-manager doctor
backup-manager setup
backup-manager backup
backup-manager snapshots
backup-manager restore
backup-manager stats
backup-manager check
backup-manager recovery-info
backup-manager recovery-sheet
```

Verify that headings, labels, result states, prompts and application-generated errors use the
selected language consistently. External Restic and systemctl output may remain in the language
provided by those programs. Existing configurations without `system.language` must continue to
use German.

For each language, use an isolated configuration, password file, state directory and local test
repository. Initialize the repository, create a backup, list its snapshot, check repository
integrity and restore the snapshot to a separate target. Compare at least one restored file
byte-for-byte with its source and verify that a failed Restic restore produces a nonzero CLI exit
status.

---

# First-User Tests (Layer 8)

Verify that a first-time user with no prior knowledge of the project can successfully install and configure Linux Backup Manager.

### Test Procedure

* Create a completely fresh Python virtual environment outside the source checkout.
* Install the application from the generated wheel.
* Run:

```bash
backup-manager setup
```

* Follow the setup wizard without manually creating or editing configuration files.
* Create the first backup.
* Verify that the repository is created successfully.
* Run the setup wizard again.

### Expected Result

A first-time user can complete the entire installation and setup process without external assistance.

The repeated execution of the setup wizard must not create duplicate resources or corrupt the existing installation.

---

# Regression Tests

Before every release execute:

### Ruff

```bash
ruff check .
```

### Unit Tests

```bash
pytest
```

### Distribution Build

```bash
python -m build
```

Install the generated wheel in a new virtual environment and verify:

```bash
backup-manager --version
backup-manager --help
pip check
```

### Local CI Quality Gate

Run the complete Python 3.12 quality sequence defined in `.github/workflows/ci.yml` locally on the
final release-candidate commit. The project is maintained locally, so no remote CI result is
required.

### Git Status

```bash
git status
```

### Expected Result

* No linting errors.
* All unit tests pass.
* Wheel and source distribution build successfully.
* A clean installation from the built artifact succeeds.
* German and English end-to-end backup and restore tests pass.
* The complete local CI quality gate succeeds.
* The working tree is clean.

---

# Release Criteria

A release candidate is considered ready when:

* all automated tests pass.
* a fresh installation succeeds.
* the setup wizard completes successfully.
* backups can be created.
* restores can be completed successfully.
* repository checks pass.
* documentation and release claims are consistent and up to date.
* the First-User Test (Layer 8) passes without requiring manual intervention.

---

Linux Backup Manager Documentation

Release Candidate 1.1.0-rc1 · Stable Version 1.0.1
