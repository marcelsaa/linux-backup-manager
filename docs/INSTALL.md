# Linux Backup Manager

# Installation Guide

**Version:** 1.0.0

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
backup-manager 1.0.0
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
* creates the password file
* checks required software
* detects the configured USB backup drive
* initializes the Restic repository if necessary

The setup wizard can safely be executed multiple times.

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

Version 1.0.0
