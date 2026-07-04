# Linux Backup Manager

# Benutzerhandbuch

**[English version](../USER_GUIDE.md)**

**Version:** 1.3.2

---

# Einführung

Der Linux Backup Manager (LBM) bietet eine einheitliche Kommandozeilen-Oberfläche zum
Erstellen, Verwalten und Wiederherstellen von Backups.

Dieses Handbuch erklärt jeden verfügbaren Befehl, wann er verwendet werden sollte und was
während der Ausführung zu erwarten ist.

Bevor du einen anderen Befehl als `setup` verwendest, stelle sicher, dass die Ersteinrichtung
erfolgreich abgeschlossen wurde.

---

# Befehlsübersicht

| Befehl      | Zweck                                                   |
| ----------- | -------------------------------------------------------- |
| `menu`      | Geführtes Hauptmenü öffnen (Standard ohne Argumente)      |
| `setup`     | Linux Backup Manager konfigurieren                        |
| `settings`  | Einzelne Einstellungen interaktiv ändern                   |
| `export-config` | Aktuelle Konfigurationsdatei an einen anderen Ort kopieren |
| `import-config` | Externe Konfigurationsdatei validieren und übernehmen  |
| `status`    | Aktuelle Konfiguration und Systemstatus anzeigen            |
| `health`    | System-Health-Checks durchführen                          |
| `doctor`    | Umfassende Read-only-Diagnose ausführen                   |
| `logs`      | Log-Datei anzeigen (Pfad und letzte Einträge)             |
| `recovery-info` | Passwortsichere Recovery-Informationen anzeigen        |
| `recovery-sheet` | Passwortfreies Recovery-Dokument erstellen            |
| `change-password` | Repository-Passwort ändern                          |
| `backup`    | Neues Backup erstellen                                     |
| `schedule-install` | Automatische Backups installieren und aktivieren    |
| `schedule-status` | Status des automatischen Backup-Timers anzeigen      |
| `schedule-remove` | Automatische Backup-Timer deaktivieren und entfernen  |
| `snapshots` | Verfügbare Snapshots anzeigen                              |
| `restore`   | Vollständigen Snapshot in ein Verzeichnis wiederherstellen (Expertenfunktion) |
| `mount`     | Snapshot schreibgeschützt einhängen und im Dateimanager durchsuchen (Standard für "Dateien wiederherstellen") |
| `stats`     | Repository-Statistiken anzeigen                            |
| `check`     | Repository-Integrität prüfen                               |
| `forget`    | Alte Snapshots gemäß der Aufbewahrungsrichtlinie entfernen |
| `prune`     | Unreferenzierte Repository-Daten entfernen                 |
| `migrate`   | Alle Snapshots auf ein anderes konfiguriertes Ziel kopieren (Expertenfunktion) |

---

# menu

## Zweck

Öffnet das geführte Hauptmenü – der Standard-Einstiegspunkt, wenn `backup-manager` ohne Befehl
aufgerufen wird (z. B. über die Anwendungsmenü-Verknüpfung). Das Menü bleibt geöffnet, bis
"Beenden" gewählt wird, sodass mehrere Aktionen in einer Sitzung ausgeführt werden können. Über
den Menüpunkten steht bei jeder Anzeige der Zeitpunkt des letzten erfolgreichen Backups, damit
auf einen Blick erkennbar ist, ob ein Backup fällig ist, ohne erst "Status" zu öffnen.

## Befehl

```bash
backup-manager
backup-manager menu
```

## Aufbau

* Backup starten
* Dateien wiederherstellen
* Status
* Einstellungen
* Administration
  * Doctor (ausführliche Diagnose)
  * Repository prüfen
  * Log-Dateien anzeigen
  * Backup-Verlauf
  * Repository-Informationen
  * Expertenfunktionen
    * Repository initialisieren
    * Vollständigen Snapshot wiederherstellen
    * Snapshot-Statistiken anzeigen
    * Alte Snapshots entfernen
    * Repository bereinigen
    * Repository migrieren
    * Passwort ändern
    * Recovery-Dokument erstellen
    * Konfiguration exportieren
    * Konfiguration importieren
    * Zeitplan installieren / anzeigen / entfernen
* Beenden

Jeder Menüpunkt ruft denselben Befehl auf, der an anderer Stelle in diesem Handbuch beschrieben
ist – das Menü ist eine Komfortschicht, keine eigenständige Implementierung.
`backup-manager --non-interactive` (ohne Befehl) führt stattdessen `status` aus, da das Menü
interaktive Eingaben benötigt.

"Dateien wiederherstellen" im Hauptmenü ruft `mount` auf (einzelne Dateien durchsuchen und
kopieren), nicht den vollständigen `restore`-Befehl – siehe die Abschnitte `mount` und
`restore` weiter unten für den Unterschied.

---

# setup

## Zweck

Der Setup-Assistent bereitet den Linux Backup Manager für die erste Nutzung vor.

Er legt alle benötigten Dateien an und prüft, dass das System bereit für Backups ist.

## Befehl

```bash
backup-manager setup
```

## Was der Setup-Assistent tut

Während der Ausführung erledigt der Assistent folgende Aufgaben:

* Erstellt das Konfigurationsverzeichnis
* Erstellt die Konfigurationsdatei
* Wählt die Anwendungssprache (`de` oder `en`) aus und speichert sie
* Bietet an, eine bestehende Konfiguration zu bearbeiten, und sichert die vorherige Datei
  als `config.yaml.bak`
* Erstellt die Passwortdatei
* Lässt den Nutzer USB, NAS oder beide Backup-Ziele auswählen
* Validiert die Erreichbarkeit jedes konfigurierten Ziels und bietet eine Korrekturschleife
  für nicht erreichbare Pfade an, wobei der Assistent geöffnet bleibt, bis ein erreichbares
  Ziel bestätigt ist
* Konfiguriert zielspezifische Bezeichnungen, Einhängepfade und Repository-Pfade
* Zeigt vor dem Schreiben einer Konfiguration eine vollständige Zusammenfassung von Host,
  Backup-Pfaden, Zielen und Zeitplan zur Bestätigung an
* Prüft die benötigte Software
* Erkennt jedes konfigurierte Backup-Ziel
* Prüft jedes konfigurierte Restic-Repository
* Legt fehlende Repositories auf Wunsch an

Der Setup-Assistent kann gefahrlos mehrfach ausgeführt werden. Existiert bereits eine
Konfiguration, fragt er, ob Backup-Ordner, Ziele und der automatische Zeitplan bearbeitet
werden sollen. Bei Ablehnung bleibt die Datei unverändert. Bei Zustimmung wird
`config.yaml.bak` angelegt, bevor die aktualisierte Datei geschrieben wird.

Die gewählte Sprache steuert alle von der Anwendung erzeugten Befehlsausgaben und
Eingabeaufforderungen. Rohausgaben externer Programme wie Restic und systemctl werden
unverändert angezeigt.

Ein ungültiges Repository-Passwort wird getrennt von einem fehlenden Repository gemeldet.
Setup bietet niemals an, ein bestehendes Repository zu initialisieren, das mit dem
konfigurierten Passwort nicht geöffnet werden kann. Vor dem Anlegen einer Passwortdatei
verlangt Setup eine ausdrückliche Bestätigung, dass ein vergessenes Repository-Passwort
nicht zurückgesetzt werden kann und eine geschützte Kopie separat aufbewahrt werden muss.

---

# settings

## Zweck

Öffnet ein interaktives Menü, um einzelne Einstellungen zu ändern, ohne den gesamten
Setup-Assistenten erneut zu durchlaufen.

## Befehl

```bash
backup-manager settings
```

## Verfügbare Einstellungen

* Sprache
* Backup-Pfade
* Backup-Ziele (USB und NAS)
* Automatischer Backup-Zeitplan

Wähle einen Menüeintrag, um ihn zu ändern, oder wähle die Beenden-Option, um das Menü zu
verlassen. Jede Änderung wird atomar gespeichert, bevor das Menü zurückkehrt, und es wird
ein `config.yaml.bak`-Backup der vorherigen Konfiguration angelegt. Das Menü bleibt aktiv,
bis der Nutzer sich zum Beenden entscheidet, sodass mehrere Einstellungen in einer Sitzung
geändert werden können.

---

# export-config

## Zweck

Kopiert die aktuelle Konfigurationsdatei an einen vom Nutzer gewählten Ort, zum Beispiel um
eine externe Sicherung der Konfiguration zu behalten oder sie auf einen anderen Rechner zu
übertragen.

## Befehl

```bash
backup-manager export-config
```

Eine bestehende Datei am gewählten Ziel wird erst nach ausdrücklicher Bestätigung
überschrieben. Der Befehl meldet einen Fehler, falls noch keine Konfiguration existiert.

---

# import-config

## Zweck

Liest eine externe Konfigurationsdatei, validiert sie vollständig und übernimmt sie als
aktive Konfiguration.

## Befehl

```bash
backup-manager import-config
```

Die Quelldatei wird vollständig validiert, bevor irgendetwas geändert wird. Eine bestehende
Konfiguration wird als `config.yaml.bak` gesichert, bevor sie atomar ersetzt wird. Fehlt die
Quelldatei oder schlägt die Validierung fehl, bleibt die bestehende Konfiguration
unangetastet.

---

# status

## Zweck

Zeigt die aktuelle Konfiguration an und meldet den erkannten Systemzustand.

## Befehl

```bash
backup-manager status
```

Verwende diesen Befehl, wann immer du überprüfen möchtest, dass die Anwendung korrekt
konfiguriert wurde.

---

# health

## Zweck

Führt eine vollständige Prüfung der Backup-Umgebung durch.

## Befehl

```bash
backup-manager health
```

Typische Prüfungen umfassen:

* Konfiguration
* Passwortdatei
* USB-Gerät
* Restic-Repository
* Benötigte Software

Es wird empfohlen, den Health-Check regelmäßig auszuführen.

---

# doctor

## Zweck

Führt eine einzelne Read-only-Diagnose für Support und Selbstprüfung durch. Der Befehl meldet:

* ob die Konfiguration geladen werden kann;
* ob die Passwortdatei existiert und plausible, restriktive Rechte hat;
* ob Restic installiert und ausführbar ist;
* ob jedes konfigurierte USB- oder NAS-Ziel erreichbar und beschreibbar ist;
* ob jedes erreichbare Restic-Repository geöffnet werden kann;
* den Zeitpunkt des letzten erfolgreich aufgezeichneten Backups.

## Befehl

```bash
backup-manager doctor
```

Ergebnisse werden mit lokalisierten Bezeichnungen klassifiziert (`OK`, `Warning`, `Error`,
`Skipped` auf Englisch; `OK`, `WARNUNG`, `FEHLER`, `ÜBERSPRUNGEN` auf Deutsch). Ein fehlendes,
zuvor aufgezeichnetes Backup ist eine Warnung. Fehler bei Konfiguration, Passwort, Restic,
Ziel oder Repository lassen den Befehl mit Status 1 beenden. Erfolgreiche Prüfungen und
Warnungen beenden mit Status 0.

`doctor` führt keine Reparaturen durch. Es initialisiert keine Repositories, erstellt keine
Backups, ändert die Konfiguration nicht und verändert keine automatischen Backup-Timer.

---

# logs

## Zweck

Zeigt den Speicherort der Anwendungs-Logdatei und deren letzte Einträge an, zur
Fehlersuche ohne die Datei manuell suchen zu müssen.

## Befehl

```bash
backup-manager logs
```

Gibt den Pfad der Logdatei aus (`~/.local/state/lbm/backup-manager.log`), gefolgt von bis zu
40 letzten Zeilen. Existiert die Datei noch nicht oder ist sie leer, wird stattdessen ein
entsprechender Hinweis ausgegeben.

---

# recovery-info

## Zweck

Zeigt die Pfade, Repository-Ziele und Notfallschritte an, die für die Wiederherstellung
benötigt werden, ohne das Repository-Passwort zu lesen oder auszugeben.

## Befehl

```bash
backup-manager recovery-info
```

Führe diesen Befehl nach dem Setup und immer dann aus, wenn sich der Pfad der Passwortdatei
oder das Repository-Ziel ändert. Bewahre eine geschützte Kopie des Passworts oder der
Passwortdatei getrennt vom Repository auf. Siehe `docs/de/RECOVERY.md` für das vollständige
Recovery-Konzept.

---

# recovery-sheet

## Zweck

Erstellt ein optionales Recovery-Dokument mit den konfigurierten Repository-Zielen, wichtigen
Dateipfaden, Notfallbefehlen und leeren Feldern für externe Recovery-Notizen. Das Dokument
enthält niemals das Repository-Passwort.

## Befehl

```bash
backup-manager recovery-sheet
```

Wähle einen Ausgabepfad oder akzeptiere `~/linux-backup-manager-recovery.txt`. Bestehende
Dateien erfordern eine ausdrückliche Überschreib-Bestätigung. Das Ergebnis wird atomar mit
den Rechten `0600` geschrieben.

Drucke das Dokument aus oder kopiere es an einen geschützten Ort, getrennt sowohl vom
Computer als auch vom Backup-Repository. Notiere manuell, wo die geschützte Passwortkopie
aufbewahrt wird; schreibe das Passwort selbst nicht in ein ungeschütztes Dokument.

---

# change-password

## Zweck

Ändert das Repository-Passwort für alle konfigurierten Repositories.

## Befehl

```bash
backup-manager change-password
```

Das neue Passwort wird nacheinander auf jedes konfigurierte Repository angewendet, und die
Passwortdatei wird erst atomar ersetzt, nachdem alle Repositories erfolgreich waren. Schlägt
ein Repository fehl, werden die bereits geänderten Repositories namentlich gemeldet, und die
Passwortdatei bleibt unverändert, sodass kein Repository mit der alten Passwortdatei
unzugänglich bleibt.

Nach einer erfolgreichen Änderung bietet der Befehl an, das Recovery-Dokument neu zu
erstellen, da ein zuvor erstelltes Dokument noch auf den alten Passwortstand verweist.

---

# backup

## Zweck

Erstellt ein neues Restic-Backup anhand der konfigurierten Backup-Pfade.

## Befehl

```bash
backup-manager backup
```

Der Backup-Vorgang speichert nur geänderte Daten.

Restic führt automatisch eine Deduplizierung durch.

---

# snapshots

## Zweck

Zeigt alle aktuell im Repository gespeicherten Snapshots an.

## Befehl

```bash
backup-manager snapshots
```

Snapshots stellen Wiederherstellungspunkte dar, die später wiederhergestellt werden können.

---

# mount

## Zweck

Hängt einen ausgewählten Snapshot schreibgeschützt per FUSE ein und öffnet ihn im
Standard-Dateimanager, sodass einzelne Dateien durchsucht und herauskopiert werden können,
ohne den gesamten Snapshot vorher wiederherzustellen zu müssen. Das ist es, was der
Hauptmenüpunkt "Dateien wiederherstellen" ausführt, und der empfohlene Weg, um wenige
einzelne Dateien zurückzuholen.

## Befehl

```bash
backup-manager mount
```

## Ablauf

1. Snapshot aus der Liste auswählen, genau wie bei `restore`.
2. Der Snapshot wird schreibgeschützt an einem temporären Ort eingehängt, der Dateimanager
   öffnet sich automatisch am Snapshot-Wurzelverzeichnis (fällt auf eine Pfadausgabe zurück,
   falls kein Dateimanager gefunden wird).
3. Snapshot wie einen normalen Ordner durchsuchen und benötigte Dateien herauskopieren.
4. Enter im Terminal drücken, wenn fertig – der Snapshot wird automatisch ausgehängt.

Es werden keine Restic-Befehle oder Repository-Interna angezeigt. Der Mount ist immer
schreibgeschützt und wird auch bei einem Abbruch (`Strg+C`) ausgehängt.

## Voraussetzungen

Zum Einhängen wird FUSE (`fusermount` oder `umount`) benötigt; das automatische Öffnen des
Dateimanagers benötigt `xdg-open`. Beides ist auf Desktop-Linux-Installationen üblich; fehlt
eines davon, meldet `mount` das klar, statt stillschweigend zu scheitern.

---

# restore

## Zweck

Stellt einen vollständigen Snapshot in ein Verzeichnis wieder her. Das ist das
Vollständig-Wiederherstellungs-Gegenstück zu `mount` – geeignet, um alles auf einmal
zurückzubekommen (z. B. nach einer vollständigen Notfallwiederherstellung, siehe
`docs/RECOVERY.md`), nicht um nach einzelnen Dateien zu suchen. Erreichbar über das
Hauptmenü unter Administration → Expertenfunktionen → "Vollständigen Snapshot
wiederherstellen".

## Befehl

```bash
backup-manager restore
```

Der Restore-Befehl führt den Nutzer durch den Wiederherstellungsvorgang.

Aus Sicherheitsgründen wird empfohlen, in ein separates Verzeichnis wiederherzustellen.

---

# stats

## Zweck

Repository-Statistiken anzeigen.

## Befehl

```bash
backup-manager stats
```

Typische Informationen umfassen:

* Anzahl der Snapshots
* Zeitstempel des ersten und letzten Snapshots
* Host des letzten Snapshots

---

# check

## Zweck

Repository-Integrität prüfen.

## Befehl

```bash
backup-manager check
```

Regelmäßige Repository-Prüfungen helfen dabei, beschädigte Repositories zu erkennen, bevor
ein Restore nötig wird.

---

# forget

## Zweck

Snapshots gemäß der konfigurierten Aufbewahrungsrichtlinie entfernen.

## Befehl

```bash
backup-manager forget
```

Es werden nur Snapshots entfernt, die außerhalb der konfigurierten Aufbewahrungsrichtlinie
liegen.

---

# prune

## Zweck

Nicht mehr benötigte Repository-Daten entfernen.

## Befehl

```bash
backup-manager prune
```

Dieser Befehl sollte normalerweise nach `forget` ausgeführt werden.

---

# migrate

## Zweck

Kopiert alle Snapshots von einem konfigurierten Backup-Ziel zu einem anderen (z. B. von USB
zu NAS), unter Verwendung von Restics eigenem `copy`-Befehl. Nützlich beim Umzug auf neuen
Speicher, ohne die Backup-Historie zu verlieren. Erreichbar über Administration →
Expertenfunktionen → "Repository migrieren".

## Befehl

```bash
backup-manager migrate
```

## Voraussetzungen

Mindestens zwei konfigurierte, aktivierte und aktuell erreichbare Backup-Ziele (siehe
`docs/CONFIGURATION.md`). Ist nur ein Ziel erreichbar, meldet `migrate`, dass ein zweites
Ziel benötigt wird, und bricht ohne Änderungen ab.

## Ablauf

1. Quellziel aus der Liste der verfügbaren Ziele auswählen.
2. Zielziel aus den verbleibenden Zielen auswählen.
3. Bestätigen – das Kopieren kann je nach Datenmenge lange dauern, da Restic sowohl von der
   Quelle lesen als auch auf das Ziel schreiben muss.
4. Ist das Ziel noch kein initialisiertes Restic-Repository, wird es automatisch angelegt.
5. Alle Snapshots werden kopiert. Bestehende Snapshots am Ziel bleiben unangetastet, nichts
   wird an der Quelle gelöscht.

---

# Empfohlener Ablauf

Für die regelmäßige Nutzung wird folgender Ablauf empfohlen.

1. Den Setup-Assistenten einmal ausführen.
2. Regelmäßig Backups durchführen.
3. Die Repository-Gesundheit prüfen.
4. Die Aufbewahrungsrichtlinie anwenden.
5. Das Repository bereinigen (Prune).
6. Regelmäßig Restores testen.

---

# Automatische Backups

Installiere oder repariere die User-Level-systemd-Timer mit:

```bash
backup-manager schedule-install
```

Während des Setups wählt der Nutzer die Uhrzeit und das Intervall in Tagen. Der Standard ist
täglich um 20:00 Uhr. Nach einem Neustart oder Login wartet ein zweiter Timer eine kurze,
feste Verzögerung ab, bevor geprüft wird, ob das gewählte Intervall seit dem letzten
erfolgreichen Backup abgelaufen ist, und holt bei Bedarf sofort nach. Die Verzögerung
verhindert einen unerwarteten zusätzlichen Snapshot, wenn Setup und Neustart am selben Tag
stattfinden.

Timer prüfen oder entfernen mit:

```bash
backup-manager schedule-status
backup-manager schedule-remove
```

Die Timer laufen als aktueller Nutzer und benötigen keinen dauerhaft laufenden
LBM-Prozess. Backup-Ziele müssen eingehängt und erreichbar sein, wenn ein Timer auslöst.

---

Linux Backup Manager Dokumentation

Version 1.3.2
