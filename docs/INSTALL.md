# Linux Backup Manager

# Installation Guide

**Version:** 1.1.0

---

## 1. Introduction

This guide explains how to install and configure the Linux Backup Manager (LBM) on a Linux system.

The installation process has been designed to require only a few steps. After installing the required software, the integrated setup wizard guides you through the initial configuration.

No manual editing of configuration files is required.

---

## 2. System Requirements

The Linux Backup Manager has been developed and tested on modern Linux distributions.

### Minimum Requirements

* Linux
* Python 3.12 or newer
* Restic
* systemd with user services for optional automatic backups

### Recommended

* USB storage device for backups
* Administrative privileges for software installation

---

## 3. Required Software

Before installing LBM, verify that the required software is available.

### Python

```bash
python3 --version
```

Python 3.12 or newer is required.

### Restic

```bash
restic version
```

If one of these commands is not available, install the missing software using your Linux distribution's package manager.

---

## 4. Managed Installation or Upgrade

Place `installer.py` next to the release wheel. Use the exact SHA-256 published with that wheel.
First run the write-free detection and preflight:

```bash
python3 installer.py linux_backup_manager-1.1.0-py3-none-any.whl \
  --sha256 <PUBLISHED_SHA256> --dry-run
```

The preflight checks Python, Restic, free space, installation permissions and, for a Version 1.0.1
upgrade, every configured target and repository. If it passes, run the same command without
`--dry-run`. The installer asks for confirmation; automation may explicitly add `--yes`.

The managed path either creates a fresh versioned installation or upgrades the supported Version
1.0.1 user installation. It preserves the old venv, configuration, password file and repository.
An ambiguous, partial or unsupported installation is refused without changes.

After a failed cutover, the installer automatically restores and verifies the old launcher, units,
exact timer states, configuration, password metadata and logical repository state. A critical
rollback warning means the retained recovery directory must be inspected before continuing.

For a fresh installation, run `backup-manager setup` after the installer completes. Never run setup
over a supported existing Version 1.0.1 configuration merely to perform an upgrade.

### Development Installation

Obtain the source archive or clone the project repository, then change into the project directory.

```bash
cd linux-backup-manager
```

Install the project.

```bash
pip install .
```

Installation only takes a few seconds.

For development, install the optional quality-assurance tools:

```bash
pip install ".[dev]"
```

---

## 5. Verify the Installation

Verify that the installation completed successfully.

```bash
backup-manager --version
```

Expected output:

```text
backup-manager 1.1.0
```

---

## 6. Running the Setup Wizard

Start the interactive setup wizard.

```bash
backup-manager setup
```

During setup, LBM automatically:

* creates the configuration directory
* creates the configuration file
* asks for the application language (`de` or `en`)
* offers safe interactive reconfiguration when the file already exists
* creates the password file
* requires acknowledgement that the repository password cannot be recovered
* checks required software
* detects the configured USB backup drive
* initializes the Restic repository if necessary
* installs user-level systemd timers when automatic backups are enabled

The setup wizard can safely be executed multiple times. Before changing an existing configuration,
it stores the previous file as `config.yaml.bak`. Existing repositories with an invalid password
are reported and are never reinitialized.

After setup, review the recovery-critical paths and store a protected password copy separately:

```bash
backup-manager recovery-info
```

Optionally create a password-free recovery sheet and store it separately:

```bash
backup-manager recovery-sheet
```

Run the read-only system diagnosis after setup:

```bash
backup-manager doctor
```

Resolve every reported error before relying on automatic backups. The command only checks the
environment and never repairs or changes it.

---

## 7. First Backup

Create your first backup.

```bash
backup-manager backup
```

List available snapshots.

```bash
backup-manager snapshots
```

---

## 8. Verify the Repository

Run a repository integrity check.

```bash
backup-manager check
```

Regular repository checks are recommended.

---

## 9. Next Steps

After the installation has completed successfully, continue with the **User Guide** for a detailed explanation of all available commands and configuration options.

---

Linux Backup Manager Documentation

Version 1.1.0
