# Linux Backup Manager

[![CI](https://github.com/marcelsaa/linux-backup-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/marcelsaa/linux-backup-manager/actions/workflows/ci.yml)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](pyproject.toml)

**[Deutsche Version](docs/de/README.md)**

> **Reliable Linux backups should be simple.**

Linux Backup Manager (LBM) is an open-source command-line application that simplifies creating, maintaining and restoring backups on Linux systems.

Instead of manually configuring Restic repositories, password files and backup locations, LBM provides an interactive setup wizard that guides users through the complete initial configuration. Once configured, all backup and maintenance tasks can be performed through a consistent command-line interface.

LBM focuses on reliability, predictable behaviour and long-term maintainability while building on the proven open-source backup tool **Restic**.

---

# Why Linux Backup Manager?

Creating reliable backups should not require extensive knowledge of backup software.

Linux Backup Manager was created with the following goals:

* Easy initial setup
* Reliable backup workflow
* Consistent command-line interface
* Clear and actionable error messages
* Minimal configuration effort
* Long-term maintainability

The project is intended for Linux users who want a dependable backup solution without manually managing Restic repositories or complex configuration files.

---

# Features

## Easy Setup

* Interactive setup wizard
* Automatic configuration generation
* Safe interactive editing of existing configurations with automatic backup
* Automatic password file creation
* Explicit non-recoverable-password warning during setup
* Recovery metadata and emergency instructions without exposing the password
* Optional password-free recovery sheet with secure file permissions
* Automatic repository initialization
* Clear distinction between missing repositories and invalid repository passwords
* XDG-compliant configuration directory

## Backup

* Restic-based backups
* USB backup support
* NAS backup support for mounted network shares
* Parallel backups to multiple destinations
* User-configurable backup time and interval through systemd user timers
* Immediate catch-up backup when the configured interval has been exceeded
* Configurable backup paths
* Configurable exclude patterns

## Restore

* Snapshot selection
* Guided restore workflow
* Restore into a separate target directory

## Repository Maintenance

* Repository integrity checks
* Repository statistics
* Snapshot management
* Retention policy
* Repository pruning

## User Experience

* Colored console output
* Clear error messages
* Consistent command structure
* Robust first-run experience
* Read-only `doctor` diagnostics for configuration, credentials, targets and repositories
* Complete German/English command-line output with catalog fallback

---

# Requirements

Linux Backup Manager requires:

* Linux
* Python 3.12 or newer
* Restic

---

# Installation

Download the wheel and `installer.py` from the [Releases page](https://github.com/marcelsaa/linux-backup-manager/releases)
and run the standalone managed installer supplied beside the wheel. It verifies the published
SHA-256, performs write-free preflight checks and chooses either fresh installation or the
supported Version 1.0.1 upgrade path:

```bash
python3 installer.py linux_backup_manager-1.2.0-py3-none-any.whl \
  --sha256 <PUBLISHED_SHA256> --dry-run
```

Repeat without `--dry-run` only after all checks pass. See `docs/INSTALL.md` for rollback guarantees
and the complete command.

For source development, clone the repository and change into it:

```bash
git clone https://github.com/marcelsaa/linux-backup-manager.git
cd linux-backup-manager
```

Install the application:

```bash
pip install .
```

Verify the installation:

```bash
backup-manager --version
```

---

# Quick Start

Run the setup wizard:

```bash
backup-manager setup
```

Create your first backup:

```bash
backup-manager backup
```

Display available snapshots:

```bash
backup-manager snapshots
```

Restore data:

```bash
backup-manager restore
```

Verify the repository:

```bash
backup-manager check
```

Diagnose the complete backup environment without changing it:

```bash
backup-manager doctor
```

---

# Example Session

An abbreviated, illustrative run — actual wording depends on the configured language and
current system state:

```
$ backup-manager backup
Starting backup to USB (LinuxBackup) ...
Backup completed: 1284 files, 2.1 GiB new data, 47.3 GiB total in repository
Applying retention policy and pruning ...

$ backup-manager doctor
── Configuration ────────────────────────────────
✓ Configuration file             OK: valid and readable
✓ Password file permissions      OK: 0600

── Backup targets ───────────────────────────────
✓ USB (LinuxBackup)              OK: mounted and writable

── Repositories ─────────────────────────────────
✓ USB repository                 OK: reachable, last backup 2 hours ago

Summary: 4 OK, 0 warnings, 0 errors
```

---

# Available Commands

| Command                    | Description                           |
| -------------------------- | ------------------------------------- |
| `backup-manager` / `backup-manager menu` | Open the guided main menu (default with no arguments) |
| `backup-manager setup`     | Interactive setup wizard              |
| `backup-manager settings`  | Change individual settings interactively |
| `backup-manager export-config` | Copy the current configuration file to another location |
| `backup-manager import-config` | Validate and adopt an external configuration file |
| `backup-manager status`    | Display system information            |
| `backup-manager health`    | Run health checks                     |
| `backup-manager doctor`    | Run read-only support diagnostics     |
| `backup-manager logs`      | View the log file (path and recent entries) |
| `backup-manager recovery-info` | Display password-safe recovery information |
| `backup-manager recovery-sheet` | Create a password-free recovery document |
| `backup-manager change-password` | Change the repository password  |
| `backup-manager backup`    | Create a backup                       |
| `backup-manager schedule-install` | Install and activate automatic backups |
| `backup-manager schedule-status` | Display the systemd timer status |
| `backup-manager schedule-remove` | Disable automatic backups |
| `backup-manager snapshots` | List available snapshots              |
| `backup-manager mount`     | Mount a snapshot read-only and browse it in a file manager (default restore action) |
| `backup-manager restore`   | Restore a full snapshot to a directory (Expert Function) |
| `backup-manager stats`     | Display repository statistics         |
| `backup-manager check`     | Verify repository integrity           |
| `backup-manager forget`    | Apply the configured retention policy |
| `backup-manager prune`     | Remove unreferenced repository data   |

---

# Documentation

Detailed documentation is available in the `docs/` directory.

* [Installation Guide](docs/INSTALL.md) ([Deutsch](docs/de/INSTALL.md))
* [User Guide](docs/USER_GUIDE.md) ([Deutsch](docs/de/USER_GUIDE.md))
* [Configuration Reference](docs/CONFIGURATION.md) ([Deutsch](docs/de/CONFIGURATION.md))
* [Restore Guide](docs/RESTORE.md) ([Deutsch](docs/de/RESTORE.md))
* [Recovery and Password Safety Guide](docs/RECOVERY.md) ([Deutsch](docs/de/RECOVERY.md))
* [FAQ](docs/FAQ.md) ([Deutsch](docs/de/FAQ.md))
* [Architecture Overview](docs/ARCHITECTURE.md)
* [Quality Assurance Test Plan](docs/QA_TESTPLAN.md)
* [Project Roadmap](docs/ROADMAP.md)
* [Automatic Backup Guide](docs/SYSTEMD.md) ([Deutsch](docs/de/SYSTEMD.md))
* [Internationalization Guide](docs/INTERNATIONALIZATION.md)
* [Development Process](docs/DEVELOPMENT.md)

---

# Roadmap

See [the project roadmap](docs/ROADMAP.md) for completed and planned work.

---

# Project Status

**Current stable version:** 1.2.0

Linux Backup Manager 1.2.0 is the current stable release. It adds an interactive `settings`
menu, a `change-password` command, structured `doctor` diagnostics with systemd timer status,
`export-config`/`import-config`, and sensible retention defaults with automatic repository
cleanup, on top of the managed installer and full German/English internationalization
introduced in 1.1.0. Artifacts are built locally and are not published to production PyPI.

The core functionality has been implemented and successfully validated through automated tests, manual integration tests and multiple first-user installation scenarios.

See the [project roadmap](docs/ROADMAP.md) for completed and planned work.

---

# Contributing & Support

Linux Backup Manager is a personal project, shared publicly so others can read, use and adapt
it. It is not seeking contributors, and there is no guarantee that issues or pull requests will
be reviewed — see [`CONTRIBUTING.md`](CONTRIBUTING.md) for details. Security vulnerabilities are
the one exception and can be reported privately; see [`SECURITY.md`](SECURITY.md).

---

# Disclaimer

Linux Backup Manager is provided **"as is"**, without any express or implied warranty.

Although every effort has been made to provide reliable software, no guarantee is given that the software is free of defects or suitable for every use case.

Users are responsible for verifying their backups and regularly testing restore procedures.

The author assumes no liability for data loss or other damages resulting from the use of this software.

---

# License

Linux Backup Manager is licensed under the GNU General Public License v3.0.

Linux Backup Manager calls the external [Restic](https://restic.net/) binary as a separate
system tool; there is no code linking between the two projects. Restic is licensed under the
BSD 2-Clause License, which is compatible with GPL-3.0.

---

Copyright © 2026 Marcel Saager
