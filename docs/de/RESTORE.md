# Linux Backup Manager

# Restore-Anleitung

**[English version](../RESTORE.md)**

**Version:** 1.3.2

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

# Wiederherstellungsart wählen

Linux Backup Manager bietet zwei Wege, Dateien zurückzubekommen, beide starten mit derselben
Snapshot-Auswahl:

* **`mount`** – hängt einen Snapshot schreibgeschützt ein und öffnet ihn im Dateimanager,
  sodass einzelne Dateien nach Bedarf durchsucht und herauskopiert werden können. Es wird
  nichts kopiert, bis man es selbst tut. Das ist es, was der Hauptmenüpunkt "Dateien
  wiederherstellen" ausführt – die richtige Wahl, wenn nur einige wenige Dateien
  zurückgeholt werden müssen.
* **`restore`** – kopiert einen kompletten Snapshot in einem Schritt in ein Verzeichnis. Die
  richtige Wahl für eine vollständige Notfallwiederherstellung (siehe `docs/RECOVERY.md`),
  nicht um nach einzelnen Dateien zu suchen. Erreichbar über das Hauptmenü unter
  Administration → Expertenfunktionen → "Vollständigen Snapshot wiederherstellen".

Der Rest dieser Anleitung behandelt zuerst `mount`, da es der empfohlene Standard ist,
danach `restore`.

---

# Snapshot einhängen (`mount`)

Direkt starten, oder über den Hauptmenüpunkt "Dateien wiederherstellen":

```bash
backup-manager mount
```

1. Den zu durchsuchenden Snapshot aus der Liste der verfügbaren Snapshots auswählen (siehe
   "Snapshot auswählen" unten).
2. Der Snapshot wird schreibgeschützt an einem temporären Ort eingehängt. Der Standard-
   Dateimanager öffnet sich automatisch am Snapshot-Wurzelverzeichnis. Wird kein
   Dateimanager gefunden, wird stattdessen der Mount-Pfad ausgegeben, um ihn manuell zu
   öffnen.
3. Den Snapshot wie einen normalen Ordner durchsuchen und benötigte Dateien herauskopieren.
4. Enter im Terminal drücken, wenn fertig. Der Snapshot wird automatisch ausgehängt – auch
   wenn der Vorgang mit `Strg+C` abgebrochen wird.

Zu keinem Zeitpunkt werden Restic-Befehle oder Repository-Interna angezeigt.

**Voraussetzungen:** Zum Einhängen wird FUSE (`fusermount` oder `umount`) auf dem System
benötigt; das automatische Öffnen des Dateimanagers benötigt `xdg-open`. Beides ist auf
Desktop-Linux-Installationen üblich.

**Hinweis:** Das Schließen des Dateimanager-Fensters löst *nicht* automatisch das Aushängen
aus – die meisten Dateimanager laufen als ein einziger Hintergrundprozess, es gibt also
keine verlässliche Möglichkeit zu erkennen, dass genau ein bestimmtes Fenster geschlossen
wurde. Stattdessen bei Bedarf im Terminal Enter drücken.

---

# Snapshot auswählen

Ein Snapshot stellt den Zustand der Dateien zu einem bestimmten Zeitpunkt dar.

Sowohl `mount` als auch `restore` zeigen alle verfügbaren Snapshots an und fragen, welcher
verwendet werden soll.

---

# Vollständigen Snapshot wiederherstellen (`restore`)

Direkt starten, oder über Administration → Expertenfunktionen → "Vollständigen Snapshot
wiederherstellen":

```bash
backup-manager restore
```

Der Restore-Befehl führt durch den vollständigen Wiederherstellungsvorgang.

## Restore-Ziel wählen

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

Nach Abschluss des Restores (oder nach dem Herauskopieren von Dateien aus einem
eingehängten Snapshot):

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

## `mount` meldet ein Mount- oder Dateimanager-Problem

* "Einhängen fehlgeschlagen" bedeutet meist, dass FUSE nicht verfügbar ist oder das falsche
  Passwort konfiguriert ist – Details stehen in der ausgegebenen Fehlermeldung.
* "Kein Dateimanager gefunden" bedeutet, dass `xdg-open` nicht installiert oder kein
  Standard-Dateimanager konfiguriert ist; der Mount ist trotzdem erfolgreich, der
  ausgegebene Pfad kann manuell geöffnet werden.

---

# Zusammenfassung

Ein Backup sollte nie als erfolgreich gelten, bevor ein Restore getestet wurde.

Regelmäßige Restore-Tests sind der beste Weg sicherzustellen, dass wertvolle Daten
tatsächlich wiederhergestellt werden können.

---

Linux Backup Manager Dokumentation

Version 1.3.2
