# Recovery and Password Safety

**Version:** 1.1.0-dev

---

# Purpose

Linux Backup Manager repositories are encrypted by Restic. The repository password is required to
read snapshots or restore files. It cannot be reset or recovered by Linux Backup Manager, Restic,
the project developers or a storage provider.

This recovery concept prevents avoidable password loss and documents the information required to
rebuild a Linux Backup Manager installation after a system failure.

---

# Recovery-Critical Assets

A complete recovery requires three independent assets:

1. The backup repository containing the encrypted snapshots.
2. The repository password or a protected copy of the password file.
3. The configuration or a record of the repository target and backup settings.

Storing the only password copy inside its encrypted repository is not sufficient: the password is
needed before that repository can be opened.

The default local files are:

```text
~/.config/linux-backup-manager/config.yaml
~/.config/linux-backup-manager/restic.pass
```

The password file contains the repository password and normally has mode `0600`.

---

# Recovery Information Command

Display the current recovery metadata with:

```bash
backup-manager recovery-info
```

The command reports:

* configuration and password-file paths;
* password-file presence and permissions;
* configured USB and NAS repository locations;
* a concise emergency restore procedure.

It never opens the password file and never prints the password.

---

# Safe Password Storage

Keep at least one protected password copy separate from the backup repository and the computer being
backed up. Suitable options include:

* a trusted password manager;
* an encrypted offline medium stored separately;
* a sealed paper copy in a physically secure location;
* a protected copy of `restic.pass` on a separate recovery medium.

Avoid:

* committing the password file to Git;
* sending it through unencrypted email or messaging;
* storing an unprotected plaintext copy in general cloud storage;
* keeping the only copy on the same USB drive as the repository;
* placing the password itself in an automatically generated recovery document.

Anyone who obtains both the repository and its password can read the backup contents.

---

# Preparation Checklist

Before relying on a repository:

1. Run `backup-manager recovery-info` and verify all paths and targets.
2. Store the password or password file in a protected, separate location.
3. Store a copy of `config.yaml` or record the target settings.
4. Run `backup-manager check`.
5. Perform and verify a real restore test.
6. Repeat recovery checks whenever the password, target or configuration changes.

---

# Emergency Recovery Procedure

After replacing or reinstalling the computer:

1. Install Python 3.12 or newer, Restic and the appropriate Linux Backup Manager release.
2. Connect and mount the USB or NAS repository.
3. Restore `config.yaml` to `~/.config/linux-backup-manager/config.yaml`.
4. Restore the protected password-file copy to the configured password path.
5. Restrict its permissions:

   ```bash
   chmod 600 ~/.config/linux-backup-manager/restic.pass
   ```

6. Verify access:

   ```bash
   backup-manager health
   backup-manager snapshots
   backup-manager check
   ```

7. Restore into a separate directory:

   ```bash
   backup-manager restore
   ```

8. Compare important restored files with known originals or checksums before copying data back.

If the original configuration is unavailable, recreate it with `backup-manager setup` using the
same repository target and the original password file. Do not initialize or overwrite the existing
repository.

---

# Forgotten Password

If neither the correct password nor a valid copy of the password file exists, the encrypted Restic
repository cannot be opened. There is no password-reset or bypass procedure.

Do not delete the inaccessible repository immediately: another protected password copy may still be
found. Create a new repository with a new securely stored password for future backups, but keep it
separate from the old repository.

---

# Recovery Sheet

Create an optional recovery sheet with:

```bash
backup-manager recovery-sheet
```

The default output is:

```text
~/linux-backup-manager-recovery.txt
```

The command asks before overwriting an existing file and writes the result atomically with mode
`0600`. The sheet contains:

* Linux Backup Manager version, host and creation time;
* configuration and password-file paths;
* USB and NAS repository locations;
* empty fields for the separately stored password copy, configuration copy and last restore test;
* emergency verification and restore commands.

The sheet deliberately does not read or contain the repository password. It is an orientation and
recovery-procedure document, not a password backup. Print it or copy it to a protected location
separate from the computer and repository.

---

Linux Backup Manager Documentation

Development Version 1.1.0-dev
