# Linux Backup Manager

# Architecture

**Version:** 1.0.1

---

# Overview

The Linux Backup Manager (LBM) is a command-line application written in Python.

The project follows a modular architecture where each component is responsible for a single task. The `Application` class acts as the central command dispatcher and coordinates the interaction between the individual modules.

The `Application` class delegates user-facing workflows to dedicated services.

---

# High-Level Architecture

```text
CLI
 │
 ├── ErrorHandler
 │
 ▼
Application
 │
 ▼
Services
 │
 ├── StatusService
 ├── HealthService
 ├── SetupService
 ├── BackupService
 ├── RestoreService
 ├── SystemdScheduler
 └── RepositoryMaintenanceService
     │
     └── RepositoryProvider
          ├── USB Target
          ├── NAS Target
          └── Restic Repositories
```

---

# Main Components

## CLI

The command-line interface parses user input and dispatches commands to the application layer.

Responsibilities:

* Command parsing
* Argument validation
* Application startup
* Central rendering of expected application errors

---

## Application

The `Application` class is a thin command coordinator. It loads configuration lazily and
delegates each command to a dedicated application service.

Responsibilities:

* Configuration loading
* Service construction
* Command delegation

---

## Services

Application services contain the user-facing workflows and keep infrastructure details out of
the central application class.

Responsibilities:

* `StatusService`: system and configuration status
* `HealthService`: health-check workflow
* `SetupService`: first-run setup
* `BackupService`: backup workflow
* `RestoreService`: guided restore workflow
* `RepositoryMaintenanceService`: initialization, snapshots, checks, retention and pruning
* `RepositoryProvider`: resolve all configured targets and create Restic repository clients
* `SystemdScheduler`: install daily and startup-check user timers

Successful backups are recorded by `BackupStateStore`. A daily timer checks the user-selected
interval at the configured time. The startup timer invokes `backup-if-due`, which only runs when
the last recorded success is older than that interval.

`BackupService` executes backups for all available destinations concurrently. Commands that
operate on one repository ask the user to select a destination when more than one is available.

Expected failures cross service boundaries as typed `ApplicationError` subclasses. The CLI
renders these errors consistently without exposing internal tracebacks.

---

## Configuration

Configuration is stored in:

```text
~/.config/linux-backup-manager/config.yaml
```

The configuration is loaded only when required (lazy loading).

This prevents circular dependencies during the initial setup.

---

## Setup Wizard

The setup wizard performs the first-time configuration.

Responsibilities:

* Create configuration
* Create password file
* Verify required software
* Detect USB backup device
* Create repository

The setup wizard can safely be executed multiple times.

---

## Backup

The backup module creates Restic backups using the configured backup paths.

---

## Restore

The restore module restores snapshots from the repository.

---

## Repository Management

Repository management includes:

* Repository initialization
* Repository statistics
* Repository integrity checks
* Snapshot management
* Retention
* Pruning

---

## User Interface

Console output is centralized through the `Console` helper class.

Responsibilities:

* Success messages
* Warnings
* Errors
* Informational output

---

# Configuration Flow

```text
CLI
 │
 ▼
Application
 │
 ▼
Load Configuration
 │
 ▼
Execute Command
```

The `setup` command is the only exception.

During setup, the configuration is created first and then loaded before the remaining setup steps continue.

---

# Architecture Evolution

The current development work toward Version 1.1 introduces dedicated services and reduces the
`Application` class to orchestration.

Further improvements may include:

* Dependency injection at the application boundary

---

# Design Goals

The architecture follows the following principles:

* Separation of responsibilities
* Minimal external dependencies
* Predictable behaviour
* Robust error handling
* Testability
* Long-term maintainability

---

Linux Backup Manager Documentation

Version 1.0.1
