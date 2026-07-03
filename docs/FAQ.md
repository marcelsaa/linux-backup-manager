# Linux Backup Manager

# Frequently Asked Questions (FAQ)

**[Deutsche Version](de/FAQ.md)**

**Version:** 1.3.0

---

# General

## Where is the configuration stored?

The configuration file is stored in:

```text
~/.config/linux-backup-manager/config.yaml
```

The file is created automatically during the setup process.

---

## Where is the repository password stored?

The password file is stored in:

```text
~/.config/linux-backup-manager/restic.pass
```

Its file permissions are automatically restricted to the current user.

---

## Can I run the setup wizard more than once?

Yes.

The setup wizard is idempotent and may safely be executed multiple times.

It only creates missing components and verifies the existing installation.

---

# Backup

## Why is my USB drive not detected?

Verify the following:

* The USB drive is connected.
* The filesystem label matches the configuration.
* The drive is mounted.
* The drive is accessible.

Running

```bash
backup-manager doctor
```

reports USB reachability and the repository state without changing either one.

---

## Can I use multiple USB drives?

Not simultaneously as two independent USB targets. Only one USB target can be configured at
a time. See `docs/ROADMAP.md` for planned work in this area.

---

## Can I use a NAS?

Yes. NAS backups to a mounted network share are supported alongside USB, and both run in
parallel when enabled. See `docs/CONFIGURATION.md` for the `targets.nas` configuration
options.

---

# Restore

## I forgot my repository password.

Without the correct repository password, the backup repository cannot be accessed.

The password cannot be reset by Linux Backup Manager, Restic or the project developers. Restore a
protected copy of the password or password file. If no valid copy exists, the encrypted repository
cannot be recovered.

Use `backup-manager recovery-info` before an emergency and follow `docs/RECOVERY.md`. Keep the
password copy separate from the repository.

---

## Can I restore individual files?

Yes.

The restore command allows restoring data from individual snapshots.

For safety reasons, restoring into a separate directory is recommended.

---

# Repository

## Should I run repository checks?

Yes.

Regular repository checks help detecting problems before a restore becomes necessary.

Run

```bash
backup-manager check
```

periodically.

---

## When should I use `forget`?

`forget` removes snapshots according to the configured retention policy.

---

## When should I use `prune`?

`prune` removes repository data that is no longer referenced by any snapshot.

Normally it is executed after `forget`.

---

# Future Features

See `docs/ROADMAP.md` for completed and planned work.

---

Linux Backup Manager Documentation

Version 1.3.0
