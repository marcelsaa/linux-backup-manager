# Linux Backup Manager

# Restore-Anleitung

**[English version](../RESTORE.md)**

**Version:** 1.1.0-rc1

---

# Einführung

Backups zu erstellen ist nur die eine Hälfte einer erfolgreichen Backup-Strategie.

Die Fähigkeit, Daten schnell und verlässlich wiederherzustellen, ist ebenso wichtig.

Diese Anleitung erklärt, wie Daten aus einem vom Linux Backup Manager verwalteten
Restic-Repository wiederhergestellt werden.

---

# Bevor es losgeht

Vor Beginn eines Restore-Vorgangs Folgendes prüfen:

* Das Backup-Repository ist erreichbar.
* Das USB-Backup-Laufwerk ist angeschlossen.
* Die Repository-Passwortdatei existiert.
* Das Repository besteht eine Integritätsprüfung.

Recovery-kritische Pfade und Zielinformationen anzeigen, ohne das Passwort preiszugeben:

```bash
backup-manager recovery-info
```

Es wird empfohlen, vor dem Wiederherstellen eine Repository-Prüfung durchzuführen.

```bash
backup-manager check
```

---

# Restore starten

Restore-Assistenten starten.

```bash
backup-manager restore
```

Der Restore-Befehl führt durch den vollständigen Wiederherstellungsvorgang.

---

# Snapshot auswählen

Ein Snapshot stellt den Zustand der Dateien zu einem bestimmten Zeitpunkt dar.

Der Restore-Assistent zeigt alle verfügbaren Snapshots an.

Den Snapshot auswählen, der wiederhergestellt werden soll.

---

# Restore-Ziel wählen

Aus Sicherheitsgründen sollten Dateien immer in ein separates Verzeichnis
wiederhergestellt werden.

Der Restore-Befehl fragt nach einem Ziel und schlägt ein Verzeichnis unterhalb von
`~/lbm-restore/<snapshot-id>` vor. Ist das gewählte Verzeichnis nicht leer, muss eine
zusätzliche Warnung bestätigt werden, bevor der Restore beginnt.

Empfohlener Ablauf:

* In ein leeres Verzeichnis wiederherstellen.
* Die wiederhergestellten Dateien prüfen.
* Die benötigten Dateien zurück an ihren ursprünglichen Ort kopieren.

Das verhindert ein versehentliches Überschreiben bestehender Daten.

---

# Wiederhergestellte Dateien überprüfen

Nach Abschluss des Restores:

* Prüfen, dass alle erwarteten Dateien vorhanden sind.
* Wichtige Dokumente öffnen.
* Verzeichnisstrukturen prüfen.
* Bei Bedarf Dateiberechtigungen prüfen.

Alte Backups nicht löschen, bevor sicher ist, dass die wiederhergestellten Daten
vollständig sind.

---

# Best Practices

Ein Restore sollte nicht nur nach Datenverlust durchgeführt werden.

Regelmäßige Test-Restores helfen sicherzustellen, dass:

* Backups vollständig sind
* das Repository gesund ist
* der Restore-Ablauf vertraut ist
* die Wiederherstellung funktioniert, wenn sie tatsächlich benötigt wird

Regelmäßiges Testen von Restores gilt als Best Practice.

---

# Fehlerbehebung

## Repository kann nicht gefunden werden

Mögliche Ursachen:

* USB-Laufwerk nicht angeschlossen
* Falsches USB-Label
* Repository verschoben

---

## Falsches Passwort

Das Repository-Passwort stimmt nicht mit dem bei der Repository-Erstellung verwendeten
Passwort überein.

Ohne das richtige Passwort kann auf das Repository nicht zugegriffen werden.

---

## Beschädigtes Repository

Ausführen:

```bash
backup-manager check
```

Werden Fehler gemeldet, das Repository reparieren, bevor ein weiterer Restore-Versuch
unternommen wird.

---

# Zusammenfassung

Ein Backup sollte nie als erfolgreich gelten, bevor ein Restore getestet wurde.

Regelmäßige Restore-Tests sind der beste Weg sicherzustellen, dass wertvolle Daten
tatsächlich wiederhergestellt werden können.

---

Linux Backup Manager Dokumentation

Release Candidate 1.1.0-rc1
