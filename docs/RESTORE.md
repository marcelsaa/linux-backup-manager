# Linux Backup Manager

# Restore Guide

**[Deutsche Version](de/RESTORE.md)**

**Version:** 1.3.2

---

# Introduction

Creating backups is only one half of a successful backup strategy.

The ability to restore data quickly and reliably is equally important.

This guide explains how to restore data from a Restic repository managed by Linux Backup Manager.

---

# Before You Begin

Before starting a restore operation, verify the following:

* The backup repository is available.
* The USB backup drive is connected.
* The repository password file exists.
* The repository passes an integrity check.

Display recovery-critical paths and target information without exposing the password:

```bash
backup-manager recovery-info
```

Running a repository check before restoring is recommended.

```bash
backup-manager check
```

---

# Choosing a Restore Method

Linux Backup Manager offers two ways to get files back, and both start with the same
snapshot selection step:

* **`mount`** — mounts a snapshot read-only and opens it in a file manager, so individual
  files can be browsed and copied out on demand. Nothing is copied until you copy it
  yourself. This is what the main menu's "Restore files" entry runs, and the right choice
  when you need a handful of files back.
* **`restore`** — copies an entire snapshot into a directory in one step. The right choice
  for full disaster recovery (see `docs/RECOVERY.md`), not for retrieving a few files.
  Reachable from the main menu via Administration → Expert Functions → "Restore a full
  snapshot".

The rest of this guide covers `mount` first, since it is the recommended default, followed
by `restore`.

---

# Mounting a Snapshot (`mount`)

Start it directly, or via the main menu's "Restore files" entry:

```bash
backup-manager mount
```

1. Select the snapshot to browse from the list of available snapshots (see "Selecting a
   Snapshot" below).
2. The snapshot is mounted read-only at a temporary location. The default file manager opens
   automatically at the snapshot's root. If no file manager is found, the mount path is
   printed instead so it can be opened manually.
3. Browse the snapshot like any other folder and copy out whatever files are needed.
4. Press Enter in the terminal when finished. The snapshot is unmounted automatically —
   including if the operation is interrupted with `Ctrl+C`.

No Restic commands or repository internals are shown at any point.

**Requirements:** mounting needs FUSE (`fusermount` or `umount`) on the system; opening the
file manager automatically needs `xdg-open`. Both are standard on desktop Linux
installations.

**Note:** closing the file manager window does *not* trigger the unmount by itself — most
file managers run as a single background process, so there is no reliable way to detect that
one particular window was closed. Press Enter in the terminal instead when done.

---

# Selecting a Snapshot

A snapshot represents the state of your files at a specific point in time.

Both `mount` and `restore` display all available snapshots and ask which one to use.

---

# Restoring a Full Snapshot (`restore`)

Start it directly, or via Administration → Expert Functions → "Restore a full snapshot":

```bash
backup-manager restore
```

The restore command guides you through the complete restore process.

## Choosing a Restore Destination

For safety reasons, files should always be restored into a separate directory.

The restore command asks for a destination and suggests a directory below
`~/lbm-restore/<snapshot-id>`. If the selected directory is not empty, an additional warning must
be confirmed before the restore starts.

Recommended workflow:

* Restore into an empty directory.
* Verify the restored files.
* Copy the required files back to their original location.

This prevents accidental overwriting of existing data.

---

# Verifying Restored Files

After a restore has completed (or after copying files out of a mounted snapshot):

* Verify that all expected files exist.
* Open important documents.
* Check directory structures.
* Verify file permissions if required.

Do not delete old backups until you are certain that the restored data is complete.

---

# Best Practices

A restore should not only be performed after data loss.

Regular test restores help ensure that:

* backups are complete
* the repository is healthy
* the restore procedure is familiar
* recovery works when it is actually needed

Testing restores periodically is considered best practice.

---

# Troubleshooting

## Repository cannot be found

Possible causes:

* USB drive not connected
* Wrong USB label
* Repository moved

---

## Wrong password

The repository password does not match the password used during repository creation.

Without the correct password the repository cannot be accessed.

---

## Damaged repository

Run:

```bash
backup-manager check
```

If errors are reported, repair the repository before attempting another restore.

---

## `mount` reports a mount or file-manager problem

* "Mount failed" usually means FUSE is not available, or the wrong password is configured —
  check the printed error message for details.
* "No file manager found" means `xdg-open` is not installed or no default file manager is
  configured; the mount still succeeded, so the printed path can be opened manually.

---

# Summary

A backup should never be considered successful until a restore has been tested.

Regular restore tests are the best way to ensure that valuable data can actually be recovered.

---

Linux Backup Manager Documentation

Version 1.3.2
