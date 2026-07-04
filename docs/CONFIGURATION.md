# Linux Backup Manager

# Configuration Reference

**[Deutsche Version](de/CONFIGURATION.md)**

**Version:** 1.3.2

---

# Introduction

The Linux Backup Manager stores its configuration in a YAML file.

Default location:

```text
~/.config/linux-backup-manager/config.yaml
```

The configuration file is automatically created by the setup wizard during the first installation.
On later runs, the wizard can update backup folders, destinations and scheduling settings. It saves
the previous version as `config.yaml.bak` before replacing it.

Manual editing is possible but normally not required.

---

# Complete Configuration

```yaml
system:
  host_name: my-linux-pc
  language: de

paths:
  log_dir: logs
  state_dir: state
  password_file: ~/.config/linux-backup-manager/restic.pass

backup:
  paths:
    - ~/Documents
    - ~/Pictures

  excludes:
    - ~/.cache

targets:
  usb:
    enabled: true
    label: LinuxBackup
    repository_path: restic/linux-mint

  nas:
    enabled: false
    mount_path: /mnt/backup-nas
    repository_path: restic/linux-mint

retention:
  keep_daily: 14
  keep_weekly: 8
  keep_monthly: 12
  keep_yearly: 3

schedule:
  enabled: true
  daily_time: "20:00"
  interval_days: 1
  boot_delay_minutes: 2

```

---

# Configuration Sections

## system

General system information.

| Option      | Description                                              |
| ----------- | -------------------------------------------------------- |
| `host_name` | Name of the current computer.                            |
| `language`  | Application language: `de` or `en`; defaults to `de`.    |

---

## paths

Defines internal directories used by Linux Backup Manager.

| Option          | Description                                 |
| --------------- | ------------------------------------------- |
| `log_dir`       | Directory used for log files.               |
| `state_dir`     | Directory used for application state.       |
| `password_file` | Location of the Restic repository password. |

---

## backup

Defines which files and directories are backed up.

### paths

List of directories included in every backup.

### excludes

List of excluded files and directories.

Exclude patterns support wildcards where supported by Restic.

---

## targets

Defines backup destinations.

All enabled and available destinations receive a backup. USB and NAS backups run in parallel.

### usb

| Option            | Description                                                  |
| ----------------- | ------------------------------------------------------------ |
| `enabled`         | Enables USB backups.                                         |
| `label`           | Expected filesystem label of the USB drive.                  |
| `repository_path` | Relative path of the Restic repository on the backup device. |

### nas

NAS support expects the network share to be mounted by the operating system.

| Option            | Description                                             |
| ----------------- | ------------------------------------------------------- |
| `enabled`         | Enables backups to the mounted NAS share.               |
| `mount_path`      | Local mount point of the NAS share.                      |
| `repository_path` | Relative path of the Restic repository on the NAS share. |

---

## retention

Retention policy for repository snapshots.

| Option         | Description                |
| -------------- | -------------------------- |
| `keep_daily`   | Daily snapshots to keep.   |
| `keep_weekly`  | Weekly snapshots to keep.  |
| `keep_monthly` | Monthly snapshots to keep. |
| `keep_yearly`  | Yearly snapshots to keep.  |

---

## schedule

Controls automatic backups through systemd user timers.

| Option                  | Description                                             |
| ----------------------- | ------------------------------------------------------- |
| `enabled`               | Install automatic backups during interactive setup.     |
| `daily_time`            | Time at which the interval is checked.                  |
| `interval_days`         | Number of days between successful backups.              |
| `boot_delay_minutes`    | Delay before checking after system/user-manager start.  |

The timer checks the chosen interval at 20:00 by default. Both time and interval are selected
during setup and may be edited later. A second timer starts shortly after boot or login and
creates a catch-up backup when no successful backup is known or the selected interval has been
exceeded. Failed or incomplete multi-destination backups do not update the success timestamp.

---

# Examples

The setup wizard and the `settings` menu cover every option below interactively — manual
editing is never required. These examples illustrate a few common scenarios for reference.
See `docs/TUTORIAL.md` for step-by-step walkthroughs of moving between these scenarios.

## Single USB drive (the default scenario)

```yaml
targets:
  usb:
    enabled: true
    label: LinuxBackup
    repository_path: restic/production
  nas:
    enabled: false
    mount_path: /mnt/backup-nas
    repository_path: restic/production
```

## USB drive and NAS share in parallel

Both destinations receive every backup; there is no primary/secondary distinction.

```yaml
targets:
  usb:
    enabled: true
    label: LinuxBackup
    repository_path: restic/production
  nas:
    enabled: true
    mount_path: /mnt/backup-nas
    repository_path: restic/production
```

## Development machine with a larger exclude list

Excludes commonly grown source trees and build artifacts in addition to the defaults.

```yaml
backup:
  paths:
    - ~/Projects
    - ~/Documents
  excludes:
    - ~/.cache
    - ~/Projects/*/node_modules
    - ~/Projects/*/.venv
    - ~/Projects/*/target
    - ~/Projects/*/build
```

## Conservative retention for limited storage space

Keeps fewer historical snapshots than the default, trading recovery depth for space.

```yaml
retention:
  keep_daily: 7
  keep_weekly: 4
  keep_monthly: 3
  keep_yearly: 1
```

---

# Notes

The setup wizard creates this file automatically and can update its main operational settings.

Manual editing should normally be necessary only for retention and other advanced settings that
the setup wizard does not expose.

Duplicate YAML keys are rejected because silently overwritten settings could select unintended
backup paths or destinations.

---

Linux Backup Manager Documentation

Version 1.3.2
