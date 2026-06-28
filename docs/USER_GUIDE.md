# Linux Backup Manager

# User Guide

**Version:** 1.1.0-dev

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
| `doctor`    | Run comprehensive read-only diagnostics                |
| `recovery-info` | Display password-safe recovery information         |
| `recovery-sheet` | Create a password-free recovery document           |
| `backup`    | Create a new backup                                    |
| `schedule-install` | Install and activate automatic backups           |
| `schedule-status` | Display automatic-backup timer status             |
| `schedule-remove` | Disable and remove automatic-backup timers         |
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
* Selects and stores the application language (`de` or `en`)
* Offers to edit an existing configuration and saves the previous file as `config.yaml.bak`
* Creates the password file
* Lets the user select USB, NAS or both backup destinations
* Configures target-specific labels, mount paths and repository paths
* Verifies the required software
* Detects every configured backup destination
* Checks every configured Restic repository
* Creates missing repositories if requested

The setup wizard can safely be executed multiple times. When a configuration already exists, it
asks whether backup folders, destinations and the automatic schedule should be edited. Declining
keeps the file unchanged. Accepting creates `config.yaml.bak` before the updated file is written.

The language selection and catalog fallback are available as an internationalization foundation.
Most command output remains German until the following translation sprints migrate the existing
messages.

An invalid repository password is reported separately from a missing repository. Setup never
offers to initialize an existing repository that cannot be opened with the configured password.
Before creating a password file, setup requires explicit confirmation that a forgotten repository
password cannot be reset and that a protected copy must be stored separately.

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

# doctor

## Purpose

Runs a single read-only diagnosis for support and self-checks. The command reports:

* whether the configuration can be loaded;
* whether the password file exists and has plausible restrictive permissions;
* whether Restic is installed and executable;
* whether every configured USB or NAS target is reachable and writable;
* whether each reachable Restic repository can be opened;
* the last successfully recorded backup time.

## Command

```bash
backup-manager doctor
```

Results are classified as `OK`, `WARNUNG`, `FEHLER` or `ÜBERSPRUNGEN`. A missing previously
recorded backup is a warning. Configuration, password, Restic, target or repository failures make
the command exit with status 1. Successful checks and warnings exit with status 0.

`doctor` performs no repairs. It does not initialize repositories, create backups, change the
configuration or alter automatic-backup timers.

---

# recovery-info

## Purpose

Displays the paths, repository targets and emergency steps required for recovery without reading or
printing the repository password.

## Command

```bash
backup-manager recovery-info
```

Run this command after setup and whenever the password-file path or repository target changes. Keep
a protected password or password-file copy separate from the repository. See `docs/RECOVERY.md` for
the complete recovery concept.

---

# recovery-sheet

## Purpose

Creates an optional recovery document containing the configured repository targets, important file
paths, emergency commands and blank fields for external recovery records. The document never
contains the repository password.

## Command

```bash
backup-manager recovery-sheet
```

Choose an output path or accept `~/linux-backup-manager-recovery.txt`. Existing files require
explicit overwrite confirmation. The result is written atomically with permissions `0600`.

Print the sheet or copy it to a protected location separate from both the computer and backup
repository. Manually record where the protected password copy is stored; do not write the password
itself into an unprotected sheet.

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

# Automatic Backups

Install or repair the user-level systemd timers with:

```bash
backup-manager schedule-install
```

During setup, the user chooses the time and interval in days. The default is daily at 20:00.
After a restart or login, a second timer checks whether the chosen interval since the last
successful backup has elapsed and immediately catches up when required.

Inspect or remove the timers with:

```bash
backup-manager schedule-status
backup-manager schedule-remove
```

The timers run as the current user and do not require a permanently running LBM process. Backup
targets must be mounted and accessible when a timer fires.

---

Linux Backup Manager Documentation

Development Version 1.1.0-dev
