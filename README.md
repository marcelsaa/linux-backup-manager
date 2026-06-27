# Linux Backup Manager

> **Reliable Linux backups should be simple.**

Linux Backup Manager (LBM) is an open-source command-line application that simplifies creating, maintaining and restoring backups on Linux systems.

Instead of manually configuring Restic repositories, password files and backup locations, LBM provides an interactive setup wizard that guides users through the complete initial configuration. Once configured, all backup and maintenance tasks can be performed through a consistent command-line interface.

LBM focuses on reliability, predictable behaviour and long-term maintainability while building on proven open-source technologies such as **Restic** and **Timeshift**.

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
* Automatic password file creation
* Automatic repository initialization
* XDG-compliant configuration directory

## Backup

* Restic-based backups
* USB backup support
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

---

# Requirements

Linux Backup Manager requires:

* Linux
* Python 3.12 or newer
* Restic
* Timeshift

---

# Installation

Clone the repository:

```bash
git clone https://github.com/<your-account>/linux-backup-manager.git
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

---

# Available Commands

| Command                    | Description                           |
| -------------------------- | ------------------------------------- |
| `backup-manager setup`     | Interactive setup wizard              |
| `backup-manager status`    | Display system information            |
| `backup-manager health`    | Run health checks                     |
| `backup-manager backup`    | Create a backup                       |
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
* FAQ
* Architecture Overview
* Quality Assurance Test Plan
* Project Roadmap

---

# Roadmap

Planned features for Version 1.1 include:

* Multiple backup targets (USB and NAS)
* Interactive backup source selection
* Interactive backup target selection
* Refactoring into dedicated service classes
* Improved recovery workflow
* Warning during setup that repository passwords cannot be recovered
* Complete internationalization (German and English)

---

# Project Status

**Current Version:** 1.0.0

Linux Backup Manager is currently approaching its first public release.

The core functionality has been implemented and successfully validated through automated tests, manual integration tests and multiple first-user installation scenarios.

The current focus is on documentation, quality assurance and final release preparation.

---

# Disclaimer

Linux Backup Manager is provided **"as is"**, without any express or implied warranty.

Although every effort has been made to provide reliable software, no guarantee is given that the software is free of defects or suitable for every use case.

Users are responsible for verifying their backups and regularly testing restore procedures.

The author assumes no liability for data loss or other damages resulting from the use of this software.

---

# License

The licensing model will be finalized before the first public release.

---

Copyright © 2026 Marcel Saager
