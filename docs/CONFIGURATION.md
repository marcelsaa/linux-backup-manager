# Linux Backup Manager

# Configuration Reference

**Version:** 1.0.0

---

# Introduction

The Linux Backup Manager stores its configuration in a YAML file.

Default location:

```text
~/.config/linux-backup-manager/config.yaml
```

The configuration file is automatically created by the setup wizard during the first installation.

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

timeshift:
  enabled: true
  interval_days: 7

retention:
  keep_daily: 14
  keep_weekly: 8
  keep_monthly: 12
  keep_yearly: 3

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

### usb

| Option            | Description                                                  |
| ----------------- | ------------------------------------------------------------ |
| `enabled`         | Enables USB backups.                                         |
| `label`           | Expected filesystem label of the USB drive.                  |
| `repository_path` | Relative path of the Restic repository on the backup device. |

---

## timeshift

Controls automatic Timeshift snapshot creation.

| Option          | Description                               |
| --------------- | ----------------------------------------- |
| `enabled`       | Enable or disable Timeshift integration.  |
| `interval_days` | Minimum number of days between snapshots. |

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

## notifications

Controls optional notifications.

| Option              | Description                      |
| ------------------- | -------------------------------- |
| `notify_on_success` | Notify after successful backups. |
| `notify_on_error`   | Notify when errors occur.        |

---

# Notes

The setup wizard creates this file automatically.

Editing the configuration manually should only be necessary when changing backup paths, retention settings or backup targets.

---

Linux Backup Manager Documentation

Version 1.0.0
