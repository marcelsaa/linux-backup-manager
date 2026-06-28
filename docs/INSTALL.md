# Linux Backup Manager

# Installation Guide

**Version:** 1.1.0-dev

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

## 4. Installing Linux Backup Manager

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
backup-manager 1.0.1
```

For private use, install the locally built wheel directly instead of uploading it to a package
index:

```bash
python -m pip install dist/linux_backup_manager-1.0.1-py3-none-any.whl
```

Keep the wheel in private storage or distribute it through a private channel. A private GitHub
repository does not make a package uploaded to TestPyPI or PyPI private.

---

## 6. Running the Setup Wizard

Start the interactive setup wizard.

```bash
backup-manager setup
```

During setup, LBM automatically:

* creates the configuration directory
* creates the configuration file
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

Development Version 1.1.0-dev
