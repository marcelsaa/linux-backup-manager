# Automatic Backups with systemd

**[Deutsche Version](de/SYSTEMD.md)**

Linux Backup Manager uses systemd user timers. No permanently running backup process is needed.

## Behavior

Two independent timers are installed:

* The scheduled timer checks the configured interval at the user-selected time. The default is
  every day at 20:00.
* The startup timer runs shortly after boot or user login. It immediately starts a backup when
  the selected interval since the last fully successful backup has elapsed.

Only a backup that succeeds for every enabled destination updates the last-success timestamp.

## Commands

```bash
backup-manager schedule-install
backup-manager schedule-status
backup-manager schedule-remove
```

The unit files are stored below:

```text
~/.config/systemd/user/
```

## Diagnostics

Display active timers:

```bash
systemctl --user list-timers 'linux-backup-manager-*'
```

Display recent logs:

```bash
journalctl --user -u linux-backup-manager-daily.service
journalctl --user -u linux-backup-manager-due.service
```

The user-level systemd manager normally starts at login. Backup drives and NAS mounts must be
available to the user when the backup begins. Systems that must run backups without an interactive
login require separately configured user lingering and system-level mount availability.
