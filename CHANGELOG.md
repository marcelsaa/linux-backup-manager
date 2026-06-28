# Changelog

All notable changes to the Linux Backup Manager project are documented in this file.

The project follows Semantic Versioning and keeps a chronological history of all major development milestones.

---

# Unreleased

## Version 1.1.0 Development

### Changed

* Development continues on the `develop` branch while Version 1.0.1 remains stable on `main`
* Package version advanced to the PEP 440 development version `1.1.0.dev0`

## Sprint 34 – Continuous Integration

### Added

* GitHub Actions quality gate for pushes to `main` and `develop`, pull requests and manual runs
* Automated Python 3.12 dependency and byte-compilation checks for source and test files
* Automated Ruff linting and the complete pytest suite
* Automated wheel and source-distribution builds with Twine metadata validation
* Read-only workflow permissions, disabled credential persistence, concurrency cancellation and a
  15-minute job timeout

### Changed

* Added Twine to the optional development dependencies

---

# v1.0.1 – 2026-06-28

## Production Acceptance

### Validated

* Persistent local wheel installation and CLI Version 1.0.1
* Production USB repository initialization at `restic/production`
* Real backup of 6,893 files in snapshot `f78aabcc`
* Repository integrity, statistics and automatic-backup due checks
* Active systemd user timers using the persistent production virtual environment
* Successful restore to the normal user filesystem with byte-identical SHA-256 verification

## Sprint 33 – Private Stable Release Hardening

### Added

* Interactive editing of backup folders, destinations and scheduling in an existing configuration
* Automatic `config.yaml.bak` creation before an existing configuration is replaced
* Explicit repository states for ready, missing, invalid-password and other error conditions

### Changed

* Configuration files are written through an atomic temporary-file replacement
* Repository initialization is offered only when the repository is actually missing
* Version advanced from `1.0.1rc1` to the private-use stable release `1.0.1`

### Fixed

* Existing repositories with an incorrect password are no longer reported as missing
* Setup no longer attempts `restic init` against repositories that already contain a configuration

---

## Sprint 32 – 1.0.1rc1 TestPyPI Revalidation

### Validated

* Version advanced to `1.0.1rc1` after the immutable TestPyPI 1.0.0 publication
* Wheel and source distribution rebuilt from committed release source
* Both artifacts passed `twine check` and were published to TestPyPI
* Clean installation pinned exclusively to TestPyPI succeeded
* Interactive setup accepted a custom 18:30 time and three-day backup interval
* systemd units were generated, enabled through the setup path and accepted by systemd tooling
* Real Restic backup, state persistence, due checks, snapshots, repository check and restore data
  integrity passed

---

## Sprint 31 – Automatic systemd Backups

### Added

* User-selectable backup time and interval in days
* Daily systemd user timer checking the configured interval at the selected time
* Startup timer checking shortly after boot/login whether the selected interval was exceeded
* Persistent timestamp for the last fully successful backup
* `backup-if-due`, `schedule-install`, `schedule-status` and `schedule-remove` commands
* Automatic timer installation during first-user setup

### Changed

* Backup commands now return failure when a configured destination is unavailable or fails
* Only fully successful multi-destination backups update the success timestamp
* Status output includes automation settings and the last successful backup

---

## Sprint 30 – TestPyPI Release Validation

### Validated

* Wheel and source distribution uploaded successfully to TestPyPI
* Installation performed exclusively from TestPyPI in a fresh virtual environment
* Runtime dependencies installed separately from production PyPI
* Console entry point, version, help, package resources and dependency integrity verified
* Interactive first-user setup completed from the TestPyPI installation
* NAS repository initialized and a real Restic backup created successfully
* Health check, snapshot listing and repository integrity check passed

---

## Sprint 29 – Release Stabilization

### Added

* Complete package metadata, build backend and source-distribution manifest
* Optional `dev` dependencies for build, test and lint tooling
* Duplicate YAML-key detection
* User-selected restore destinations with non-empty-directory protection
* Release-gate tests and Sprint 29 release report

### Changed

* NAS-only configurations now receive correct health checks
* Expected CLI failures now return non-zero exit codes
* Renamed misleading `--yes` option to `--non-interactive`
* Removed Timeshift from 1.0 requirements and claims until an integration exists
* Corrected repository-statistics and licensing documentation

### Fixed

* Restore no longer targets a development-only directory inside the source tree
* Source distributions now include documentation, configuration examples and changelog

---

## Sprint 28 – Interactive Backup Target Setup

### Added

* Interactive selection of USB, NAS or both destinations during first-time setup
* Prompts for target-specific labels, mount paths and repository paths
* Validation requiring at least one configured destination
* Checks and optional initialization for every enabled repository
* Sprint reports for Sprints 25 through 28

### Changed

* Setup configuration generation now edits parsed YAML instead of replacing template lines
* Setup repository checks now use the shared multi-target repository provider

---

## Sprint 27 – Multiple Backup Destinations

### Added

* Optional NAS target configuration for mounted network shares
* Resolution and selection of multiple available repositories
* Parallel backups to all enabled USB and NAS destinations

### Changed

* Existing USB-only configuration remains valid and NAS targets default to disabled
* Single-repository commands prompt for a destination when several are available

---

## Sprint 26 – Central Error Handling

### Added

* Typed application errors for configuration and external command failures
* Central CLI error handler for consistent user-facing diagnostics
* Graceful handling of keyboard interrupts

### Changed

* Configuration loading now translates file, YAML and validation failures into domain errors
* Setup reuses the same structured configuration diagnostics as the CLI

### Fixed

* A missing Restic executable is no longer reported as a missing configuration file

---

## Sprint 25 – Service Architecture Refactoring

### Added

* Dedicated services for status, health, setup, backup, restore and repository maintenance
* Shared repository provider for resolving configured backup targets
* Service-level tests for backup, retention, setup and repository resolution

### Changed

* Reduced the `Application` class to configuration loading and command orchestration
* Centralized Restic process execution and environment configuration
* Simplified CLI command dispatch
* Updated architecture and roadmap documentation

### Fixed

* Invalid or failed `lsblk` output is handled as an unavailable USB target
* Health checks now respect non-zero command exit codes
* Removed unreachable duplicate code from the setup wizard

---

# v1.0.0

## Sprint 22.4 – First User Experience

### Added

* Automatic creation of the configuration file
* Automatic creation of the repository password file
* Automatic repository initialization
* Package resource support for the default configuration
* XDG-compliant configuration directory
* Improved password validation
* Password length validation
* Interactive password retry
* User guidance during password creation

### Changed

* Lazy loading of the configuration
* Setup wizard now uses the generated configuration as the single source of truth
* Improved setup workflow
* Improved first-run user experience
* Improved setup messages and diagnostics

### Fixed

* Setup could not be executed without an existing configuration
* Incorrect configuration file location
* Package installation issues
* Repository initialization inconsistencies
* Multiple first-user installation problems

---

# v1.0.0

## Sprint 22.3 – Release Candidate Infrastructure

### Added

* Version command (`backup-manager --version`)
* Single Source of Truth versioning
* `importlib.metadata` integration
* Support for installation using `pip install .`

### Changed

* Package dependencies updated

---

# v1.0.0

## Sprint 22.2 – Robustness

### Improved

* Error handling for missing configuration files
* Error handling for invalid YAML
* Error handling for missing Restic
* Error handling for missing Timeshift
* Error handling for missing `lsblk`
* Error handling for invalid repository passwords
* Error handling for invalid repositories
* Error handling for missing USB devices
* Improved CLI diagnostics

---

# v1.0.0

## Sprint 22.1 – Testing

### Added

* Unit tests

### Fixed

* JSON decoding issues
* Invalid timestamp handling
* Repository robustness improvements

---

# v0.2.0-dev

## Added

* Health check implementation
* Python version verification
* Restic verification
* Timeshift verification
* Password file verification
* Installed software version reporting

---

# v0.1.0-dev

## Added

* Initial project structure
* Python virtual environment
* `src` project layout
* YAML configuration
* Initial Linux Backup Manager architecture

---

Linux Backup Manager

Version 1.0.0
