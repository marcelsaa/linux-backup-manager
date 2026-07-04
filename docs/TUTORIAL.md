# Linux Backup Manager

# Tutorials

**[Deutsche Version](de/TUTORIAL.md)**

**Version:** 1.3.0

---

# Introduction

This guide walks through common, real-world tasks step by step. It assumes Linux Backup
Manager is already installed and set up — see `docs/INSTALL.md` if that is not yet the case.
For a complete list of every command and configuration option, see `docs/USER_GUIDE.md` and
`docs/CONFIGURATION.md`.

---

# Tutorial 1: Your First Week

A short walkthrough of what normally happens after the initial setup.

1. **Day 1 — Setup.** `backup-manager setup` asks for the folders to back up, the backup
   destination (USB drive and/or NAS share) and a repository password, then creates the first
   backup automatically if you confirm.
2. **Day 1 — Check the result.** Open the guided main menu (`backup-manager`) and choose
   "Status", or run `backup-manager doctor` for a more detailed, read-only health check.
   Both work without needing to remember any Restic commands.
3. **Every day after that.** If automatic backups were enabled during setup, nothing further
   is required — a systemd timer creates a new backup at the configured time. The main menu
   shows the time of the last successful backup above the menu items every time it opens, so
   a glance is enough to confirm backups are still running.
4. **End of week — spot check.** Run `backup-manager doctor` once. It reports the backup
   targets, the repository, the password file and the automatic-backup timer in one place,
   each marked OK, WARNING or ERROR.

---

# Tutorial 2: Restoring a Single File You Deleted by Accident

The most common restore scenario does not need a full recovery — only one or a few files.

1. Open the guided main menu (`backup-manager`) and choose **"Restore files"** (or run
   `backup-manager mount` directly).
2. Pick the snapshot to browse — usually the most recent one, unless the file was deleted
   further in the past.
3. The snapshot is mounted read-only and, if a file manager is available, opened
   automatically. Browse to the file, then copy or drag it to where you need it.
4. When finished, return to the terminal and press Enter to unmount the snapshot cleanly.

No files inside the mounted snapshot can be modified — this makes it safe to browse without
any risk of accidentally changing the backup itself. See `docs/RESTORE.md` for the full
restore workflow, including restoring an entire snapshot at once.

---

# Tutorial 3: Adding a Second Backup Target

Starting with a single USB drive and adding a NAS share later (or the other way around) is a
common upgrade path.

1. Make sure the new destination is reachable: the USB drive is plugged in and mounted, or the
   NAS share is already mounted at the configured path by the operating system.
2. Open the guided main menu and choose **"Settings"** (or run `backup-manager settings`).
3. Choose the target to enable and confirm. Linux Backup Manager creates the repository on the
   new destination automatically if it does not exist yet.
4. Run `backup-manager backup` once to confirm both destinations now receive a backup in
   parallel, or wait for the next automatic run.

From this point on, every backup goes to every enabled and reachable destination — there is
no separate "primary" and "secondary" target.

---

# Tutorial 4: Moving Existing Backups to a New Drive

Replacing an aging USB drive without starting the backup history over from scratch.

1. Configure the new drive as a backup target (see Tutorial 3) — both the old and the new
   destination need to be enabled and reachable at the same time for this step.
2. Open the guided main menu → **Administration → Expert Functions → "Migrate repository"**
   (or run `backup-manager migrate`), and confirm.
3. All snapshots are copied from the old destination to the new one. This can take a while for
   large repositories — the confirmation prompt exists specifically because of that.
4. Once the copy is confirmed, disable the old destination in **Settings** (or physically
   remove the old drive after double-checking `backup-manager doctor` shows the new
   repository as reachable).

---

# Tutorial 5: If You Ever Forget the Repository Password

There is deliberately no way to recover a forgotten Restic repository password — this is
Restic's own design, not a limitation of Linux Backup Manager. Preparing for this case in
advance costs a few minutes and avoids losing access to every backup later.

1. Run `backup-manager recovery-sheet` once, right after setup. It creates a printable,
   password-free document with everything needed to locate and identify the repository, kept
   at `0600` permissions.
2. Store the actual password somewhere durable and separate from this computer — a password
   manager or a written note in a safe place both work.
3. See `docs/RECOVERY.md` for the complete reasoning and the disaster-recovery steps if access
   is ever lost regardless.

---

Linux Backup Manager Documentation

Version 1.3.0
