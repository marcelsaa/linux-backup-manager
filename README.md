# Linux Backup Manager

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

Release users should run the standalone managed installer supplied beside the wheel. It verifies
the published SHA-256, performs write-free preflight checks and chooses either fresh installation
or the supported Version 1.0.1 upgrade path:

```bash
python3 installer.py linux_backup_manager-1.1.0-py3-none-any.whl \
  --sha256 <PUBLISHED_SHA256> --dry-run
```

Repeat without `--dry-run` only after all checks pass. See `docs/INSTALL.md` for rollback guarantees
and the complete command.

For source development, obtain or clone the repository, then change into it:

```bash
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

# Available Commands

| Command                    | Description                           |
| -------------------------- | ------------------------------------- |
| `backup-manager setup`     | Interactive setup wizard              |
| `backup-manager settings`  | Change individual settings interactively |
| `backup-manager export-config` | Copy the current configuration file to another location |
| `backup-manager import-config` | Validate and adopt an external configuration file |
| `backup-manager status`    | Display system information            |
| `backup-manager health`    | Run health checks                     |
| `backup-manager doctor`    | Run read-only support diagnostics     |
| `backup-manager recovery-info` | Display password-safe recovery information |
| `backup-manager recovery-sheet` | Create a password-free recovery document |
| `backup-manager change-password` | Change the repository password  |
| `backup-manager backup`    | Create a backup                       |
| `backup-manager schedule-install` | Install and activate automatic backups |
| `backup-manager schedule-status` | Display the systemd timer status |
| `backup-manager schedule-remove` | Disable automatic backups |
| `backup-manager snapshots` | List available snapshots              |
| `backup-manager restore`   | Restore data from a snapshot          |
| `backup-manager stats`     | Display repository statistics         |
| `backup-manager check`     | Verify repository integrity           |
| `backup-manager forget`    | Apply the configured retention policy |
| `backup-manager prune`     | Remove unreferenced repository data   |

---

# Documentation

Detailed documentation is available in the `docs/` directory.

* Installation Guide
* User Guide
* Configuration Reference
* Restore Guide
* Recovery and Password Safety Guide
* FAQ
* Architecture Overview
* Quality Assurance Test Plan
* Project Roadmap
* Automatic Backup Guide
* Internationalization Guide
* Development Process

---

# Roadmap

See [the project roadmap](docs/ROADMAP.md) for completed and planned work.

---

# Project Status

**Current Version:** 1.1.0

Linux Backup Manager 1.1.0 is the current stable release. It adds a standalone managed installer,
complete German and English internationalization and a hardened first-user setup wizard. Artifacts
are built locally and are not published to production PyPI.

The core functionality has been implemented and successfully validated through automated tests, manual integration tests and multiple first-user installation scenarios.

Version 1.1 is feature-frozen. Until the final release, changes are limited to bug fixes,
documentation and translations; new features are deferred to Version 1.2.

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
