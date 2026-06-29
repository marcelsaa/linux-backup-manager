# Linux Backup Manager

# Project Roadmap

**Last updated:** Version 1.1.0-rc1

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

## Release Candidate Policy

* [x] Feature freeze begins with `1.1.0rc1`
* [ ] Apply only bug fixes, documentation and translation corrections
* [ ] Build `1.1.0rc2` only if candidate changes require another validation cycle
* [ ] Release Version 1.1.0
* [ ] Begin Version 1.2 development after the Version 1.1.0 release

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

# Long-Term Goals

The long-term objective is to provide a dependable backup solution that can be installed and operated by Linux users without requiring detailed knowledge of Restic.

Every release should improve usability without compromising reliability.

---

Linux Backup Manager Documentation

Release Candidate 1.1.0-rc1 · Stable Version 1.0.1
