# Linux Backup Manager

# Configuration Reference

**Version:** 1.0.1

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
  host_name: blackpanther

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

checks:
  restic_check_interval_days: 30

notifications:
  notify_on_success: false
  notify_on_error: true
```

---

# Configuration Sections

## system

General system information.

| Option      | Description                   |
| ----------- | ----------------------------- |
| `host_name` | Name of the current computer. |

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

## checks

Repository maintenance settings.

| Option                       | Description                                   |
| ---------------------------- | --------------------------------------------- |
| `restic_check_interval_days` | Interval between repository integrity checks. |

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

## notifications

Controls optional notifications.

| Option              | Description                      |
| ------------------- | -------------------------------- |
| `notify_on_success` | Notify after successful backups. |
| `notify_on_error`   | Notify when errors occur.        |

---

# Notes

The setup wizard creates this file automatically and can update its main operational settings.

Manual editing should normally be necessary only for retention and other advanced settings that
the setup wizard does not expose.

Duplicate YAML keys are rejected because silently overwritten settings could select unintended
backup paths or destinations.

---

Linux Backup Manager Documentation

Version 1.0.1
