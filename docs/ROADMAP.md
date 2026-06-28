# Linux Backup Manager

# Project Roadmap

**Last updated:** Version 1.0.0

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

---

# Version 1.1

## Architecture

* [x] Refactor the Application class into dedicated services
* [x] BackupService
* [x] RestoreService
* [x] SetupService
* [x] HealthService
* [x] RepositoryMaintenanceService
* Central exception handling

---

## Backup

* Multiple backup targets
* USB + NAS support
* Parallel backup destinations
* Interactive backup target selection

---

## Configuration

* [x] Interactive folder selection during setup
* Interactive backup destination selection
* Detection of duplicate YAML keys

---

## Restore

* Recovery information
* Recovery concept for forgotten repository passwords
* Optional recovery sheet
* Display a clear warning during setup that the repository password cannot be recovered and must be stored in a safe place.

---

## Internationalization

* English and German documentation
* Switchable application language
* Consistent CLI terminology

---

## Development

* Optional development dependencies
* Improved testing
* Continuous integration

---

# Version 1.2

## User Experience

* Interactive configuration menus
* Configuration import/export
* Repository migration
* Improved diagnostics

---

## Documentation

* Complete German documentation
* User tutorials
* Additional examples

---

# Long-Term Goals

The long-term objective is to provide a dependable backup solution that can be installed and operated by Linux users without requiring detailed knowledge of Restic.

Every release should improve usability without compromising reliability.

---

Linux Backup Manager Documentation

Version 1.0.0
