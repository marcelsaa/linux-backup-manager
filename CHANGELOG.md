# Changelog

All notable changes to the Linux Backup Manager project are documented in this file.

The project follows Semantic Versioning and keeps a chronological history of all major development milestones.

---

# Unreleased

## Sprint 82 – Lesbare, zweisprachige CLI-Hilfe

### Added

* `backup-manager -h`/`--help` zeigt jetzt einen eigenen, lesbaren Hilfetext statt argparses
  unübersichtlicher Klammerliste aller 23 Befehle: ein vollständiger deutscher Block (türkis)
  gefolgt von einem vollständigen englischen Block (magenta), jeweils mit Beschreibung pro
  Befehl. Neues Modul `lbm/cli/help_renderer.py`; neue i18n-Schlüssel
  `cli.commands.<befehl>.description`, `cli.options.help`, `cli.options.version`,
  `cli.help.heading_de`/`heading_en` in beiden Katalogen. Zwei neue Farbkonstanten
  `Console.CYAN`/`Console.MAGENTA`. 6 neue Tests (186 → 192 Tests).

## Sprint 81 – Desktop-Verknüpfung schließt sich sofort wieder (Fix)

### Fixed

* Die von `installer.py` erzeugte Desktop-/Menü-Verknüpfung öffnete ein Terminal, das sich
  sofort wieder schloss, da `backup-manager` ohne Argumente (`status`) fast augenblicklich
  beendet und nichts das Terminal offen hielt. Der `Exec`-Eintrag pausiert jetzt nach der
  Ausführung mit einem "Press Enter to close..."-Prompt.
* Der erste Fix-Versuch (`read -p`) schlug unter `dash` (Standard-`/bin/sh` auf Debian/
  Ubuntu) fehl, da `-p` ein Bash-ismus ist; korrigiert auf ein POSIX-kompatibles
  `printf`+`read -r`.
* Testfall ergänzt, der `read -p` explizit ausschließt (185 → 186 Tests).

---

# v1.2.0 – 2026-07-02

## Sprint 80 – Zu GitHub gepusht

### Released

* `main`, `develop` und Tag `v1.2.0` zu `github.com/marcelsaa/linux-backup-manager` gepusht.
* Beide durch den Push ausgelösten CI-Läufe erfolgreich.

## Sprint 79 – Version 1.2.0 final freigegeben

### Released

* Version von `1.2.0rc2` auf finales `1.2.0` angehoben (`pyproject.toml`).
* Nutzerorientierte und Architektur-Dokumentation auf die neue stabile Version aktualisiert:
  `README.md`, `docs/INSTALL.md`, `docs/USER_GUIDE.md`, `docs/ARCHITECTURE.md`,
  `docs/CONFIGURATION.md`, `docs/QA_TESTPLAN.md`, `docs/FAQ.md`, `docs/RESTORE.md`,
  `docs/RECOVERY.md`, `docs/DEVELOPMENT.md`, `docs/INTERNATIONALIZATION.md` sowie deren
  `docs/de/`-Pendants. `docs/ARCHITECTURE.md` ergänzt außerdem die seit 1.1.0 hinzugekommenen
  Services (`PasswordChangeService`, `ConfigExportService`, `ConfigImportService`,
  `settings`-Menü) im Architekturdiagramm.
* `develop` nach `main` gemergt und mit `v1.2.0` getaggt.

## Sprint 78 – Managed-Fresh-Install-Validierung über installer.py bestanden

### UAT / Validierung

* Verwaltete Neuinstallation von `1.2.0rc2` über `installer.py` (Dry-Run dann echter Lauf)
  in einer vierten isolierten VM (`ubuntu24.04-managed-Fresh`) durchgeführt: Modus korrekt
  als `fresh` erkannt, Launcher-Symlink korrekt auf die neue versionierte venv gesetzt,
  keine `config.yaml` durch den Installer selbst angelegt. Anschließendes First-User-Setup
  (Deutsch), Backup/Check, Restore, EOF-Verhalten, `doctor`/`health`, `schedule-remove` und
  ein idempotenter Re-Lauf (`Detected mode: current`) alle bestanden.
* Damit sind **alle** Punkte aus `docs/reports/RELEASE_CANDIDATE_1.2.0rc2.md`
  ("Outstanding Before Release") erledigt. Der Kandidat ist technisch bereit für den Merge
  nach `main`; der Merge selbst erfolgt erst nach ausdrücklicher Freigabe des Nutzers.

## Sprint 77 – Voller Upgrade-Lauf 1.0.1→1.2.0rc2 in isolierter VM bestanden

### UAT / Validierung

* Voller (nicht nur Dry-Run) Upgrade-Lauf von einer echten 1.0.1-Installation (Legacy-Venv-
  Layout wie auf dem Produktivsystem, echte Config/Passwort/NAS-Repository/Snapshots/Timer)
  auf `1.2.0rc2` in einer dritten isolierten VM (`ubuntu24.04-UAT`) durchgeführt. 1.0.1-Wheel
  aus dem Git-Tag `v1.0.1` gebaut, da kein fertiges Artefakt mehr vorlag.
* Negativer Preflight (unerreichbares NAS) korrekt mit Exit `1` und ohne Zustandsänderung
  abgelehnt. Echter Upgrade-Lauf: Config/Passwort-Inhalt und -Rechte exakt erhalten, alter
  1.0.1-Venv für Rollback erhalten, Launcher korrekt auf neue versionierte venv umgeschaltet,
  systemd-Units auf neuen Interpreter aktualisiert, Timer-Zustand erhalten, `doctor`/`check`
  danach fehlerfrei. Post-Upgrade-Backup und -Restore erfolgreich (SHA-256-Match), erneuter
  Installer-Lauf korrekt als `current` (idempotent) erkannt.
* Damit ist der seit Sprint 74/75 offene Punkt "voller Upgrade-Lauf" erledigt. Letzter
  verbleibender Punkt vor Merge nach `main`: Managed-Fresh-Install-Validierung über
  `installer.py`.

## Sprint 76 – Englischer UAT-Durchlauf für 1.2.0rc2 auf neuer VM-Umgebung

### UAT / Validierung

* Englischer UAT-Durchlauf (seit Sprint 73 ausstehend) auf einer neuen, stabilen
  libvirt/KVM-VM (`Ubuntu24.04-Clean`, Ubuntu 24.04) vollständig und ohne Workaround
  durchgeführt – gegen `1.2.0rc2` statt des überholten `1.2.0rc1`. Alle 15 Schritte
  bestanden, durchgehend Englisch.
* Schritt 7 (Settings → Zeitplan) diente gleichzeitig als End-to-End-Nachprüfung des
  UAT-1.2.0-DE-001-Fixes gegen eine echte systemd-User-Instanz: Timer-`OnCalendar`
  bestätigt aktualisiert, `list-timers` bestätigt neuen Trigger. Vom Projektinhaber als
  ausreichende Re-Validierung akzeptiert – Fix jetzt vollständig bestätigt.
* Neuer, nicht-blockierender Fund UAT-1.2.0-EN-001: `doctor` fällt bei komplett nicht
  ladbarer Konfiguration auf Deutsch statt Englisch zurück
  (`_configured_language()` in `src/lbm/cli/main.py`). Vom Projektinhaber als bekannt und
  aufgeschoben akzeptiert, kein Release-Blocker.
* UAT-Entscheidung in `docs/reports/USER_ACCEPTANCE_TEST_1.2.0rc1.md` von "Pending" auf
  "Passed" aktualisiert – beide Sprachdurchläufe jetzt abgeschlossen.

## Sprint 75 – Dry-Run-Validierung des 1.0.1→1.2.0-Upgrade-Pfads

### UAT / Validierung

* `installer.py --dry-run` mit dem `1.2.0rc2`-Wheel direkt auf dem echten Produktivsystem
  ausgeführt (Version dort: `1.0.1`). Ergebnis: Modus korrekt als `upgrade` erkannt,
  Preflight-Prüfungen (Python ≥ 3.12, Restic, Speicherplatz) bestanden, keinerlei
  Seiteneffekte (Config, Passwortdatei, systemd-Timer vor/nach Lauf verifiziert
  unverändert). Deckt aber nur Erkennung/Preflight ab, nicht die eigentliche Migration
  (venv-Cutover, Rollback) – ein voller Upgrade-Lauf bleibt vor dem echten Produktiv-Upgrade
  empfohlen.

## Sprint 74 – UAT-1.2.0-DE-001 behoben (1.2.0rc2)

### Fixed

* `settings`-Zeitplan-Untermenü (`configure_settings()` in `src/lbm/setup/wizard.py`)
  installiert den systemd-Timer jetzt korrekt neu, wenn der Zeitplan geändert wird
  (`SystemdScheduler.install()`), bzw. entfernt ihn, wenn die Planung im Menü deaktiviert
  wird (`SystemdScheduler.remove()`). Vorher wurde nur `config.yaml` aktualisiert, der Timer
  behielt die alte Zeit bei. Behebt UAT-1.2.0-DE-001.
* Neue Tests in `tests/test_setup_wizard.py`: Reinstall bei aktiviertem Zeitplan, Removal bei
  Deaktivierung, kein Scheduler-Aufruf bei anderen Menüpunkten (185 Tests, vorher 182).
* Version auf `1.2.0rc2` angehoben; neues Wheel gebaut (SHA-256
  `4b6ff1176e5516b314b556c3fafd52897cd514134611f8ecc16211201c422467`).

## Sprint 73 – Englischer UAT-Durchlauf: nicht sicher durchführbar

### UAT

* Der englische UAT-Durchlauf für 1.2.0rc1 konnte nicht sicher durchgeführt werden: die
  Host-Hardware für die GNOME-Boxes-Test-VM wurde instabil (VM startete unzuverlässig,
  SSH-Portweiterleitung brach wiederholt ab). Auf ausdrückliche Weisung des Projektinhabers
  wird dies als "nicht sicher durchgeführt" dokumentiert statt stillschweigend übersprungen
  oder fälschlich als bestanden vermerkt – siehe
  `docs/reports/USER_ACCEPTANCE_TEST_1.2.0rc1.md`, Abschnitt "English Pass Waived".
* Dies ist eine einmalige, vom Projektinhaber freigegebene Ausnahme; die englischsprachige
  Bedienung wird nach dem Release manuell auf dem Echtsystem verifiziert.

## Sprint 72 – UAT-Durchführung 1.2.0rc1 (deutscher Durchlauf)

### UAT

* Kompletter deutscher UAT-Durchlauf (Schritte 1–15) in einer isolierten GNOME-Boxes-VM
  (Linux Mint 22.3) per SSH durchgeführt. 14 von 15 Bereichen ohne Befund bestanden.
* **Fund UAT-1.2.0-DE-001:** Das `settings`-Zeitplan-Untermenü aktualisiert `config.yaml`,
  installiert den systemd-Timer aber nicht neu – der Timer behält die alte `OnCalendar`-Zeit,
  ohne Warnhinweis. `doctor` erkennt diese Diskrepanz ebenfalls nicht (prüft nur
  aktiv/aktiviert, nicht die Zeit-Übereinstimmung). Nicht release-blockierend (bestehender
  Zeitplan funktioniert weiter), aber ein reales Verhaltensproblem.
* Bestätigt: Der 1.1.0rc1-Fund UAT-DE-002 (unerwünschtes Catch-up-Snapshot durch den
  `due`-Timer) tritt in 1.2.0rc1 nicht mehr auf.
* Bestätigt: Der 1.1.0rc1-Fund UAT-DE-001 (Beispiel-Hostname `blackpanther` statt echtem
  Hostnamen) ist behoben – `setup` setzt `host_name` korrekt über `gethostname()`.
* Englischer Durchlauf noch offen (braucht eine zweite frische VM oder ein zurückgesetztes
  Abbild derselben VM).

## Sprint 71 – UAT-Anleitung für 1.2.0rc1

### Added

* `docs/reports/USER_ACCEPTANCE_TEST_1.2.0rc1.md`: vollständige, schrittweise
  UAT-Anleitung für die fällige VM-Validierung (fokussiert auf Neuinstallation, nicht
  Upgrade). Deckt den kompletten Ablauf ab und legt besonderen Fokus auf die seit 1.1.0
  neuen Befehle (`settings`, `change-password`, `export-config`/`import-config`) sowie die
  strukturierte `doctor`-Ausgabe. Deutsch/Englisch-Unterschiede (Bestätigungs-Buchstaben
  `[j/N]` vs. `[y/N]`, Doctor-Statuslabels, Timer-Statustexte) explizit tabellarisch
  aufgeführt. Enthält leere Acceptance-Record- und Findings-Vorlagen sowie eine
  Entscheidungsregel, analog zu `docs/reports/FINAL_USER_ACCEPTANCE_TEST_1.1.0rc1.md`.
* `docs/reports/RELEASE_CANDIDATE_1.2.0rc1.md`: Verweis auf die neue UAT-Anleitung ergänzt.

## Sprint 70 – Version 1.2.0 Release Candidate 1

### Changed

* Package version advanced from `1.2.0.dev0` to `1.2.0rc1` for RC validation.
* Feature freeze begins: from this point on, only bug fixes, documentation and translation
  corrections are applied until the 1.2.0 release.
* Local quality gate passed: `ruff check .`, `python -m compileall`, `pytest` (182 tests),
  `python -m build`, `python -m twine check dist/*` – all green.
* Wheel built: `linux_backup_manager-1.2.0rc1-py3-none-any.whl`, SHA-256
  `0f012f29125f59104422c2d70d6f021f683b25489a39e9c3a47adac9daa9c9f9`.

### Scope of 1.2.0

Product features since 1.1.0 (Sprints 46–54): automatic repository cleanup and retention
defaults, systemd timer diagnostics, desktop integration, `change-password`, interactive
`settings` menu, structured `doctor` output, `restic --json` parsing, `export-config`/
`import-config`. Process and documentation work (Sprints 55–69): license and security
policy, full GitHub publication, and complete bilingual documentation. User tutorials and
additional examples are deferred past 1.2.0 and do not block this release.

### Pending before release

* Managed fresh-install validation in an isolated VM (manual, not automatable in this
  environment).
* Manual UAT in German and English.
* Merge to `main` after UAT passes.

## Sprint 69 – Bilinguale Dokumentation abgeschlossen: FAQ, Konfiguration, systemd

### Added

* `docs/de/FAQ.md`, `docs/de/CONFIGURATION.md`, `docs/de/SYSTEMD.md`: vollständige deutsche
  Übersetzungen – letzte Gruppe der bilingualen Dokumentation. Damit sind alle 8
  vorgesehenen nutzerorientierten Docs zweisprachig verfügbar.
* Sprachumschalter-Links in beiden Richtungen für alle drei Dokumente.
* `README.md`- und `docs/de/README.md`-Dokumentationslisten vervollständigt (Platzhalter aus
  Sprint 67/68 durch echte Links ersetzt).

### Fixed

* `docs/FAQ.md` enthielt veraltete Antworten: "Kann ich ein NAS verwenden?" behauptete
  fälschlich "noch nicht", obwohl NAS-Unterstützung bereits vor 1.1.0 implementiert wurde;
  die "Future Features"-Liste war komplett überholt (alle fünf Punkte bereits erledigt oder
  in Arbeit). Vor der Übersetzung im englischen Original korrigiert, um den Fehler nicht in
  beide Sprachen zu übernehmen.

## Sprint 68 – Bilinguale Dokumentation: Installation, Restore, Recovery

### Added

* `docs/de/INSTALL.md`, `docs/de/RESTORE.md`, `docs/de/RECOVERY.md`: vollständige deutsche
  Übersetzungen.
* Sprachumschalter-Links in beiden Richtungen für alle drei Dokumente.
* `README.md`-Dokumentationsliste um die drei deutschen Links ergänzt.

### Fixed

* `docs/de/README.md` verlinkte bereits auf noch nicht existierende
  `docs/de/CONFIGURATION.md`/`FAQ.md`/`SYSTEMD.md` (vorausschauend in Sprint 67 gesetzt).
  Bis zur Übersetzung dieser drei Dokumente zeigen die Links vorübergehend auf die
  englischen Originale.

## Sprint 67 – Bilinguale Dokumentation: README und User Guide

### Added

* `docs/de/README.md`: vollständige deutsche Übersetzung der README.
* `docs/de/USER_GUIDE.md`: vollständige deutsche Übersetzung des Benutzerhandbuchs.
* Gegenseitige Sprachumschalter-Links am Kopf von `README.md`/`docs/de/README.md` und
  `docs/USER_GUIDE.md`/`docs/de/USER_GUIDE.md`.
* `README.md`-Dokumentationsliste: Link zur deutschen USER_GUIDE ergänzt.

### Changed

* `docs/ROADMAP.md`: Fortschritt bei "Complete German and English documentation"
  dokumentiert (2 von 8 vorgesehenen Dokumenten fertig); Architektur-/Prozess-Docs bleiben
  bewusst englisch-only.
* `CLAUDE.md`-Dokumentationsstruktur um `docs/de/*.md` ergänzt.

## Sprint 66 – Fix: installer-Test hing an echtem `restic`-Binary

### Fixed

* `tests/test_installer.py::test_dry_run_does_not_create_files` konstruierte den
  `Installer` ohne gemockten `runner` – dadurch rief `_preflight()` echte
  `subprocess`-Aufrufe an `restic version` auf. Lief lokal nur durch, weil `restic`
  installiert war; schlug auf dem GitHub-Actions-Runner (kein `restic` vorhanden) fehl.
  Fund: erster echter CI-Lauf auf GitHub nach der Veröffentlichung (Sprint 65) zeigte den
  Fehler auf `main`. Behoben durch Ergänzen von `runner=Mock(return_value=completed(stdout="3.12\n"))`,
  passend zum in allen anderen Installer-Tests verwendeten Dependency-Injection-Muster.
* Derselbe Bug bestand unverändert auch auf dem `main`-Branch (stammt aus Sprint 44 /
  v1.1.0). Auf Nutzerentscheidung direkt dort gefixt (Commit `fix: mock restic in installer
  dry-run test`, bewusste Abweichung vom Standard-"nur via PR aus develop"-Workflow, da reine
  Testisolation ohne Verhaltensänderung) und zu GitHub gepusht. Beide CI-Läufe (`main` und
  `develop`) sind jetzt grün.

## Sprint 65 – Repository öffentlich auf GitHub veröffentlicht

### Added

* Öffentliches Repository unter https://github.com/marcelsaa/linux-backup-manager
  angelegt (leer initialisiert, kein README/.gitignore/License von GitHub).
* Gefilterte Kopie (frisch regeneriert auf Stand Sprint 64, inkl. Autor-E-Mail-Korrektur
  und Ausschluss von `docs/reports/`/`CLAUDE.md`) gepusht: `main` (Default-Branch),
  `develop`, Tags `v1.0.1`/`v1.1.0`/`v1.1.0rc2`.
* Issues in den Repository-Einstellungen deaktiviert (`hasIssuesEnabled: false`).
* Erster CI-Lauf auf GitHub Actions automatisch durch den Push ausgelöst.

### Notes

* Der GitHub-Push scheiterte zunächst, da das `gh`-Token nicht den `workflow`-Scope hatte
  (nötig für `.github/workflows/ci.yml`); nach `gh auth refresh -h github.com -s workflow`
  erfolgreich abgeschlossen.
* Das eigentliche Arbeits-Repo (`/home/marcel/Projekte/linux-backup-manager`) war zu keinem
  Zeitpunkt Ziel des Pushes und bleibt unverändert; die lokale gefilterte Kopie unter
  `/home/marcel/Projekte/linux-backup-manager-public.git` bleibt als Vorlage für künftige
  Aktualisierungen (z. B. den v1.2.0-Release) bestehen.

## Sprint 64 – Versions- und Roadmap-Konsistenz

### Changed

* `pyproject.toml`: Version von `1.1.0` auf `1.2.0.dev0` gesetzt, passend zur seit Sprint 46
  laufenden v1.2.0-Entwicklung. Folgt derselben Konvention wie der `1.1.0.dev0`-Bump direkt
  nach dem 1.0.1-Release.
* `docs/ROADMAP.md`: Checkbox "Begin Version 1.2 development after the Version 1.1.0
  release" abgehakt – war seit Sprint 46 faktisch erfüllt, aber nie markiert.

## Sprint 63 – README für externe Zielgruppe und History-Bereinigung vorbereitet

### Changed

* `README.md`: CI-/Lizenz-/Python-Badges ergänzt, Installationsabschnitt um konkreten
  Releases-Link und Klon-URL erweitert, neue "Example Session" mit illustrativem
  Terminal-Transkript (keine echten Screenshots, da CLI-Tool ohne Bildmaterial),
  Dokumentationsliste in klickbare Links umgewandelt, neuer
  "Contributing & Support"-Abschnitt (verweist auf `CONTRIBUTING.md`/`SECURITY.md`),
  veralteten Feature-Freeze-Hinweis im "Project Status"-Abschnitt korrigiert.

### Added (außerhalb des Arbeits-Repos)

* Separate, gefilterte bare Kopie unter
  `/home/marcel/Projekte/linux-backup-manager-public.git`, erzeugt via `git-filter-repo`:
  `docs/reports/` und `CLAUDE.md` aus der gesamten Historie entfernt und verifiziert nicht
  mehr als Objekte vorhanden; Autor-E-Mail der ersten vier Commits per `--mailmap` auf
  `marcel.saager@gmx.de` vereinheitlicht; interner Tag `backup-v1.0.0-before-refactor`
  entfernt; `refs/replace/*`- und `refs/codex/*`-Nebenreferenzen bereinigt;
  `git gc --prune=now` durchgeführt. Das eigentliche Arbeits-Repo bleibt davon unberührt.
  Funktionaler Sanity-Check (`compileall` + `pytest`, 182 Tests) in einem Checkout der
  gefilterten Kopie erfolgreich.

## Sprint 62 – CLAUDE.md-Veröffentlichung und Co-Authored-By entschieden

### Decided

* `CLAUDE.md` bleibt privat, analog zu `docs/reports/`. Enthält keine personenbezogenen
  Daten (geprüft), ist aber ein internes Arbeitsanweisungs-Dokument für den KI-Assistenten
  ohne Mehrwert für die Zielgruppe – passt zum Engagement-Modell (Sprint 60). Muss bei der
  späteren History-Filterung ebenfalls ausgeschlossen werden.
* `Co-Authored-By: Claude Sonnet` im Git-Verlauf bleibt unverändert stehen. Anders als der
  Tailscale-Fund (Sprint 58) ist das kein Datenschutzrisiko, sondern eine zutreffende
  Attribution; ein History-Rewrite dafür wäre eine sachlich unbegründete Verfälschung.
* `docs/ROADMAP.md` entsprechend aktualisiert (beide Checkboxen im Abschnitt
  "Repository-Inhalt" abgehakt).

## Sprint 61 – Distributionskanal und Versionierung entschieden

### Decided

* Distributionskanal für die Veröffentlichung: **GitHub Releases** (Wheel + `installer.py` +
  veröffentlichter SHA-256), **kein PyPI**. `installer.py` baut eine eigene verwaltete venv
  mit Desktop-Integration, Upgrade-Erkennung und Rollback auf, was zu einem `pip
  install`-Fluss nicht passt. Der freie PyPI-Name (Sprint 59) bleibt als spätere Option
  offen.
* Versionierung: Die bestehende Tag-Historie (`v1.0.1`, `v1.1.0`) wird beim späteren
  History-Rewrite behalten, nicht verworfen. `v1.2.0` ist der erste Tag mit angehängten
  GitHub-Release-Assets, nicht der erste Tag überhaupt. Der interne Tag
  `backup-v1.0.0-before-refactor` wird nicht mit veröffentlicht.
* `docs/ROADMAP.md` entsprechend aktualisiert (beide Checkboxen im Abschnitt
  "Distribution" abgehakt).

## Sprint 60 – Engagement-Modell für die Veröffentlichung

### Added

* Neue `CONTRIBUTING.md`: legt explizit fest, dass die Veröffentlichung eine reine Geste ist –
  keine Support-Verpflichtung, keine Zusage zur Prüfung oder Annahme von Pull Requests, Fork
  statt Feature-Wunsch als empfohlener Weg. Sicherheitsmeldungen bleiben über `SECURITY.md`
  ausgenommen.

### Decided

* Engagement-Modell für die Veröffentlichung festgelegt: öffentlich sichtbar/forkbar, aber
  Issues werden in den GitHub-Repository-Einstellungen deaktiviert (manueller Schritt nach
  Repo-Erstellung), Pull Requests erzeugen keine Verpflichtung. Details in
  `docs/ROADMAP.md`, Abschnitt "Engagement-Modell".
* `.github/ISSUE_TEMPLATE/` aus Sprint 59 bleibt trotz geplanter Issue-Deaktivierung bestehen
  (auf Wunsch des Nutzers), für den Fall einer künftigen Kursänderung.
* Contribution-Richtlinien-Checkbox in `docs/ROADMAP.md` abgehakt.

## Sprint 59 – PyPI-Namensprüfung und Issue-Templates

### Added

* `.github/ISSUE_TEMPLATE/bug_report.md` und `feature_request.md`: strukturierte
  GitHub-Issue-Vorlagen für die geplante öffentliche Veröffentlichung. Der
  Feature-Request-Vorlage liegt ein Scope-Check gemäß der Design-Philosophie
  (`docs/ROADMAP.md`) bei.

### Changed

* `docs/ROADMAP.md`: Paketnamen-Verfügbarkeit geprüft (`linux-backup-manager` ist auf PyPI
  nicht registriert, `404` bei `pypi.org/pypi/linux-backup-manager/json`) und Checkbox
  abgehakt. Issue-Templates-Checkbox abgehakt.

## Sprint 58 – CI-Workflow-Review und Git-Historie-Fund

### Changed

* `docs/ROADMAP.md`: Roadmap-Punkt "GitHub Actions / CI für öffentliches Repo prüfen"
  abgehakt – `.github/workflows/ci.yml` enthält keine Secrets, setzt
  `permissions: contents: read` und referenziert keine internen Pfade.

### Found

* Die ersten vier Commits (Projektstart, 25.06.2026) tragen als Autor-E-Mail die reale
  Tailscale-MagicDNS-Adresse (`marcel@blackpanther.tail6983d3.ts.net`) statt der regulären
  Adresse. Als neuer Punkt unter "Repository-Inhalt" in `docs/ROADMAP.md` vermerkt; Korrektur
  per History-Rewrite ist Teil der Bereinigung unmittelbar vor der Veröffentlichung, nicht
  Teil dieses Sprints.

## Sprint 57 – Kuratierte Entwicklungsdokumentation

### Added

* Neue `docs/DEVELOPMENT.md`: öffentliche Zusammenfassung der Entwicklungsmethodik
  (iterative Sprints, verpflichtendes Quality Gate, Release-Candidate-Prozess) ohne
  personenbezogene Details oder Sprint-Einzelheiten.
* `README.md`-Dokumentationsliste um "Development Process" ergänzt.

### Decided

* `docs/reports/` (Sprint- und Validierungsberichte) bleibt privat und wird vor der
  GitHub-Veröffentlichung aus der Git-Historie gefiltert statt redigiert – enthält reale
  Pfade und Hostnamen, die vor dem ersten öffentlichen Push entfernt werden müssen.
* `docs/ROADMAP.md` entsprechend aktualisiert: Entscheidung zu Sprint-Berichten
  dokumentiert; Entscheidung zu `CLAUDE.md`-Veröffentlichung bleibt separat offen.

## Sprint 56 – Fehlende Befehlsdokumentation nachgezogen

### Changed

* `README.md`: Befehlsübersicht um `settings`, `export-config`, `import-config` und
  `change-password` ergänzt (Sprints 49/51/54 waren dort nie dokumentiert).
* `docs/USER_GUIDE.md`: Vier neue Abschnitte für dieselben Befehle ergänzt, inklusive
  Command-Overview-Tabelle. Beschreibt Menüoptionen von `settings`, das sequenzielle
  Vorgehen bei `change-password` (inkl. Verhalten bei Teilfehlern) sowie Validierungs-
  und Backup-Verhalten von `export-config`/`import-config`.

## Sprint 55 – Sicherheits-Meldeweg und Lizenz-Dokumentation

### Added

* Neue `SECURITY.md`: privater Meldeweg für Sicherheitslücken (E-Mail statt öffentlichem
  Issue), da LBM Passwortdateien und Repository-Zugänge verwaltet.

### Changed

* `README.md`: Lizenzabschnitt um einen Hinweis zur Restic-Abhängigkeit ergänzt (Restic:
  BSD-2-Clause, kompatibel mit GPL-3.0; keine Code-Verflechtung, da Restic als externes
  Systemwerkzeug aufgerufen wird).
* `docs/ROADMAP.md`: Checkboxen "Lizenzwahl bestätigen", "Restic-Lizenzkompatibilität
  dokumentieren" und "`SECURITY.md` erstellen" im Abschnitt "GitHub-Veröffentlichung"
  abgehakt.

## Sprint 54 – Konfigurationsexport und -import

### Added

* Neuer Befehl `backup-manager export-config`: kopiert die aktuelle Konfigurationsdatei
  an einen vom Nutzer gewählten Zielort. Überschreiben wird bestätigt, bevor es passiert.
* Neuer Befehl `backup-manager import-config`: liest eine externe Konfigurationsdatei,
  validiert sie vollständig (AppConfig + Pydantic), sichert die bestehende Konfiguration
  als `.bak` und ersetzt sie atomar.
* `ConfigExportService` und `ConfigImportService` in `lbm/services/config_transfer.py`;
  Spracherkennung aus der vorhandenen Konfiguration mit Fallback auf Deutsch.
* 12 neue i18n-Schlüssel unter `config_transfer:` in Deutsch und Englisch.
* 8 neue Tests in `tests/test_config_transfer.py`.

## Sprint 53 – JSON-Parsing für Backup-Ausgabe

### Changed

* `restic backup` wird jetzt mit `--json` aufgerufen. Die Ausgabe wird strukturiert via
  `_parse_backup_json()` ausgewertet statt durch fragile Regex-Muster.
* Neue Hilfsfunktionen `_format_bytes()` und `_format_duration()` formatieren Bytes und
  Sekunden aus der JSON-Ausgabe in lesbare Strings.
* `import re` aus `restic.py` entfernt.

## Sprint 52 – Verbesserte Diagnose-Darstellung

### Changed

* `backup-manager doctor` gliedert die Ausgabe jetzt in sechs Abschnitte mit Überschriften:
  Konfiguration, Programme, Sicherheit, Backup-Ziele, Repositories, Zeitplan.
* Neue Zusammenfassungszeile am Ende zeigt die Anzahl von OK / Warnung(en) / Fehler /
  Übersprungen auf einen Blick.
* Gesamtstatus am Ende farbig hervorgehoben: grün (OK), gelb (Warnung), rot (Fehler).
* Status-Symbole (✓ / ! / ✗ / -) farbig kodiert in der Ergebnisliste.
* 7 neue i18n-Schlüssel unter `doctor:` in Deutsch und Englisch.

## Sprint 51 – Interaktives Einstellungsmenü

### Added

* Neuer Befehl `backup-manager settings`: zeigt ein nummeriertes Menü zum gezielten Ändern
  einzelner Einstellungen (Sprache, Backup-Pfade, Backup-Ziele, Zeitplan).
* Nach jeder Änderung wird die Konfiguration atomar gespeichert (`.bak`-Backup) und das
  Menü kehrt zurück, bis der Nutzer "Beenden" wählt.
* 10 neue i18n-Schlüssel unter `settings:` in Deutsch und Englisch.

## Sprint 50 – Refactoring: `_is_yes()` Utility

### Changed

* `_is_yes()`-Methode aus fünf Klassen (`RepositoryMaintenanceService`, `RestoreService`,
  `RecoverySheetService`, `PasswordChangeService`, `SetupWizard`) in eine gemeinsame
  Utility-Funktion `lbm.utils.prompts.is_yes()` extrahiert. Kein Verhaltensunterschied.

## Sprint 49 – Passwort ändern

### Added

* Neuer Befehl `backup-manager change-password`: ändert das Repository-Passwort in allen
  konfigurierten Repos sequenziell, ersetzt die Passwortdatei atomar und bietet danach die
  Neuerstellung des Recovery Sheets an.
* `ResticRepository.change_password(new_password_file)`: ruft `restic key passwd
  --new-password-file` auf, kein interaktiver Input, kein `shell=True`.
* Neuer `PasswordChangeService` in `services/password.py`.
* Schlägt das zweite Repo fehl, werden die bereits geänderten Repos namentlich gemeldet und
  die Passwortdatei bleibt unverändert.
* 15 neue i18n-Schlüssel unter `password_change:` in Deutsch und Englisch.

## Sprint 48 – Desktop-Integration

### Added

* Der Installer bietet am Ende jeder erfolgreichen Installation und jedes Upgrades optional an,
  einen Desktop-Shortcut anzulegen:
  * **Anwendungsmenüeintrag** (`~/.local/share/applications/linux-backup-manager.desktop`) –
    erscheint im Systemmenü aller großen Desktop-Umgebungen (GNOME, KDE, XFCE u.a.).
  * **Desktop-Symbol** (`~/Desktop/linux-backup-manager.desktop`) – nur wenn das Verzeichnis
    existiert und der Nutzer zustimmt.
* Die `.desktop`-Datei verwendet `Terminal=true` und `Exec=<Pfad-zum-Launcher>`, sodass der
  Eintrag nach Upgrades ohne Anpassung weiterhin funktioniert.
* Mit `--yes` wird der Anwendungsmenüeintrag automatisch erstellt; das Desktop-Symbol wird
  in nicht-interaktiven Läufen nicht angelegt.
* Falls `update-desktop-database` verfügbar ist, wird es nach dem Schreiben aufgerufen.
* `Layout` erhält vier neue Properties: `applications_dir`, `desktop_entry`, `desktop`,
  `desktop_icon`.

## Sprint 47 – systemd-Timer-Diagnose und Backup-Alter

### Added

* `DoctorService` prüft nun den systemd-Timer-Status (`linux-backup-manager-daily.timer`):
  aktiv/geplant (OK), installiert aber nicht aktiv (WARNUNG), nicht installiert (WARNUNG),
  systemd fehlt (WARNUNG), Schedule nicht konfiguriert (ÜBERSPRUNGEN).
* Letztes Backup wird in `doctor` und `status` mit Altersangabe angezeigt
  (z.B. `28.06.2026 20:30:00 CEST (vor 2 Tagen)`).
* `doctor` warnt, wenn das Backup gemessen am konfigurierten Intervall überfällig ist.
* Neue i18n-Schlüssel: `common.age_days`, `common.age_hours`, `common.age_minutes`;
  `doctor.timer*`, `doctor.last_backup_overdue` – in Deutsch und Englisch.

## Sprint 46 – Automatisches Repository-Cleanup und Retention-Defaults

### Added

* `RetentionConfig` erhält Standardwerte: `keep_daily=14`, `keep_weekly=8`, `keep_monthly=12`,
  `keep_yearly=3`. Neu erstellte Konfigurationen ohne expliziten `retention:`-Block verwenden
  diese Werte automatisch.
* `ResticRepository.cleanup()`: kombiniert `forget` + `prune` in einem Schritt, gibt `bool`
  zurück.
* `BackupService` ruft nach jedem erfolgreichen Backup automatisch Cleanup auf. Ein
  Cleanup-Fehler gibt eine Warnung aus, beeinflusst aber nicht den Backup-Exit-Code.
* Neue i18n-Schlüssel `backup.cleanup_start`, `backup.cleanup_done`, `backup.cleanup_failed`
  in Deutsch und Englisch.

---

# v1.1.0 – 2026-06-30

## Version 1.1.0 Release Candidate 3

### Changed

* Package version advanced from `1.1.0rc2` to `1.1.0rc3` for Sprint 44 validation

## Sprint 44 – Managed Installation and Upgrade

### Added

* Standalone `installer.py` for managed fresh installation and Version 1.0.1 upgrade
* SHA-256 and package-metadata verification before any installation action
* Write-free `--dry-run` mode showing the detected mode and planned actions without side effects
* Detection of fresh, supported 1.0.1, already-current and partial/unsupported installation states
* Preflight checks for Python 3.12+, Restic, free disk space, write permissions and NAS/USB
  repository reachability before any venv or file is created
* Versioned virtual environment layout under
  `~/.local/share/linux-backup-manager/versions/<version>/`
* Atomic launcher cutover: symlink is switched via a temporary file and `os.replace`
* Automatic rollback with invariant verification on cutover failure: config, password, units,
  launcher and repository state must be byte-identical to the captured pre-upgrade baseline
* Upgrade backup directory at `~/.local/share/linux-backup-manager/upgrade-backups/` for recovery
* 16 dedicated installer tests covering wrong hash, partial state, old Python, unavailable Restic,
  insufficient space, injected cutover failure and idempotent rerun

### Validation

* Passed the complete automated gate with 121 tests (including 16 installer tests), Ruff and Python
  byte-compilation
* Passed isolated integration validation: real 1.0.1 install, managed upgrade, post-upgrade backup
  and byte-identical restore
* Passed the pristine-VM German fresh-install UAT for the exact `1.1.0rc3` wheel and `installer.py`
  (SPRINT\_44\_FRESH\_DE\_PASSED)
* Passed the pristine-VM German 1.0.1 upgrade UAT: negative preflight, dry-run, upgrade, preserved
  config/password/timers, post-upgrade backup and SHA-256-verified restore
  (SPRINT\_44\_UPGRADE\_DE\_PASSED)
* Passed the independent pristine-VM English fresh-install UAT with fully English application output
  (SPRINT\_44\_FRESH\_EN\_PASSED)
* Approved Version 1.1.0rc3 for migration from Version 1.0.1 after all applicable acceptance gates
  passed without workaround or unresolved finding

## Version 1.1.0 Release Candidate 2

### Changed

* Package version advanced from `1.1.0rc1` to `1.1.0rc2` for Sprint 43 validation

## Sprint 43 – Setup and UAT Hardening

### Fixed

* Fresh first-user configurations now use the real system host name instead of retaining the
  packaged example value `blackpanther`
* Interactive setup validates selected USB and NAS targets before writing configuration and offers
  a correction loop for unavailable targets
* Setup displays a final host, path, target and schedule summary before configuration is persisted
* systemd user timers are no longer installed when password, Restic or repository setup is
  incomplete
* Interactive EOF now returns a localized controlled Exit `1` instead of a Python traceback
* The startup due timer now waits from timer activation, preventing an immediate catch-up race when
  setup occurs long after boot

### Validation

* Added German and English regression coverage for target correction, summary output, real host
  identity, scheduler gating, EOF handling and timer activation semantics
* Passed the complete automated gate with 105 tests, Ruff and Python byte-compilation
* Passed the pristine-VM German external UAT for the exact `1.1.0rc2` wheel, including target
  correction, host identity, timer delay, restore metadata, EOF handling and cleanup
* Passed the independent pristine-VM English external UAT with the same exact wheel and fully
  English application output
* Approved Version 1.1.0rc2 for migration from Version 1.0.1 after both external passes completed
  without workaround or unresolved finding

## Version 1.1.0 Release Candidate 1

### Changed

* Package version advanced from `1.1.0.dev0` to `1.1.0rc1`
* Version 1.1 entered feature freeze after the successful Sprint 41 release gate
* Until Version 1.1.0, changes are limited to bug fixes, documentation and translations

## Sprint 42 – Restore Finalization

### Validation

* Fully analyzed the sandbox-specific `lchown` restore failure against normal unprivileged Linux
  behavior and official Restic exit semantics
* Confirmed that Linux Backup Manager must continue propagating every nonzero Restic restore status
* Added regression coverage preventing `lchown` errors from being reclassified as success
* Passed the complete quality gate with 100 tests
* Rebuilt and freshly installed the `1.1.0rc1` wheel and recorded its SHA-256 checksum
* Passed independent German and English First-User workflows with real isolated systemd user timers
* Passed full restores with matching SHA-256 hashes, modes and modification timestamps
* Approved Version 1.1.0rc1 for migration from Version 1.0.1

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

## Sprint 35 – Recovery Foundation

### Added

* `recovery-info` command showing recovery-critical paths, targets and emergency steps
* Recovery information service that checks password-file metadata without reading its content
* Recovery and password-safety guide for preparation, system replacement and password loss
* Regression tests ensuring recovery output never contains the repository password

### Changed

* Password creation now requires explicit acknowledgement that repository passwords cannot be reset
* Setup explains that the password or a protected password-file copy must be stored separately
* Roadmap reorganized around Version 1.1 safety and maintainability and Version 1.2 user experience

## Sprint 36 – Password-Free Recovery Sheet

### Added

* `recovery-sheet` command with a selectable output path and safe default location
* Password-free recovery document containing targets, paths, emergency commands and manual fields
* Explicit overwrite confirmation for existing recovery documents
* Atomic file replacement and restrictive `0600` permissions
* Typed write-error handling through the central application error path

### Security

* Recovery sheet generation never opens or copies the repository password file
* The generated document states prominently that it does not replace a protected password copy
* Users are instructed to store or print the sheet separately from computer and repository

## Sprint 37 – Read-Only Doctor Diagnostics

### Added

* `doctor` command for a single support and self-check report
* Aggregated configuration, password-file permission, Restic, USB, NAS and repository diagnostics
* Last successfully recorded backup timestamp with a warning when no timestamp is available
* Explicit `OK`, `WARNUNG`, `FEHLER` and `ÜBERSPRUNGEN` result states
* Nonzero command exit status when at least one diagnosis fails

### Safety

* Doctor checks are read-only and contain no repair action
* The command never initializes repositories, creates backups, changes configuration or alters
  systemd timers

## Sprint 38 – Internationalization Foundation

### Added

* Central `LanguageService` with nested YAML message-catalog support and value formatting
* Packaged German and English language catalogs
* Interactive `de`/`en` selection during initial setup and configuration editing
* Persisted `system.language` setting with strict configuration validation
* English, German and stable-key fallback behavior for missing messages or catalogs

### Compatibility

* Existing configurations without a language setting continue to load and default to German
* Existing CLI output remains largely unchanged until later translation sprints

## Sprint 39 – Core CLI Internationalization

### Added

* Complete German and English catalogs for `status`, `doctor`, `health` and `setup`
* Localized setup prompts, validation messages, password warnings and repository diagnostics
* Localized target-resolution and scheduler-installation messages used by core workflows
* German and English regression tests for all four migrated commands

### Changed

* Status, doctor and health labels and result states now resolve through `LanguageService`
* Setup loads the configured language before printing its header and switches immediately after a
  new language selection
* Shared health checks, repository target resolution and systemd scheduler accept the selected
  language while preserving German defaults for existing callers

## Sprint 40 – Complete CLI Internationalization

### Added

* German and English messages for backup, restore, snapshot and repository-maintenance commands
* German and English recovery information and generated recovery-sheet content
* Localized backup-due decisions, CLI help and keyboard-interruption messages
* Installed command-group regression tests for all remaining English workflows

### Changed

* Backup, restore, maintenance and recovery services now resolve user-facing text through
  `LanguageService`
* Successful Restic operations use consistent application translations while raw external errors
  and diagnostic output remain unchanged
* The roadmap now marks the complete switchable German/English CLI as implemented

## Sprint 41 – 1.1 Release Candidate Stabilization

### Fixed

* Failed Restic restores now propagate a nonzero command-line exit status

### Changed

* Release installation checks now require the generated wheel instead of a source checkout
* The QA plan now requires isolated German and English backup-and-restore end-to-end tests
* Development and stable version claims in the installation and QA documentation were aligned

### Validated

* German and English catalogs retain matching keys and format placeholders
* The complete Python 3.12 quality gate, distributions and fresh wheel installation pass locally
* Real local Restic repositories complete backup, snapshot, integrity and byte-identity checks

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
