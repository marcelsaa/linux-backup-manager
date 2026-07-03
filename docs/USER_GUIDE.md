# Linux Backup Manager

# User Guide

**[Deutsche Version](de/USER_GUIDE.md)**

**Version:** 1.3.0

---

# Introduction

The Linux Backup Manager (LBM) provides a consistent command-line interface for creating, maintaining and restoring backups.

This guide explains every available command, when it should be used and what can be expected during execution.

Before using any command except `setup`, make sure the initial setup has been completed successfully.

---

# Command Overview

| Command     | Purpose                                                |
| ----------- | ------------------------------------------------------ |
| `menu`      | Open the guided main menu (default with no arguments)  |
| `setup`     | Configure Linux Backup Manager                         |
| `settings`  | Change individual settings interactively               |
| `export-config` | Copy the current configuration file to another location |
| `import-config` | Validate and adopt an external configuration file  |
| `status`    | Display current configuration and system status        |
| `health`    | Perform system health checks                           |
| `doctor`    | Run comprehensive read-only diagnostics                |
| `logs`      | View the log file (path and recent entries)            |
| `recovery-info` | Display password-safe recovery information         |
| `recovery-sheet` | Create a password-free recovery document           |
| `change-password` | Change the repository password                   |
| `backup`    | Create a new backup                                    |
| `schedule-install` | Install and activate automatic backups           |
| `schedule-status` | Display automatic-backup timer status             |
| `schedule-remove` | Disable and remove automatic-backup timers         |
| `snapshots` | Display available snapshots                            |
| `restore`   | Restore a full snapshot to a directory (Expert Function) |
| `mount`     | Mount a snapshot read-only and browse it in a file manager (default "Restore files" action) |
| `stats`     | Show repository statistics                             |
| `check`     | Verify repository integrity                            |
| `forget`    | Remove old snapshots according to the retention policy |
| `prune`     | Remove unreferenced repository data                    |
| `migrate`   | Copy all snapshots to another configured target (Expert Function) |

---

# menu

## Purpose

Opens the guided main menu — the default entry point when `backup-manager` is run without a
command (for example from the application-menu shortcut). The menu stays open until you choose
to exit, so multiple actions can be performed in one session.

## Command

```bash
backup-manager
backup-manager menu
```

## Structure

* Run backup
* Restore files
* Status
* Settings
* Administration
  * Doctor (detailed diagnostics)
  * Verify repository
  * View log files
  * Backup history
  * Repository information
  * Expert functions
    * Initialize repository
    * Restore a full snapshot
    * Show snapshot statistics
    * Remove old snapshots
    * Clean up repository
    * Migrate repository
    * Change password
    * Create recovery document
    * Export configuration
    * Import configuration
    * Install / show / remove schedule
* Exit

Every menu entry runs the same command described elsewhere in this guide; the menu is a
convenience layer, not a separate implementation. `backup-manager --non-interactive` (with no
command) runs `status` instead of opening the menu, since the menu requires interactive input.

"Restore files" in the main menu runs `mount` (browse and copy individual files), not the
full-snapshot `restore` command — see the `mount` and `restore` sections below for the
difference.

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
* Validates the availability of each configured target and offers a correction loop for
  unavailable paths, keeping the wizard open until a reachable target is confirmed
* Configures target-specific labels, mount paths and repository paths
* Presents a complete summary of host, backup paths, targets and schedule for confirmation
  before writing any configuration
* Verifies the required software
* Detects every configured backup destination
* Checks every configured Restic repository
* Creates missing repositories if requested

The setup wizard can safely be executed multiple times. When a configuration already exists, it
asks whether backup folders, destinations and the automatic schedule should be edited. Declining
keeps the file unchanged. Accepting creates `config.yaml.bak` before the updated file is written.

The selected language controls all application-generated command output and prompts. Raw output
from external programs such as Restic and systemctl is displayed unchanged.

An invalid repository password is reported separately from a missing repository. Setup never
offers to initialize an existing repository that cannot be opened with the configured password.
Before creating a password file, setup requires explicit confirmation that a forgotten repository
password cannot be reset and that a protected copy must be stored separately.

---

# settings

## Purpose

Opens an interactive menu to change individual settings without running through the entire setup
wizard again.

## Command

```bash
backup-manager settings
```

## Available settings

* Language
* Backup paths
* Backup targets (USB and NAS)
* Automatic-backup schedule

Select a menu entry to change it, or choose the exit option to leave the menu. Every change is
saved atomically before the menu returns, and a `config.yaml.bak` backup of the previous
configuration is created. The menu keeps running until the user chooses to exit, so multiple
settings can be changed in one session.

---

# export-config

## Purpose

Copies the current configuration file to a location chosen by the user, for example to keep an
external backup of the configuration or transfer it to another machine.

## Command

```bash
backup-manager export-config
```

An existing file at the chosen destination is only overwritten after explicit confirmation. The
command reports an error if no configuration exists yet.

---

# import-config

## Purpose

Reads an external configuration file, fully validates it and adopts it as the active
configuration.

## Command

```bash
backup-manager import-config
```

The source file is fully validated before anything is changed. An existing configuration is saved
as `config.yaml.bak` before it is atomically replaced. If the source file is missing or fails
validation, the existing configuration is left untouched.

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

Results are classified with localized labels (`OK`, `Warning`, `Error`, `Skipped` in English;
`OK`, `WARNUNG`, `FEHLER`, `ÜBERSPRUNGEN` in German). A missing previously recorded backup is a
warning. Configuration, password, Restic, target or repository failures make the command exit with
status 1. Successful checks and warnings exit with status 0.

`doctor` performs no repairs. It does not initialize repositories, create backups, change the
configuration or alter automatic-backup timers.

---

# logs

## Purpose

Shows the location of the application log file and its most recent entries, for troubleshooting
without needing to locate the file manually.

## Command

```bash
backup-manager logs
```

Prints the log file path (`~/.local/state/lbm/backup-manager.log`) followed by up to the last 40
lines. If the file does not exist yet or is empty, a message says so instead.

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

# change-password

## Purpose

Changes the repository password across all configured repositories.

## Command

```bash
backup-manager change-password
```

The new password is applied to every configured repository in sequence, and the password file is
replaced atomically only after all repositories succeed. If a repository fails, the already
changed repositories are reported by name and the password file remains unchanged, so no
repository is left inaccessible with the old password file.

After a successful change, the command offers to recreate the recovery sheet, since any previously
created sheet still refers to the old password state.

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

# mount

## Purpose

Mounts a selected snapshot read-only via FUSE and opens it in the default file manager, so
individual files can be browsed and copied out without restoring the entire snapshot first.
This is what the main menu's "Restore files" entry runs, and the recommended way to recover a
small number of files.

## Command

```bash
backup-manager mount
```

## Steps

1. Select a snapshot from the list, exactly as in `restore`.
2. The snapshot is mounted read-only at a temporary location and the file manager opens
   automatically at the snapshot's root (falls back to printing the path if no file manager
   is found).
3. Browse the snapshot like a normal folder and copy out whatever files are needed.
4. Press Enter in the terminal when finished; the snapshot is unmounted automatically.

No Restic commands or repository internals are shown. The mount is always read-only, and it
is unmounted even if the process is interrupted (`Ctrl+C`).

## Requirements

Mounting requires FUSE (`fusermount` or `umount`) to be available on the system; opening the
file manager automatically requires `xdg-open`. Both are common on desktop Linux
installations; if either is missing, `mount` reports a clear message instead of failing
silently.

---

# restore

## Purpose

Restores an entire snapshot into a directory. This is the full, bulk-recovery counterpart to
`mount` — use it to recover everything at once (for example after a full disaster recovery,
see `docs/RECOVERY.md`), not to look for a handful of files. Reachable from the main menu via
Administration → Expert Functions → "Restore a full snapshot".

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

# migrate

## Purpose

Copies all snapshots from one configured backup target to another (for example, from USB to
NAS), using Restic's own `copy` command under the hood. Useful when moving to new storage
without losing backup history. Reachable from Administration → Expert Functions → "Migrate
repository".

## Command

```bash
backup-manager migrate
```

## Requirements

At least two configured, enabled and currently reachable backup targets (see
`docs/CONFIGURATION.md`). With only one reachable target, `migrate` reports that a second
target is needed and stops without making changes.

## Steps

1. Select the source target from the list of available targets.
2. Select the destination target from the remaining targets.
3. Confirm — copying can take a long time depending on how much data is stored, since Restic
   has to both read from the source and write to the destination.
4. If the destination is not yet an initialized Restic repository, it is created
   automatically.
5. All snapshots are copied. Existing snapshots at the destination are left untouched;
   nothing is deleted from the source.

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
After a restart or login, a second timer waits a short fixed delay before checking whether the
chosen interval since the last successful backup has elapsed and immediately catches up when
required. The delay prevents an unexpected extra snapshot when setup and reboot happen on the
same day.

Inspect or remove the timers with:

```bash
backup-manager schedule-status
backup-manager schedule-remove
```

The timers run as the current user and do not require a permanently running LBM process. Backup
targets must be mounted and accessible when a timer fires.

---

Linux Backup Manager Documentation

Version 1.3.0
