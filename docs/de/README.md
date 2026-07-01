# Linux Backup Manager

[![CI](https://github.com/marcelsaa/linux-backup-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/marcelsaa/linux-backup-manager/actions/workflows/ci.yml)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](../../LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](../../pyproject.toml)

**[English version](../../README.md)**

> **Zuverlässige Linux-Backups sollten einfach sein.**

Linux Backup Manager (LBM) ist eine quelloffene Kommandozeilenanwendung, die das Erstellen,
Verwalten und Wiederherstellen von Backups unter Linux vereinfacht.

Statt Restic-Repositories, Passwortdateien und Backup-Ziele manuell zu konfigurieren, bietet
LBM einen interaktiven Setup-Assistenten, der Nutzer durch die vollständige Ersteinrichtung
führt. Nach der Konfiguration lassen sich alle Backup- und Wartungsaufgaben über eine
einheitliche Kommandozeilen-Oberfläche ausführen.

LBM legt den Fokus auf Verlässlichkeit, vorhersagbares Verhalten und langfristige
Wartbarkeit und baut dabei auf dem bewährten Open-Source-Backup-Werkzeug **Restic** auf.

---

# Warum Linux Backup Manager?

Verlässliche Backups zu erstellen sollte keine umfangreichen Kenntnisse von
Backup-Software erfordern.

Linux Backup Manager wurde mit folgenden Zielen entwickelt:

* Einfache Ersteinrichtung
* Verlässlicher Backup-Ablauf
* Einheitliche Kommandozeilen-Oberfläche
* Klare und handlungsleitende Fehlermeldungen
* Minimaler Konfigurationsaufwand
* Langfristige Wartbarkeit

Das Projekt richtet sich an Linux-Nutzer, die eine verlässliche Backup-Lösung wollen, ohne
Restic-Repositories oder komplexe Konfigurationsdateien manuell verwalten zu müssen.

---

# Funktionen

## Einfache Einrichtung

* Interaktiver Setup-Assistent
* Automatische Konfigurationserzeugung
* Sicheres interaktives Bearbeiten bestehender Konfigurationen mit automatischer Sicherung
* Automatische Erstellung der Passwortdatei
* Ausdrücklicher Hinweis während der Einrichtung, dass das Passwort nicht wiederherstellbar ist
* Recovery-Metadaten und Notfallanweisungen, ohne das Passwort preiszugeben
* Optionales passwortfreies Recovery-Dokument mit sicheren Dateiberechtigungen
* Automatische Repository-Initialisierung
* Klare Unterscheidung zwischen fehlendem Repository und ungültigem Repository-Passwort
* XDG-konformes Konfigurationsverzeichnis

## Backup

* Restic-basierte Backups
* Unterstützung für USB-Backups
* Unterstützung für NAS-Backups auf eingehängte Netzwerkfreigaben
* Parallele Backups auf mehrere Ziele
* Nutzerkonfigurierbare Backup-Zeit und -Intervall über systemd-User-Timer
* Sofortiges Nachhol-Backup, wenn das konfigurierte Intervall überschritten wurde
* Konfigurierbare Backup-Pfade
* Konfigurierbare Ausschluss-Muster

## Wiederherstellung

* Snapshot-Auswahl
* Geführter Restore-Ablauf
* Wiederherstellung in ein separates Zielverzeichnis

## Repository-Wartung

* Repository-Integritätsprüfungen
* Repository-Statistiken
* Snapshot-Verwaltung
* Aufbewahrungsrichtlinie (Retention)
* Repository-Bereinigung (Prune)

## Bedienerfreundlichkeit

* Farbige Konsolenausgabe
* Klare Fehlermeldungen
* Einheitliche Befehlsstruktur
* Robuster Ersteinrichtungsablauf
* Read-only-`doctor`-Diagnose für Konfiguration, Zugangsdaten, Ziele und Repositories
* Vollständige deutsche/englische Kommandozeilenausgabe mit Katalog-Fallback

---

# Voraussetzungen

Linux Backup Manager benötigt:

* Linux
* Python 3.12 oder neuer
* Restic

---

# Installation

Lade das Wheel und `installer.py` von der [Releases-Seite](https://github.com/marcelsaa/linux-backup-manager/releases)
herunter und führe den mitgelieferten, verwalteten Installer aus. Er prüft den
veröffentlichten SHA-256-Hash, führt schreibfreie Preflight-Checks durch und wählt
automatisch zwischen Neuinstallation oder dem unterstützten Upgrade-Pfad von Version 1.0.1:

```bash
python3 installer.py linux_backup_manager-1.1.0-py3-none-any.whl \
  --sha256 <VERÖFFENTLICHTER_SHA256> --dry-run
```

Wiederhole den Befehl ohne `--dry-run` erst, nachdem alle Prüfungen erfolgreich waren. Siehe
`docs/de/INSTALL.md` für Rollback-Garantien und den vollständigen Befehl.

Für die Entwicklung aus dem Quellcode das Repository klonen und hineinwechseln:

```bash
git clone https://github.com/marcelsaa/linux-backup-manager.git
cd linux-backup-manager
```

Anwendung installieren:

```bash
pip install .
```

Installation überprüfen:

```bash
backup-manager --version
```

---

# Schnellstart

Setup-Assistenten starten:

```bash
backup-manager setup
```

Erstes Backup erstellen:

```bash
backup-manager backup
```

Verfügbare Snapshots anzeigen:

```bash
backup-manager snapshots
```

Daten wiederherstellen:

```bash
backup-manager restore
```

Repository prüfen:

```bash
backup-manager check
```

Gesamte Backup-Umgebung diagnostizieren, ohne etwas zu verändern:

```bash
backup-manager doctor
```

---

# Beispielsitzung

Ein verkürzter, illustrativer Ablauf – der genaue Wortlaut hängt von der konfigurierten
Sprache und dem aktuellen Systemzustand ab:

```
$ backup-manager backup
Starte Backup folgender Pfade: /home/nutzer/Dokumente, /home/nutzer/Bilder
Backup erfolgreich
Neue Dateien: 1284, Datenmenge: 2,1 GiB neu, 47,3 GiB gesamt im Repository
Alte Snapshots werden bereinigt...
Alte Snapshots bereinigt.

$ backup-manager doctor
── Konfiguration ─────────────────────────────────
✓ Konfigurationsdatei            OK: gültig und lesbar
✓ Passwortdatei-Rechte           OK: 0600

── Backup-Ziele ──────────────────────────────────
✓ USB (LinuxBackup)              OK: eingehängt und beschreibbar

── Repositories ──────────────────────────────────
✓ USB-Repository                 OK: erreichbar, letztes Backup vor 2 Stunden

Zusammenfassung: 4 OK, 0 Warnungen, 0 Fehler
```

---

# Verfügbare Befehle

| Befehl                      | Beschreibung                                       |
| ---------------------------- | --------------------------------------------------- |
| `backup-manager setup`     | Interaktiver Setup-Assistent                         |
| `backup-manager settings`  | Einzelne Einstellungen interaktiv ändern             |
| `backup-manager export-config` | Aktuelle Konfigurationsdatei an einen anderen Ort kopieren |
| `backup-manager import-config` | Externe Konfigurationsdatei validieren und übernehmen |
| `backup-manager status`    | Systeminformationen anzeigen                         |
| `backup-manager health`    | Health-Checks ausführen                              |
| `backup-manager doctor`    | Read-only-Support-Diagnose ausführen                 |
| `backup-manager recovery-info` | Passwortsichere Recovery-Informationen anzeigen  |
| `backup-manager recovery-sheet` | Passwortfreies Recovery-Dokument erstellen      |
| `backup-manager change-password` | Repository-Passwort ändern                     |
| `backup-manager backup`    | Backup erstellen                                     |
| `backup-manager schedule-install` | Automatische Backups installieren und aktivieren |
| `backup-manager schedule-status` | Status des systemd-Timers anzeigen             |
| `backup-manager schedule-remove` | Automatische Backups deaktivieren              |
| `backup-manager snapshots` | Verfügbare Snapshots auflisten                       |
| `backup-manager restore`   | Daten aus einem Snapshot wiederherstellen             |
| `backup-manager stats`     | Repository-Statistiken anzeigen                      |
| `backup-manager check`     | Repository-Integrität prüfen                         |
| `backup-manager forget`    | Konfigurierte Aufbewahrungsrichtlinie anwenden       |
| `backup-manager prune`     | Unreferenzierte Repository-Daten entfernen           |

---

# Dokumentation

Ausführliche Dokumentation befindet sich im `docs/`-Verzeichnis.

* [Installationsanleitung](INSTALL.md)
* [Benutzerhandbuch](USER_GUIDE.md)
* [Konfigurationsreferenz](CONFIGURATION.md)
* [Restore-Anleitung](RESTORE.md)
* [Passwort-Sicherheit und Recovery-Leitfaden](RECOVERY.md)
* [FAQ](FAQ.md)
* [Anleitung für automatische Backups](SYSTEMD.md)

Die folgenden Dokumente sind bewusst nur auf Englisch verfügbar (projektinterne
Architektur- und Prozessdokumentation): [Architekturübersicht](../ARCHITECTURE.md),
[Qualitätssicherungs-Testplan](../QA_TESTPLAN.md), [Projekt-Roadmap](../ROADMAP.md),
[Entwicklungsprozess](../DEVELOPMENT.md), [Internationalisierungs-Leitfaden](../INTERNATIONALIZATION.md).

---

# Roadmap

Siehe [die Projekt-Roadmap](../ROADMAP.md) für abgeschlossene und geplante Arbeit
(nur auf Englisch verfügbar).

---

# Projektstatus

**Aktuelle stabile Version:** 1.1.0

Linux Backup Manager 1.1.0 ist die aktuelle stabile Version. Sie bringt einen eigenständigen,
verwalteten Installer, vollständige deutsche und englische Internationalisierung sowie einen
gehärteten Ersteinrichtungs-Assistenten. Die Artefakte werden lokal gebaut und nicht auf
PyPI veröffentlicht.

Die Kernfunktionalität wurde implementiert und durch automatisierte Tests, manuelle
Integrationstests und mehrere Ersteinrichtungsszenarien erfolgreich validiert.

Die Entwicklung der nächsten Version, 1.2.0, läuft. Siehe die
[Projekt-Roadmap](../ROADMAP.md) für abgeschlossene und geplante Arbeit.

---

# Mitwirken & Support

Linux Backup Manager ist ein persönliches Projekt, das öffentlich geteilt wird, damit andere
es lesen, nutzen und anpassen können. Es werden keine Mitwirkenden gesucht, und es gibt keine
Zusage, dass Issues oder Pull Requests bearbeitet werden – siehe [`CONTRIBUTING.md`](../../CONTRIBUTING.md)
für Details. Sicherheitslücken sind die einzige Ausnahme und können privat gemeldet werden;
siehe [`SECURITY.md`](../../SECURITY.md).

---

# Haftungsausschluss

Linux Backup Manager wird **"wie besehen"** bereitgestellt, ohne jegliche ausdrückliche
oder stillschweigende Gewährleistung.

Obwohl alle Anstrengungen unternommen wurden, um verlässliche Software bereitzustellen, wird
keine Garantie übernommen, dass die Software frei von Fehlern oder für jeden
Anwendungsfall geeignet ist.

Nutzer sind selbst dafür verantwortlich, ihre Backups zu überprüfen und Restore-Vorgänge
regelmäßig zu testen.

Der Autor übernimmt keine Haftung für Datenverlust oder andere Schäden, die aus der Nutzung
dieser Software entstehen.

---

# Lizenz

Linux Backup Manager ist unter der GNU General Public License v3.0 lizenziert.

Linux Backup Manager ruft die externe [Restic](https://restic.net/)-Binärdatei als
separates Systemwerkzeug auf; es gibt keine Code-Verflechtung zwischen den beiden Projekten.
Restic ist unter der BSD-2-Clause-Lizenz lizenziert, die mit GPL-3.0 kompatibel ist.

---

Copyright © 2026 Marcel Saager
