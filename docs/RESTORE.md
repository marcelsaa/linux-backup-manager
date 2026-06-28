# Linux Backup Manager

# Restore Guide

**Version:** 1.0.1

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

Running a repository check before restoring is recommended.

```bash
backup-manager check
```

---

# Starting a Restore

Start the restore wizard.

```bash
backup-manager restore
```

The restore command guides you through the complete restore process.

---

# Selecting a Snapshot

A snapshot represents the state of your files at a specific point in time.

The restore wizard displays all available snapshots.

Select the snapshot you want to restore.

---

# Choosing a Restore Destination

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

After the restore has completed:

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

# Summary

A backup should never be considered successful until a restore has been tested.

Regular restore tests are the best way to ensure that valuable data can actually be recovered.

---

Linux Backup Manager Documentation

Version 1.0.1
