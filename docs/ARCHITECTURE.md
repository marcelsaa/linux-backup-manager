# Linux Backup Manager

# Architecture

**Version:** 1.0.0

---

# Overview

The Linux Backup Manager (LBM) is a command-line application written in Python.

The project follows a modular architecture where each component is responsible for a single task. The `Application` class acts as the central command dispatcher and coordinates the interaction between the individual modules.

Future versions will gradually refactor the `Application` class into dedicated services.

---

# High-Level Architecture

```text
CLI
 │
 ▼
Application
 │
 ├── Configuration
 │
 ├── Setup Wizard
 │
 ├── Backup
 │
 ├── Restore
 │
 ├── Health Checks
 │
 ├── Repository Management
 │
 └── User Interface
```

---

# Main Components

## CLI

The command-line interface parses user input and dispatches commands to the application layer.

Responsibilities:

* Command parsing
* Argument validation
* Application startup

---

## Application

The `Application` class coordinates all operations.

Responsibilities:

* Command dispatching
* Configuration loading
* Calling feature modules
* Error handling

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

# Future Architecture

Version 1.1 plans to split the current `Application` class into dedicated services.

Planned services include:

* BackupService
* RestoreService
* SetupService
* HealthService
* RepositoryMaintenanceService

This will reduce coupling and improve maintainability.

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

Version 1.0.0
