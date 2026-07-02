# Linux Backup Manager

# Development Process

**Version:** 1.1.0

---

# Purpose

This document summarizes how Linux Backup Manager is developed and validated. It is intended for
readers who want to understand the project's engineering discipline without needing the detailed,
internal per-sprint development records.

---

# Iterative Development

Linux Backup Manager is developed in small, incremental units of work, each adding or refining a
single feature, fix, or piece of documentation. This keeps every change reviewable in isolation and
allows the test suite to grow alongside the codebase rather than in large, hard-to-verify batches.

---

# Quality Gate

Every change passes the following checks before it is committed:

1. **Linting** – `ruff check .`
2. **Byte-compilation** – `python -m compileall -q src tests`, to catch syntax errors
3. **Automated tests** – `pytest -q`

The test suite covers success and failure paths for every public service method, shell-injection
safety for all external command invocations, and both German and English output for
language-specific flows. The suite is expected to grow monotonically; existing tests are not
weakened or removed to accommodate new changes.

---

# Release Candidate Process

Stable releases follow a release-candidate cycle:

1. **Feature freeze** once the first release candidate is built – only bug fixes, documentation
   and translation corrections are applied afterward.
2. **Local quality gate** (see above) plus a full package build and `twine check`.
3. **Fresh-installation validation** of the built wheel in an isolated environment, covering both a
   clean install and an upgrade from the previous stable version.
4. **User acceptance testing** in both supported languages (German and English).
5. Only after all of the above pass is a release candidate promoted to a stable release.

---

# Internal Development Records

Detailed per-sprint development notes and release-candidate validation reports are kept as
internal records and are not part of the public repository. They contain environment-specific
details (local paths, hostnames) that are not relevant to using or contributing to the project.
`docs/QA_TESTPLAN.md` remains public and describes the manual test plan that every release
candidate must pass.

---

Linux Backup Manager Documentation
