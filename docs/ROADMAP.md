# Linux Backup Manager

# Project Roadmap

**Last updated:** Sprint 80 abgeschlossen (2026-07-02); **Version 1.2.0 released 2026-07-02
and live on GitHub** (`main`, `develop`, tag `v1.2.0`; previously: Version 1.1.0 released
June 2026). Alle Release-Gates erfüllt: beide UAT-Sprachdurchläufe (Deutsch gegen rc1,
Englisch gegen rc2), UAT-1.2.0-DE-001 behoben und end-to-end nachverifiziert, voller
1.0.1→1.2.0-Upgrade-Lauf (nicht nur Dry-Run) und `installer.py`-Managed-Fresh-Install-
Validierung, jeweils in isolierter VM bestanden. Der zurückgestellte, nicht-blockierende Fund
UAT-1.2.0-EN-001 (doctor-Sprachfallback bei kaputter Config) wurde in Sprint 83 auf `develop`
behoben (siehe `docs/reports/USER_ACCEPTANCE_TEST_1.2.0rc1.md`).
Repository öffentlich seit 2026-07-01: https://github.com/marcelsaa/linux-backup-manager

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
* [x] Complete German and English documentation – all 8 planned user-facing docs done under
  `docs/de/`: `README.md`, `USER_GUIDE.md` *(Sprint 67)*, `INSTALL.md`, `RESTORE.md`,
  `RECOVERY.md` *(Sprint 68)*, `FAQ.md`, `CONFIGURATION.md`, `SYSTEMD.md` *(Sprint 69)*.
  Architecture/process docs (`ARCHITECTURE.md`, `QA_TESTPLAN.md`, `ROADMAP.md`,
  `DEVELOPMENT.md`, `INTERNATIONALIZATION.md`) intentionally stay English-only. Also fixed
  along the way: `docs/FAQ.md` had stale answers (NAS described as unsupported, though
  implemented since before 1.1.0; a "Future Features" list that was entirely outdated).

---

## Diagnostics

* [x] Initial read-only `backup-manager doctor` self-test command
* [x] Combined configuration, password-permission, Restic, target and repository diagnostics
* [x] Last successful backup timestamp
* [x] systemd timer diagnostics *(Sprint 47)*
* [x] Last-backup age in doctor and status *(Sprint 47)*

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
* [x] Repeat the complete fresh-wheel User Acceptance Test after the fix

Status: **Passed. Version 1.1.0rc2 passed implementation, local artifact validation and independent
German and English external UAT.**

Validation update: **Both `1.1.0rc2` external UAT language passes completed without workaround or
unresolved finding. Version 1.1.0rc2 is approved for migration from Version 1.0.1.**

Current release status: **Version 1.1.0rc1 failed external acceptance and remains rejected. Its
replacement Version 1.1.0rc2 passed Sprint 43 and is approved for migration from Version 1.0.1.**

## Release Candidate Policy

* [x] Feature freeze begins with `1.1.0rc1`
* [x] Apply only bug fixes, documentation and translation corrections
* [x] Build `1.1.0rc2` because Sprint 43 fixes require another validation cycle
* [x] Accept `1.1.0rc3` after managed fresh-install and Version 1.0.1 upgrade UAT
* [x] Release Version 1.1.0
* [x] Begin Version 1.2 development after the Version 1.1.0 release – underway since
  Sprint 46; `pyproject.toml` bumped to `1.2.0.dev0` to reflect this, matching the
  `1.1.0.dev0` convention used after the 1.0.1 release *(Sprint 64)*

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

* [x] Interactive configuration menus *(Sprint 51)*
* [x] Configuration import/export *(Sprint 54)*
* [x] Repository migration – implemented under "Version 1.3" (see below), not 1.2, since
  Restic has no native migrate tool and the feature needed its own design *(Sprint 86)*
* [x] Improved diagnostic presentation *(Sprint 52)*
* [x] Apply default retention values (keep_daily: 14, keep_weekly: 8, keep_monthly: 12, keep_yearly: 3) during setup *(Sprint 46)*
* [x] Automatic forget and prune after every successful backup (hidden from the user) *(Sprint 46)*

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

* [x] Desktop entry creation (`~/.local/share/applications/`) *(Sprint 48)*
* [x] Application menu entry *(Sprint 48)*
* [x] Desktop icon (`~/Desktop/`) *(Sprint 48)*

All entries shall be optional and individually selectable.

---

## Security

* [x] Change the repository password *(Sprint 49)*
* [x] Automatically update the password file after a password change *(Sprint 49)*
* [x] Regenerate the recovery sheet after a password change *(Sprint 49)*

---

## Documentation

* [ ] User tutorials *(deferred past 1.2.0, does not block the release; still deferred as of
  Version 1.3 — content-only backlog item, not part of any specific release cycle)*
* [ ] Additional examples *(deferred past 1.2.0, does not block the release; still deferred
  as of Version 1.3 — content-only backlog item, not part of any specific release cycle)*
* [x] Complete German and English documentation for all user-facing docs *(Sprints 67–69)*

## Release Candidate Policy

* [x] Feature freeze begins with `1.2.0rc1` *(Sprint 70)*
* [x] Apply only bug fixes, documentation and translation corrections from this point on
* [x] Local quality gate passed (Ruff, compileall, pytest, build, twine check) – wheel
  SHA-256: `0f012f29125f59104422c2d70d6f021f683b25489a39e9c3a47adac9daa9c9f9` *(Sprint 70)*
* [x] Manual UAT in German (user-requested, executed via isolated VM) – 1 non-blocking
  finding (UAT-1.2.0-DE-001) *(Sprint 72)*
* [x] Manual UAT in English – **waived for `1.2.0rc1`**: test VM hardware instability made
  it unsafe to run at the time; owner-approved one-time exception *(Sprint 73)*, later
  caught up against `1.2.0rc2` on a new stable VM – see below *(Sprint 76)*
* [x] Fix UAT-1.2.0-DE-001 (`settings` schedule change now reinstalls/removes the systemd
  timer) – `1.2.0rc2`, wheel SHA-256:
  `4b6ff1176e5516b314b556c3fafd52897cd514134611f8ecc16211201c422467` *(Sprint 74)*
* [x] `installer.py --dry-run` for the 1.0.1 upgrade path run on the real production system
  – detection and preflight checks passed, no side effects *(Sprint 75)*
* [x] Manual UAT in English run against `1.2.0rc2` on a new libvirt/KVM VM (all 15 steps
  passed); Step 7 also served as the end-to-end re-validation of the UAT-1.2.0-DE-001 fix
  against a real systemd user instance, accepted by the owner as sufficient. One new
  non-blocking finding, UAT-1.2.0-EN-001 (doctor's language fallback on an unloadable
  config), accepted as known/deferred. UAT decision updated to `Passed` *(Sprint 76)*
* [x] Full upgrade run (not just dry-run) for 1.2.0 in an isolated VM: real 1.0.1 legacy
  installation upgraded to `1.2.0rc2` via `installer.py`; negative preflight, config/password
  preservation, launcher/unit/timer cutover, post-upgrade backup/restore and idempotent
  rerun all verified *(Sprint 77)*
* [x] Managed fresh-install validation of `1.2.0rc2` via `installer.py` in an isolated VM:
  dry-run and real run, launcher/versioned-venv cutover, setup, backup/restore, EOF
  handling, doctor/health, cleanup, and idempotent rerun all verified — **last outstanding
  gate item, now resolved** *(Sprint 78)*
* [x] Merge to `main` after explicit owner sign-off *(Sprint 78, second finalization merge
  in Sprint 79)*
* [x] Release Version 1.2.0 — version bumped from `1.2.0rc2` to final `1.2.0`, user-facing
  documentation audited for the new stable version (README, INSTALL, USER_GUIDE,
  ARCHITECTURE, CONFIGURATION, QA_TESTPLAN, FAQ, RESTORE, RECOVERY, DEVELOPMENT,
  INTERNATIONALIZATION and their `docs/de/` counterparts), tagged `v1.2.0` *(Sprint 79)*

---

# Version 1.3

## Restore Experience

* [x] Snapshot restoration via read-only FUSE mount — new `mount` command / main-menu
  default for "Restore files" (`restic mount`, browsing `<mountpoint>/ids/<snapshot-id>`)
  *(Sprint 85)*
* [x] Automatic file manager launch after mounting a snapshot — `xdg-open`, degrades to a
  printed path if no file manager is available *(Sprint 85)*
* [x] Clean unmount workflow after file selection — explicit "press Enter when finished"
  prompt (closing the file manager window cannot be reliably detected across desktop
  environments), unmount always runs via `try`/`finally` even on `Ctrl+C`/EOF *(Sprint 85)*
* [x] No Restic commands visible to the user *(Sprint 85)*
* [x] The previous full-snapshot restore (copy an entire snapshot to a directory) is not
  removed — it remains available unchanged as `backup-manager restore`, now reachable from
  the main menu via Administration → Expert Functions → "Restore a full snapshot", since it
  is still the right tool for full disaster recovery (see `docs/RECOVERY.md`, which
  documents `backup-manager restore` as the emergency-recovery step) *(Sprint 85)*

## Interaction Model

* [x] Guided terminal user interface with main menu (6 items, see Design Philosophy)
  — implemented in `lbm/cli/menu.py` (`MainMenu`), numbered-choice style matching the
  existing `settings` menu *(Sprint 84)*
* [x] Administration submenu for Doctor, repository check, log viewer, backup history —
  log viewer is a new `LogViewerService`/`logs` command; backup history maps to the
  existing `snapshots` command *(Sprint 84)*
* [x] Doctor integrated into Administration area — not in the 6-item main menu *(Sprint 84)*
* [x] Desktop/application-menu shortcut launches directly into the interactive main menu
  instead of running the plain `status` command once and exiting. `installer.py`'s `Exec`
  line is back to invoking the launcher directly (the Sprint 81 "Press Enter to close" pause
  hack is no longer needed, since the menu itself keeps the terminal open) *(Sprint 84)*

## CLI Help Output

* [x] Replace argparse's default `-h`/`--help` output with a custom renderer that prints a
  readable command → description list instead of the current unreadable
  `{status,health,doctor,...}` choice list with a single generic help line. Motivation
  (2026-07-03): Marcel reported that `backup-manager -h` gives no indication of what each
  command actually does, and that the output mixes English command names with a
  German-or-English description depending on the configured language — inconsistent and
  confusing.
* [x] Show both German and English together, but as two separate full-width blocks — the
  complete German command list first, then the complete English command list below it — not
  interleaved line-by-line per command. Each block colored consistently with its own ANSI
  color (`Console` already defines `GREEN`/`RED`/`YELLOW`/`BLUE`; one additional color
  constant covers the second language), so the two languages read as two clean columns of
  text rather than an alternating pattern. Confirmed with Marcel via a mockup (2026-07-03).
* [x] Needs one new i18n key per command (e.g. `cli.commands.backup.description`) in both
  `de.yaml` and `en.yaml`, since the existing single `cli.command_help` key only covers the
  generic `-h` argument description, not per-command text.
* [x] Implementation stays in `lbm/cli/` (presentation-only, no business logic): intercept
  `-h`/`--help` before `argparse.ArgumentParser.parse_args()` (e.g. `add_help=False` plus a
  manual check), load both `LanguageService("de")` and `LanguageService("en")` instances, and
  print the table via `Console`.

## Repository Migration

* [x] Copy all snapshots from one configured backup target to another (e.g. USB → NAS),
  using Restic's own `copy` command (`--from-repo`/`--from-password-file`) since Restic has
  no native "migrate" command. New `ResticRepository.copy_from()`, new `migrate` command,
  reachable from Administration → Expert Functions → "Migrate repository". Originally listed
  under "Version 1.2 → User Experience" and marked "moved to v1.3", but never actually
  tracked here until a roadmap review caught the gap *(Sprint 86)*
* [x] Only offers migration between targets already configured and reachable (via the
  existing `RepositoryProvider.get_all()`) — does not add a new target-configuration flow;
  requires at least two reachable, enabled targets *(Sprint 86)*
* [x] Destination is initialized automatically if not already a Restic repository, then all
  snapshots are copied; explicit confirmation is required first since this can take a long
  time for large repositories *(Sprint 86)*

## Release Candidate Policy

* [x] Feature freeze begins with `1.3.0rc1` *(Sprint 86)*
* [x] Apply only bug fixes, documentation and translation corrections from this point on

---

# GitHub-Veröffentlichung

Mit dem nächsten stabilen Release (Version 1.2.0) soll das Repository öffentlich auf GitHub
veröffentlicht werden. Vor der Veröffentlichung sind folgende Punkte zu klären:

## Engagement-Modell (Entscheidung 2026-07-01)

Die Veröffentlichung ist ausschließlich eine **Geste** – das Projekt wurde für den eigenen
Bedarf entwickelt, und andere sollen den Code sehen und nutzen können. Es soll daraus
**keinerlei laufender Aufwand** entstehen: keine Support-Verpflichtung, kein Zwang, PRs zu
prüfen oder zu mergen, keine Erwartungshaltung von außen.

Konkret bedeutet das:

* **Öffentlich sichtbar** (klonbar, forkbar) – das ist der einzige Zweck der Veröffentlichung.
* **Issues deaktiviert** in den GitHub-Repository-Einstellungen (Settings → Features → Issues
  aus) – technisch keine Möglichkeit für Dritte, Bug-Reports oder Feature-Wünsche zu eröffnen.
  Dies ist eine manuelle Einstellung im GitHub-Web-UI, die erst nach dem Erstellen des
  Repositories dort vorgenommen werden kann – nicht Teil dieses lokalen Repos.
* **Pull Requests** lassen sich technisch nicht sperren (Forken + PR ist Grundprinzip von
  öffentlichem GitHub), erzeugen aber keine Verpflichtung – ein geöffneter PR kann ignoriert,
  kommentarlos geschlossen oder irgendwann bearbeitet werden, ganz nach Belieben.
* **Sicherheitsmeldungen** laufen unverändert privat über `SECURITY.md` (E-Mail), unabhängig
  von Issues.
* `.github/ISSUE_TEMPLATE/` (Sprint 59) bleibt bestehen, auch wenn Issues deaktiviert werden –
  falls sich das später ändert, sind die Vorlagen bereits vorhanden. Kein Nutzen, aber auch
  kein Schaden, solange Issues aus sind.
* `CONTRIBUTING.md` dokumentiert diese Erwartungshaltung explizit für jeden, der das Repo
  besucht oder forkt.

**Lizenz und Rechtliches**

* [x] Lizenzwahl bestätigen (GPL-3.0-only in `pyproject.toml`) *(Sprint 55)*
* [x] Restic-Lizenzkompatibilität dokumentieren (Restic: BSD-2-Clause, kompatibel mit GPL-3.0 –
  in README aufgenommen) *(Sprint 55)*

**Distribution**

* [x] Distributionskanal entscheiden – **GitHub Releases** (Wheel + `installer.py` +
  veröffentlichter SHA-256 als Release-Assets), **kein PyPI**. Begründung: `installer.py`
  baut eine eigene verwaltete venv mit Desktop-Integration, Upgrade-Erkennung ab 1.0.1 und
  Rollback-Garantien auf – das passt nicht zu einem `pip install`-Fluss, der all das umgehen
  würde. Der PyPI-Name bleibt als spätere Option offen, falls jemals Bedarf entsteht
  *(Sprint 61)*
* [x] Paketname `linux-backup-manager` auf PyPI auf Verfügbarkeit prüfen – verfügbar
  (`https://pypi.org/pypi/linux-backup-manager/json` liefert `404`, Name ist nicht
  registriert) *(Sprint 59)*
* [x] Versionierung und Release-Tags auf GitHub entschieden – die bestehende Tag-Historie
  (`v1.0.1`, `v1.1.0`) wird beim History-Rewrite **behalten, nicht verworfen**; `v1.2.0` ist
  nicht der erste Tag überhaupt, sondern der erste Tag mit angehängten GitHub-Release-Assets
  (Wheel, Installer, SHA-256). Der interne Tag `backup-v1.0.0-before-refactor` wird beim
  History-Rewrite nicht mit veröffentlicht, da er ein reiner Vor-Refactor-Sicherungspunkt
  ohne externen Nutzen ist *(Sprint 61)*

**Repository-Inhalt**

* [x] Sicherstellen, dass keine privaten Pfade, Hostnamen oder persönliche Daten im Git-Verlauf
  enthalten sind – erledigt für eine **separate, gefilterte Kopie** unter
  `/home/marcel/Projekte/linux-backup-manager-public.git` (bare Repo, via `git-filter-repo`).
  Das eigentliche Arbeits-Repo bleibt unverändert. `docs/reports/` und `CLAUDE.md` sind aus der
  gesamten Historie entfernt und verifiziert nicht mehr als Objekte vorhanden (`git gc
  --prune=now` durchgeführt) *(Sprint 63)*
* [x] `CLAUDE.md` bei der History-Filterung ausgeschlossen – erledigt in derselben Filterung
  *(Sprint 63)*
* [x] Autor-E-Mail der ersten vier Commits korrigiert – per `--mailmap` in derselben Filterung
  auf `Marcel <marcel.saager@gmx.de>` vereinheitlicht, verifiziert (`git log --all --format=%ae`
  zeigt nur noch die reguläre Adresse) *(Sprint 63)*
* [x] Entscheiden, ob interne Sprint-Berichte (`docs/reports/`) mitveröffentlicht werden –
  **Nein**, bleiben privat und werden vor der Veröffentlichung aus der Git-Historie gefiltert.
  Stattdessen fasst `docs/DEVELOPMENT.md` die Entwicklungsmethodik ohne personenbezogene
  Details zusammen *(Sprint 57)*
* [x] Entscheiden, ob `CLAUDE.md` mitveröffentlicht wird – **Nein**, bleibt privat, analog zu
  `docs/reports/`. Enthält keine personenbezogenen Daten (geprüft), aber interne
  Arbeitsanweisungen für den KI-Assistenten sind kein Nutzerdokument und bieten für die
  Zielgruppe keinen Mehrwert; passt zum Engagement-Modell (keine Erklärungspflicht
  gegenüber Dritten) *(Sprint 62)*
* [x] Git-Verlauf enthält `Co-Authored-By: Claude Sonnet 4.6` – **bleibt unverändert
  stehen**. Anders als der Tailscale-Fund ist das kein Datenschutzrisiko, sondern eine
  zutreffende Attribution; ein History-Rewrite dafür wäre eine nachträgliche Verfälschung
  ohne Datenschutz- oder Sicherheitsgrund *(Sprint 62)*

**Sicherheit**

* [x] `SECURITY.md` erstellen: Meldeweg für Sicherheitslücken (private E-Mail statt öffentlichem
  Issue), da LBM Passwortdateien und Repository-Zugänge verwaltet *(Sprint 55)*

**Community**

* [x] `README.md` für eine externe Zielgruppe überarbeiten – CI-/Lizenz-/Python-Badges,
  konkreter Installationslink zur Releases-Seite, Klon-URL, illustrative
  "Example Session" (keine echten Screenshots, da CLI-Tool ohne Bildmaterial),
  klickbare Dokumentationsliste, "Contributing & Support"-Abschnitt, aktualisierter
  Project-Status-Text (Feature-Freeze-Hinweis war veraltet) *(Sprint 63)*
* [x] GitHub Actions / CI für öffentliches Repo prüfen – `.github/workflows/ci.yml` enthält
  keine Secrets, setzt `permissions: contents: read` und referenziert keine internen Pfade;
  unverändert veröffentlichungstauglich *(Sprint 58)*
* [x] Contribution-Richtlinien klären (Solo-Projekt, Pull Requests willkommen oder nicht?) –
  Entschieden: Projekt wird als Geste veröffentlicht, keine aktive Pflege-Erwartung; siehe
  "Engagement-Modell" oben und `CONTRIBUTING.md` *(Sprint 60)*
* [x] Issues in den GitHub-Repository-Einstellungen deaktivieren – erledigt, verifiziert
  via `gh repo view` (`hasIssuesEnabled: false`) *(Sprint 65)*
* [x] Issue-Templates für Bug-Reports und Feature-Requests anlegen (optional) –
  `.github/ISSUE_TEMPLATE/bug_report.md` und `feature_request.md` *(Sprint 59)*

## Veröffentlichung abgeschlossen (2026-07-01, Sprint 65)

Das Repository ist live: **https://github.com/marcelsaa/linux-backup-manager**

- [x] Öffentliches, leeres Repository unter `github.com/marcelsaa/linux-backup-manager`
  angelegt.
- [x] Gefilterte Kopie (frisch regeneriert, Stand nach Sprint 64) gepusht: `main` (Default-
  Branch), `develop`, Tags `v1.0.1`/`v1.1.0`/`v1.1.0rc2`.
- [x] Issues in den Repository-Einstellungen deaktiviert (`hasIssuesEnabled: false`,
  verifiziert via `gh repo view`).
- [x] CI-Workflow läuft automatisch auf GitHub Actions (erster Lauf ausgelöst durch den
  Push nach `main`).
- [ ] Optional: Release `v1.2.0` mit Wheel + `installer.py` + SHA-256 als Assets anlegen,
  sobald Version 1.2.0 fertig ist (siehe Abschnitt "Distribution" oben).

Die lokale gefilterte Kopie unter `/home/marcel/Projekte/linux-backup-manager-public.git`
bleibt als Vorlage für künftige Aktualisierungen bestehen (z. B. für den v1.2.0-Release):
bei Bedarf frisch aus dem Arbeits-Repo neu erzeugen (siehe `docs/reports/SPRINT_63.md`) und
erneut pushen.

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

Stable Version 1.2.0, live auf GitHub (Sprint 80 abgeschlossen) ·
Öffentlich auf GitHub: marcelsaa/linux-backup-manager
