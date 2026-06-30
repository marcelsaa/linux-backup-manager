# Linux Backup Manager

# Project Roadmap

**Last updated:** Version 1.1.0-rc3 development / Design decisions added June 2026

---

# Vision

The Linux Backup Manager aims to provide a reliable, easy-to-use backup solution for Linux systems.

The focus of the project is:

* Reliability
* Simplicity
* Predictable behaviour
* Minimal administration
* Long-term maintainability

---

# Design Philosophy

These principles are binding for all future versions. They take precedence over individual feature
requests and must be considered in every design review before new functionality is planned or
accepted into a sprint.

## Scope

Linux Backup Manager is **not a comprehensive Restic frontend**. It is a simple, guided backup tool
for private home users who do not need detailed knowledge of Restic. Complex or rarely needed
operations are deliberately separated from everyday use.

## Guiding Principle

Before introducing any new function, answer the following question:

> Does a normal user need this function on a regular basis?

If the answer is **No**, the function belongs in the **Administration** area or does not belong in
the standard interface at all.

## Planned Main Menu Structure

The main menu shall remain as small as possible and contain only regularly used functions:

1. Start backup
2. Restore files
3. Status
4. Settings
5. Administration
6. Quit

New functions shall only appear in the main menu if a normal user genuinely needs them on a regular
basis.

## Administration Area

Rarely needed diagnostic and maintenance functions belong in a dedicated Administration submenu.
Planned entries include:

- Repository integrity check
- Doctor (system diagnostics)
- View log files
- Backup history
- Repository information
- Future expert functions

## Doctor

Doctor remains part of the project as an **administration tool**, not an everyday function. It shall
live in the Administration area, not in the main menu. Doctor shall check at minimum:

- Repository reachable
- Password file present and permissions correct
- USB drive reachable
- Configuration valid
- Restic installed
- Required systemd services and timers present
- Write permissions for all backup destinations
- Further consistency checks as the project evolves

## Snapshot Restoration via Mount

Future versions shall support browsing and selectively restoring individual files from a snapshot
without requiring knowledge of Restic commands. Planned flow:

1. User selects "Restore files".
2. All available snapshots are listed.
3. User selects a snapshot.
4. The snapshot is mounted read-only (FUSE).
5. The file manager opens automatically.
6. The user browses files and directories and copies or drags out the desired files.
7. Modifications inside the mounted snapshot are not possible.
8. The user cleanly unmounts the snapshot when done.

The user shall not need to know any Restic command or option.

## Retention Design

Linux Backup Manager uses Restic's retention system exclusively. There are **no different snapshot
types**. Every snapshot is technically identical; retention rules decide only which snapshots are
kept long-term. A single snapshot can simultaneously satisfy daily, weekly, monthly and yearly
retention categories. No conversion or re-creation of snapshots takes place.

Planned default values:

| Policy | Value |
|---|---|
| keep_daily | 14 |
| keep_weekly | 8 |
| keep_monthly | 12 |
| keep_yearly | 3 |

## Automatic Repository Cleanup

Restic operates internally with `forget` and `prune`. Linux Backup Manager shall hide this
complexity from the user. The standard post-backup flow is:

1. Create backup
2. Apply retention policy (`forget`)
3. Clean repository (`prune`)

The user receives only a clear status message. A configuration option (e.g. run `prune` weekly
only) may be added later as an expert setting in the Administration area.

## No "Full Backup" Menu Item

A "Create full backup" option is **not planned** because Restic fundamentally creates complete
snapshots on every run. If a complete repository reset is ever useful (archiving, target
migration), it shall appear only as an expert function in the Administration area — never in the
main menu.

---

# Version 1.0

## Initial Release

### Core Features

* USB backups using Restic
* Interactive setup wizard
* Automatic configuration generation
* Password management
* Repository initialization
* Backup creation
* Snapshot management
* Restore workflow
* Repository statistics
* Repository integrity checks
* Retention management
* Colored console output
* Comprehensive error handling
* First-user setup workflow
* Documentation

Status:

**Completed**

## Release Stabilization

* [x] Packaging metadata and build configuration
* [x] Wheel and source-distribution build
* [x] Fresh virtual-environment installation
* [x] TestPyPI upload and clean installation
* [x] TestPyPI revalidation of automatic backups with `1.0.1rc1`
* [x] Local private-release preparation for `1.0.1` without a package-index upload
* [x] Physical USB backup and restore validation on the production workstation
* [x] CLI exit-code validation
* [x] User-selectable restore destination
* [x] NAS-only health checks
* [x] Documentation and feature-claim audit

Status: **Version 1.0.1 approved for private local production use after a successful physical USB
backup and byte-identical restore. Regular restore validation remains an operational requirement.**

---

# Version 1.1

## Architecture

* [x] Refactor the Application class into dedicated services
* [x] BackupService
* [x] RestoreService
* [x] SetupService
* [x] HealthService
* [x] RepositoryMaintenanceService
* [x] Central exception handling

---

## Backup

* [x] Multiple backup targets
* [x] USB + NAS support
* [x] Parallel backup destinations
* [x] Interactive backup target selection

---

## Configuration

* [x] Interactive folder selection during setup
* [x] Interactive backup destination selection
* [x] Interactive editing of existing configurations with automatic backup
* [x] Detection of duplicate YAML keys
* [x] Distinct diagnostics for missing repositories and invalid passwords

---

## Recovery and Password Safety

* [x] Password-safe `recovery-info` command
* [x] Recovery concept for password loss and system replacement
* [x] Explicit setup warning that repository passwords cannot be recovered
* [x] Guidance for separate, protected password-file storage
* [x] Optional recovery sheet without automatic password inclusion

---

## Internationalization

* [x] Central `LanguageService` and packaged YAML message catalogs
* [x] Persisted German/English language selection with fallback
* [x] Complete `status`, `doctor`, `health` and `setup` CLI migration
* [x] Backup, restore, maintenance, recovery and schedule command migration
* [x] Consistent translated CLI terminology and generated recovery sheets
* [ ] Complete German and English documentation

---

## Diagnostics

* [x] Initial read-only `backup-manager doctor` self-test command
* [x] Combined configuration, password-permission, Restic, target and repository diagnostics
* [x] Last successful backup timestamp
* [ ] systemd timer diagnostics
* [ ] Last-backup age and optional last-restore-test status

---

## Development

* [x] Optional development dependencies
* [x] Automated test, lint and package-build quality gate
* [x] Continuous integration for `main`, `develop` and pull requests

## 1.1 Release Candidate Stabilization

* [x] Changelog, roadmap and documentation claim audit
* [x] German and English catalog parity
* [x] Python 3.12 local CI reproduction
* [x] Wheel and source-distribution metadata validation
* [x] Fresh installation from the generated wheel
* [x] Isolated German and English backup-and-restore end-to-end tests
* [x] Complete local CI quality gate on the final stabilization state
* [x] Build and freshly install the local `1.1.0rc1` artifacts

Status: **The Version 1.1 local build and fresh-installation gate passed for `1.1.0rc1`. This gate
did not by itself approve migration; the separate migration gate subsequently passed in Sprint 42.**

## Sprint 42 – Restore Finalization

* [x] Reproduce and fully analyze the `lchown` restore failure with absolute backup paths
* [x] Determine whether Restic correctly reports a failed restore or whether Linux Backup Manager
  must interpret the result differently
* [x] Define and implement the smallest correct fix only after the ownership and exit-code semantics
  are proven
* [x] Add regression coverage for restored file content, metadata handling and CLI exit status
* [x] Rebuild the release candidate wheel and record its SHA-256 checksum
* [x] Repeat the complete isolated German and English First-User Validation from the wheel
* [x] Approve migration from Version 1.0.1 only when the final validation report passes without
  exceptions

Status: **Passed. Version 1.1.0rc1 is approved for migration from Version 1.0.1 after the complete
Sprint 42 First-User Revalidation.**

## Sprint 43 – Setup Target Validation Hardening

* [x] Validate selected USB and NAS targets during interactive configuration, before creating the
  password file or proceeding with repository setup
* [x] Keep the interactive wizard open after an unavailable target or invalid target path and let
  the user correct the selection
* [x] Show backup paths, selected targets and schedule in a final setup summary and require
  confirmation before writing the configuration
* [x] Populate or explicitly ask for the real host name during first-user setup instead of
  retaining the example value `blackpanther`; verify status and recovery-sheet host identity
* [x] Do not install or start systemd user timers until at least one configured repository is
  available and initialized
* [x] Define and test first-install catch-up semantics so enabling the due timer cannot create an
  unexpected extra snapshot during setup and acceptance testing
* [x] Add German and English regression coverage for unavailable USB targets, invalid NAS paths,
  corrected target input and scheduler suppression after incomplete setup
* [x] Treat EOF on interactive setup and restore prompts as a localized, controlled cancellation
  instead of exposing a Python traceback
* [ ] Repeat the complete fresh-wheel User Acceptance Test after the fix

Status: **Passed. Version 1.1.0rc2 passed implementation, local artifact validation and independent
German and English external UAT.**

Validation update: **Both `1.1.0rc2` external UAT language passes completed without workaround or
unresolved finding. Version 1.1.0rc2 is approved for migration from Version 1.0.1.**

Current release status: **Version 1.1.0rc1 failed external acceptance and remains rejected. Its
replacement Version 1.1.0rc2 passed Sprint 43 and is approved for migration from Version 1.0.1.**

## Release Candidate Policy

* [x] Feature freeze begins with `1.1.0rc1`
* [ ] Apply only bug fixes, documentation and translation corrections
* [x] Build `1.1.0rc2` because Sprint 43 fixes require another validation cycle
* [x] Accept `1.1.0rc3` after managed fresh-install and Version 1.0.1 upgrade UAT
* [ ] Release Version 1.1.0
* [ ] Begin Version 1.2 development after the Version 1.1.0 release

## Sprint 44 – Managed Installation and Upgrade

* [x] Detect fresh, Version 1.0.1, current and partial installations
* [x] Verify wheel identity and SHA-256 before installation
* [x] Run write-free storage, Python, Restic, permission and repository preflight checks
* [x] Install into versioned virtual environments with atomic launcher cutover
* [x] Preserve configuration, password permissions, systemd units and old venv rollback
* [x] Restore and verify the exact operational state after an injected cutover failure
* [x] Validate fresh install, real 1.0.1 upgrade, idempotency and post-upgrade restore

Status: **Passed. External VM UAT passed for German fresh install, German 1.0.1 upgrade and English
fresh install. Version 1.1.0rc3 is approved for migration from Version 1.0.1.**

## Automation

* [x] systemd user service and timer installation
* [x] User-selectable backup time and interval
* [x] Default daily backup at 20:00
* [x] Startup catch-up backup after the selected interval
* [x] Persistent last-success state

---

# Version 1.2

## User Experience

* [ ] Interactive configuration menus
* [ ] Configuration import/export
* [ ] Repository migration
* [ ] Improved diagnostic presentation
* [ ] Apply default retention values (keep_daily: 14, keep_weekly: 8, keep_monthly: 12, keep_yearly: 3) during setup
* [ ] Automatic forget and prune after every successful backup (hidden from the user)

## Desktop Integration

At the end of installation, the installer shall optionally create a desktop shortcut so that users
can launch Linux Backup Manager like any other desktop application without knowing terminal commands.

**Installer prompt (end of fresh install and upgrade):**

> Create desktop shortcut?
> You can start Linux Backup Manager conveniently by double-clicking the shortcut.
> [Yes] [No]

**Shortcut behaviour:**

- Opens the system default terminal emulator
- Launches the installed `lbm` command (not the Python interpreter directly)
- Keeps the terminal window open until the user exits the program
- All status and error messages remain visible

**Implementation:** A standard XDG `.desktop` file at
`~/.local/share/applications/linux-backup-manager.desktop` with `Terminal=true` and
`Exec=lbm`. The launcher command is used, not a hard-coded interpreter path, so the shortcut
remains valid after upgrades.

**Future extension (optional):**

* [ ] Desktop entry creation (`~/.local/share/applications/`)
* [ ] Application menu entry
* [ ] Desktop icon (`~/Desktop/`)

All entries shall be optional and individually selectable.

---

## Security

* [ ] Change the repository password
* [ ] Automatically update the password file after a password change
* [ ] Regenerate the recovery sheet after a password change

---

## Documentation

* [ ] User tutorials
* [ ] Additional examples

---

# Version 1.3

## Restore Experience

* [ ] Snapshot restoration via read-only FUSE mount
* [ ] Automatic file manager launch after mounting a snapshot
* [ ] Clean unmount workflow after file selection
* [ ] No Restic commands visible to the user

## Interaction Model

* [ ] Guided terminal user interface with main menu (6 items, see Design Philosophy)
* [ ] Administration submenu for Doctor, repository check, log viewer, backup history
* [ ] Doctor integrated into Administration area

---

# Long-Term Goals

The long-term objective is to provide a dependable backup solution that can be installed and
operated by Linux users without requiring detailed knowledge of Restic. Every release shall improve
usability without compromising reliability.

The planned interaction model for future major versions is a guided terminal user interface with a
small, stable main menu and a dedicated Administration area for expert functions. The binding design
decisions that govern this evolution are documented in the **Design Philosophy** section above.

---

Linux Backup Manager Documentation

Release Candidate 1.1.0-rc3 development · Stable Version 1.0.1
