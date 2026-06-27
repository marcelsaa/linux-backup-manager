# Changelog

All notable changes to the Linux Backup Manager project are documented in this file.

The project follows Semantic Versioning and keeps a chronological history of all major development milestones.

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

