# Linux Backup Manager

# Project Roadmap

**Last updated:** Version 1.1.0-dev

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
* [ ] Optional recovery sheet without automatic password inclusion

---

## Internationalization

* [ ] Central language manager and message catalogs
* [ ] Switchable German and English application language
* [ ] Consistent translated CLI terminology
* [ ] Complete German and English documentation

---

## Diagnostics

* [ ] `backup-manager doctor` self-test command
* [ ] Combined Restic, target, repository, timer and permission diagnostics
* [ ] Last-backup age and optional last-restore-test status

---

## Development

* [x] Optional development dependencies
* [x] Automated test, lint and package-build quality gate
* [x] Continuous integration for `main`, `develop` and pull requests

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

## Documentation

* [ ] User tutorials
* [ ] Additional examples

---

# Long-Term Goals

The long-term objective is to provide a dependable backup solution that can be installed and operated by Linux users without requiring detailed knowledge of Restic.

Every release should improve usability without compromising reliability.

---

Linux Backup Manager Documentation

Development Version 1.1.0-dev · Stable Version 1.0.1
