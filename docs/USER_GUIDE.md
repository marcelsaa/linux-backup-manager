# Linux Backup Manager

# User Guide

**Version:** 1.0.0

---

# Introduction

The Linux Backup Manager (LBM) provides a consistent command-line interface for creating, maintaining and restoring backups.

This guide explains every available command, when it should be used and what can be expected during execution.

Before using any command except `setup`, make sure the initial setup has been completed successfully.

---

# Command Overview

| Command     | Purpose                                                |
| ----------- | ------------------------------------------------------ |
| `setup`     | Configure Linux Backup Manager                         |
| `status`    | Display current configuration and system status        |
| `health`    | Perform system health checks                           |
| `backup`    | Create a new backup                                    |
| `snapshots` | Display available snapshots                            |
| `restore`   | Restore files from a snapshot                          |
| `stats`     | Show repository statistics                             |
| `check`     | Verify repository integrity                            |
| `forget`    | Remove old snapshots according to the retention policy |
| `prune`     | Remove unreferenced repository data                    |

---

# setup

## Purpose

The setup wizard prepares Linux Backup Manager for first use.

It creates all required files and verifies that the system is ready for creating backups.

## Command

```bash
backup-manager setup
```

## What the setup wizard does

During execution the wizard performs the following tasks:

* Creates the configuration directory
* Creates the configuration file
* Creates the password file
* Lets the user select USB, NAS or both backup destinations
* Configures target-specific labels, mount paths and repository paths
* Verifies the required software
* Detects every configured backup destination
* Checks every configured Restic repository
* Creates missing repositories if requested

The setup wizard can safely be executed multiple times.

---

# status

## Purpose

Displays the current configuration and reports the detected system state.

## Command

```bash
backup-manager status
```

Use this command whenever you want to verify that the application has been configured correctly.

---

# health

## Purpose

Performs a complete health check of the backup environment.

## Command

```bash
backup-manager health
```

Typical checks include:

* Configuration
* Password file
* USB device
* Restic repository
* Required software

Running the health check regularly is recommended.

---

# backup

## Purpose

Creates a new Restic backup using the configured backup paths.

## Command

```bash
backup-manager backup
```

The backup process only stores changed data.

Restic automatically performs deduplication.

---

# snapshots

## Purpose

Displays all snapshots currently stored inside the repository.

## Command

```bash
backup-manager snapshots
```

Snapshots represent restore points that can later be restored.

---

# restore

## Purpose

Restore files from a selected snapshot.

## Command

```bash
backup-manager restore
```

The restore command guides the user through the restore process.

For safety reasons, restoring into a separate directory is recommended.

---

# stats

## Purpose

Display repository statistics.

## Command

```bash
backup-manager stats
```

Typical information includes:

* Number of snapshots
* First and latest snapshot timestamp
* Host of the latest snapshot

---

# check

## Purpose

Verify repository integrity.

## Command

```bash
backup-manager check
```

Running repository checks regularly helps detecting damaged repositories before a restore becomes necessary.

---

# forget

## Purpose

Remove snapshots according to the configured retention policy.

## Command

```bash
backup-manager forget
```

Only snapshots outside the configured retention policy are removed.

---

# prune

## Purpose

Remove unused repository data.

## Command

```bash
backup-manager prune
```

This command should normally be executed after `forget`.

---

# Recommended Workflow

The following workflow is recommended for regular usage.

1. Run the setup wizard once.
2. Perform regular backups.
3. Verify repository health.
4. Apply the retention policy.
5. Prune the repository.
6. Test restores regularly.

---

Linux Backup Manager Documentation

Version 1.0.0
