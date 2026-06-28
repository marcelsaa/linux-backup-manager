# Linux Backup Manager

# Frequently Asked Questions (FAQ)

**Version:** 1.1.0-dev

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
backup-manager health
```

usually identifies the problem.

---

## Can I use multiple USB drives?

Not yet.

Support for multiple backup targets is planned for Version 1.1.

---

## Can I use a NAS?

Not yet.

NAS support is part of the Version 1.1 roadmap.

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

The following features are already planned:

* Multiple backup targets
* NAS support
* Interactive backup configuration
* German and English application language
* German documentation

---

Linux Backup Manager Documentation

Development Version 1.1.0-dev
