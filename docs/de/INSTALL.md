# Linux Backup Manager

# Installationsanleitung

**[English version](../INSTALL.md)**

**Version:** 1.3.0

---

## 1. Einführung

Diese Anleitung erklärt, wie der Linux Backup Manager (LBM) auf einem Linux-System
installiert und konfiguriert wird.

Der Installationsprozess wurde so gestaltet, dass nur wenige Schritte nötig sind. Nach der
Installation der benötigten Software führt der integrierte Setup-Assistent durch die
Ersteinrichtung.

Eine manuelle Bearbeitung von Konfigurationsdateien ist nicht erforderlich.

---

## 2. Systemvoraussetzungen

Der Linux Backup Manager wurde auf modernen Linux-Distributionen entwickelt und getestet.

### Mindestanforderungen

* Linux
* Python 3.12 oder neuer
* Restic
* systemd mit User-Services für optionale automatische Backups

### Empfohlen

* USB-Speichergerät für Backups
* Administrative Rechte für die Softwareinstallation

---

## 3. Benötigte Software

Vor der Installation von LBM prüfen, ob die benötigte Software verfügbar ist.

### Python

```bash
python3 --version
```

Python 3.12 oder neuer wird benötigt.

### Restic

```bash
restic version
```

Ist einer dieser Befehle nicht verfügbar, die fehlende Software über den Paketmanager der
Linux-Distribution installieren.

---

## 4. Verwaltete Installation oder Aktualisierung

`installer.py` neben das Release-Wheel legen. Den exakten, mit diesem Wheel veröffentlichten
SHA-256-Hash verwenden. Zuerst die schreibfreie Erkennung und den Preflight-Check ausführen:

```bash
python3 installer.py linux_backup_manager-1.3.0-py3-none-any.whl \
  --sha256 <VERÖFFENTLICHTER_SHA256> --dry-run
```

Der Preflight-Check prüft Python, Restic, freien Speicherplatz, Installationsrechte und – bei
einem Upgrade – jedes konfigurierte Ziel und Repository. Ist er
erfolgreich, denselben Befehl ohne `--dry-run` ausführen. Der Installer fragt nach
Bestätigung; für automatisierte Abläufe kann explizit `--yes` ergänzt werden.

Der verwaltete Weg legt entweder eine neue, versionierte Installation an oder aktualisiert
eine zuvor verwaltete Installation, unabhängig von deren Version. Dabei bleiben die alte
venv, Konfiguration, Passwortdatei und das Repository erhalten. Eine mehrdeutige,
unvollständige oder nicht unterstützte Installation wird ohne Änderungen abgelehnt.

Nach einem fehlgeschlagenen Umstieg (Cutover) stellt der Installer automatisch den alten
Launcher, die Units, exakten Timer-Zustände, Konfiguration, Passwort-Metadaten und den
logischen Repository-Zustand wieder her und überprüft sie. Eine kritische
Rollback-Warnung bedeutet, dass das aufbewahrte Recovery-Verzeichnis geprüft werden muss,
bevor fortgefahren wird.

Für eine Neuinstallation `backup-manager setup` ausführen, nachdem der Installer
abgeschlossen ist. Setup niemals über eine bestehende Konfiguration ausführen, nur um ein
Upgrade durchzuführen.

### Installation für die Entwicklung

Das Quellarchiv beziehen oder das Projekt-Repository klonen, dann in das
Projektverzeichnis wechseln.

```bash
cd linux-backup-manager
```

Projekt installieren.

```bash
pip install .
```

Die Installation dauert nur wenige Sekunden.

Für die Entwicklung die optionalen Qualitätssicherungs-Werkzeuge installieren:

```bash
pip install ".[dev]"
```

---

## 5. Installation überprüfen

Überprüfen, dass die Installation erfolgreich abgeschlossen wurde.

```bash
backup-manager --version
```

Erwartete Ausgabe:

```text
backup-manager 1.3.0
```

---

## 6. Setup-Assistenten ausführen

Interaktiven Setup-Assistenten starten.

```bash
backup-manager setup
```

Während des Setups erledigt LBM automatisch:

* Erstellt das Konfigurationsverzeichnis
* Erstellt die Konfigurationsdatei
* Fragt nach der Anwendungssprache (`de` oder `en`)
* Bietet eine sichere interaktive Neukonfiguration an, wenn die Datei bereits existiert
* Erstellt die Passwortdatei
* Verlangt die Bestätigung, dass das Repository-Passwort nicht wiederhergestellt werden kann
* Prüft die benötigte Software
* Erkennt das konfigurierte USB-Backup-Laufwerk
* Initialisiert das Restic-Repository bei Bedarf
* Installiert User-Level-systemd-Timer, wenn automatische Backups aktiviert sind

Der Setup-Assistent kann gefahrlos mehrfach ausgeführt werden. Vor dem Ändern einer
bestehenden Konfiguration wird die vorherige Datei als `config.yaml.bak` gespeichert.
Bestehende Repositories mit ungültigem Passwort werden gemeldet und niemals neu
initialisiert.

Nach dem Setup die recovery-kritischen Pfade prüfen und eine geschützte Passwortkopie
separat aufbewahren:

```bash
backup-manager recovery-info
```

Optional ein passwortfreies Recovery-Dokument erstellen und separat aufbewahren:

```bash
backup-manager recovery-sheet
```

Nach dem Setup die Read-only-Systemdiagnose ausführen:

```bash
backup-manager doctor
```

Jeden gemeldeten Fehler beheben, bevor auf automatische Backups vertraut wird. Der Befehl
prüft nur die Umgebung und repariert oder verändert sie niemals.

---

## 7. Erstes Backup

Erstes Backup erstellen.

```bash
backup-manager backup
```

Verfügbare Snapshots auflisten.

```bash
backup-manager snapshots
```

---

## 8. Repository überprüfen

Repository-Integritätsprüfung ausführen.

```bash
backup-manager check
```

Regelmäßige Repository-Prüfungen werden empfohlen.

---

## 9. Nächste Schritte

Nach erfolgreicher Installation weiter mit den **Anleitungen** für schrittweise
Walkthroughs häufiger Aufgaben, oder dem **Benutzerhandbuch** für eine ausführliche
Erklärung aller verfügbaren Befehle und Konfigurationsoptionen.

---

Linux Backup Manager Dokumentation

Version 1.3.0
