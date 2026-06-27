# Linux Backup Manager

> **A simple and reliable backup manager for Linux based on Restic and Timeshift.**

Linux Backup Manager (LBM) is a command-line application that simplifies the creation and management of backups on Linux systems.

The project combines the proven backup capabilities of **Restic** with **Timeshift** snapshots and provides a consistent command-line interface for setup, backup, restore and repository maintenance.

The primary goal of LBM is reliability, simplicity and predictable behaviour. A new installation can be completed using the integrated setup wizard without manually creating configuration files.

---

# Features

## Easy setup

- Interactive setup wizard
- Automatic creation of the configuration file
- Automatic creation of the password file
- Automatic initialization of the Restic repository

## Backup

- Restic based backups
- USB backup support
- Configurable backup sources
- Configurable exclude patterns

## Restore

- List available snapshots
- Restore individual snapshots
- Restore into a separate target directory

## Repository maintenance

- Repository integrity check
- Snapshot management
- Retention policy
- Repository pruning
- Health checks

## User experience

- Colored console output
- Helpful error messages
- XDG compliant configuration directory
- Python 3.12+

---

# Requirements

The following software must be installed:

- Linux
- Python 3.12 or newer
- Restic
- Timeshift

---

# Installation

Clone the repository.

```bash
git clone https://github.com/<your-account>/linux-backup-manager.git

cd linux-backup-manager
```

Install the project.

```bash
pip install .
```

Verify the installation.

```bash
backup-manager --version
```

---

# Quick Start

Run the setup wizard.

```bash
backup-manager setup
```

Create your first backup.

```bash
backup-manager backup
```

Display available snapshots.

```bash
backup-manager snapshots
```

Restore a snapshot.

```bash
backup-manager restore
```

---

# Available commands

| Command | Description |
|----------|-------------|
| `backup-manager setup` | Interactive setup wizard |
| `backup-manager status` | Display system status |
| `backup-manager health` | Run health checks |
| `backup-manager backup` | Create a backup |
| `backup-manager snapshots` | List available snapshots |
| `backup-manager restore` | Restore a snapshot |
| `backup-manager stats` | Display repository statistics |
| `backup-manager check` | Verify repository integrity |
| `backup-manager forget` | Apply retention policy |
| `backup-manager prune` | Optimize repository |

---

# Project status

Current version

**1.0.0**

Current state

**Release Candidate**

The project has successfully passed multiple first-user installation tests and is currently in the final polishing phase before the first public release.

---

# Roadmap

Planned features for Version 1.1

- Multiple backup targets (USB / NAS)
- Interactive folder selection during setup
- Interactive backup target selection
- Service based application architecture
- Internationalization (German / English)
- Recovery concept for forgotten repository passwords
- Display a clear warning during setup that the repository password cannot be recovered and must be stored in a safe place.

---

# Documentation

Detailed documentation is available in the `docs/` directory.

The documentation includes:

- Installation Guide
- User Guide
- Configuration Reference
- Restore Guide
- FAQ

---

## Disclaimer

Linux Backup Manager is provided **"as is"**, without any express or implied warranty.

Although every effort has been made to provide reliable software, no guarantee is given that the software is free of defects or suitable for every use case.

Users are responsible for verifying their backups and regularly testing restore procedures.

The author assumes no liability for data loss or other damages resulting from the use of this software.


# License

This project is released under the MIT License.