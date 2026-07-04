# Linux Backup Manager

# Konfigurationsreferenz

**[English version](../CONFIGURATION.md)**

**Version:** 1.3.2

---

# Einführung

Der Linux Backup Manager speichert seine Konfiguration in einer YAML-Datei.

Standardort:

```text
~/.config/linux-backup-manager/config.yaml
```

Die Konfigurationsdatei wird bei der ersten Installation automatisch vom Setup-Assistenten
erstellt. Bei späteren Ausführungen kann der Assistent Backup-Ordner, Ziele und
Zeitplan-Einstellungen aktualisieren. Er speichert die vorherige Version als
`config.yaml.bak`, bevor er sie ersetzt.

Eine manuelle Bearbeitung ist möglich, aber normalerweise nicht erforderlich.

---

# Vollständige Konfiguration

```yaml
system:
  host_name: mein-linux-pc
  language: de

paths:
  log_dir: logs
  state_dir: state
  password_file: ~/.config/linux-backup-manager/restic.pass

backup:
  paths:
    - ~/Dokumente
    - ~/Bilder

  excludes:
    - ~/.cache

targets:
  usb:
    enabled: true
    label: LinuxBackup
    repository_path: restic/linux-mint

  nas:
    enabled: false
    mount_path: /mnt/backup-nas
    repository_path: restic/linux-mint

retention:
  keep_daily: 14
  keep_weekly: 8
  keep_monthly: 12
  keep_yearly: 3

schedule:
  enabled: true
  daily_time: "20:00"
  interval_days: 1
  boot_delay_minutes: 2

```

---

# Konfigurationsabschnitte

## system

Allgemeine Systeminformationen.

| Option      | Beschreibung                                              |
| ----------- | ----------------------------------------------------------- |
| `host_name` | Name des aktuellen Computers.                                |
| `language`  | Anwendungssprache: `de` oder `en`; Standard ist `de`.        |

---

## paths

Definiert interne, vom Linux Backup Manager verwendete Verzeichnisse.

| Option          | Beschreibung                                    |
| --------------- | -------------------------------------------------- |
| `log_dir`       | Verzeichnis für Log-Dateien.                        |
| `state_dir`     | Verzeichnis für den Anwendungszustand.               |
| `password_file` | Ort des Restic-Repository-Passworts.                |

---

## backup

Definiert, welche Dateien und Verzeichnisse gesichert werden.

### paths

Liste der Verzeichnisse, die in jedem Backup enthalten sind.

### excludes

Liste ausgeschlossener Dateien und Verzeichnisse.

Ausschluss-Muster unterstützen Wildcards, sofern von Restic unterstützt.

---

## targets

Definiert Backup-Ziele.

Alle aktivierten und verfügbaren Ziele erhalten ein Backup. USB- und NAS-Backups laufen
parallel.

### usb

| Option            | Beschreibung                                                    |
| ----------------- | -------------------------------------------------------------------- |
| `enabled`         | Aktiviert USB-Backups.                                                |
| `label`           | Erwartetes Dateisystem-Label des USB-Laufwerks.                       |
| `repository_path` | Relativer Pfad des Restic-Repositorys auf dem Backup-Gerät.           |

### nas

NAS-Unterstützung setzt voraus, dass die Netzwerkfreigabe vom Betriebssystem eingehängt
wird.

| Option            | Beschreibung                                                |
| ----------------- | ---------------------------------------------------------------- |
| `enabled`         | Aktiviert Backups auf die eingehängte NAS-Freigabe.                |
| `mount_path`      | Lokaler Einhängepunkt der NAS-Freigabe.                            |
| `repository_path` | Relativer Pfad des Restic-Repositorys auf der NAS-Freigabe.        |

---

## retention

Aufbewahrungsrichtlinie für Repository-Snapshots.

| Option         | Beschreibung                        |
| -------------- | ---------------------------------------- |
| `keep_daily`   | Aufzubewahrende tägliche Snapshots.        |
| `keep_weekly`  | Aufzubewahrende wöchentliche Snapshots.    |
| `keep_monthly` | Aufzubewahrende monatliche Snapshots.      |
| `keep_yearly`  | Aufzubewahrende jährliche Snapshots.       |

---

## schedule

Steuert automatische Backups über systemd-User-Timer.

| Option                  | Beschreibung                                                    |
| ----------------------- | ---------------------------------------------------------------------- |
| `enabled`               | Automatische Backups während der interaktiven Einrichtung installieren. |
| `daily_time`            | Uhrzeit, zu der das Intervall geprüft wird.                             |
| `interval_days`         | Anzahl der Tage zwischen erfolgreichen Backups.                         |
| `boot_delay_minutes`    | Verzögerung vor der Prüfung nach Systemstart/User-Manager-Start.        |

Der Timer prüft das gewählte Intervall standardmäßig um 20:00 Uhr. Sowohl Uhrzeit als auch
Intervall werden während des Setups ausgewählt und können später bearbeitet werden. Ein
zweiter Timer startet kurz nach dem Systemstart oder Login und erstellt ein Nachhol-Backup,
wenn kein erfolgreiches Backup bekannt ist oder das gewählte Intervall überschritten wurde.
Fehlgeschlagene oder unvollständige Multi-Ziel-Backups aktualisieren den
Erfolgs-Zeitstempel nicht.

---

# Beispiele

Der Setup-Assistent und das `settings`-Menü decken jede der folgenden Optionen interaktiv ab
– manuelle Bearbeitung ist nie erforderlich. Diese Beispiele veranschaulichen einige gängige
Szenarien zur Orientierung. Siehe `docs/de/TUTORIAL.md` für schrittweise Anleitungen, um
zwischen diesen Szenarien zu wechseln.

## Einzelnes USB-Laufwerk (das Standardszenario)

```yaml
targets:
  usb:
    enabled: true
    label: LinuxBackup
    repository_path: restic/production
  nas:
    enabled: false
    mount_path: /mnt/backup-nas
    repository_path: restic/production
```

## USB-Laufwerk und NAS-Freigabe parallel

Beide Ziele erhalten jedes Backup; es gibt keine primäre/sekundäre Unterscheidung.

```yaml
targets:
  usb:
    enabled: true
    label: LinuxBackup
    repository_path: restic/production
  nas:
    enabled: true
    mount_path: /mnt/backup-nas
    repository_path: restic/production
```

## Entwicklungsrechner mit größerer Ausschlussliste

Schließt zusätzlich zu den Standardwerten typischerweise groß werdende Quellbäume und
Build-Artefakte aus.

```yaml
backup:
  paths:
    - ~/Projekte
    - ~/Dokumente
  excludes:
    - ~/.cache
    - ~/Projekte/*/node_modules
    - ~/Projekte/*/.venv
    - ~/Projekte/*/target
    - ~/Projekte/*/build
```

## Konservative Aufbewahrung bei begrenztem Speicherplatz

Behält weniger historische Snapshots als der Standard – tauscht Wiederherstellungstiefe gegen
Speicherplatz.

```yaml
retention:
  keep_daily: 7
  keep_weekly: 4
  keep_monthly: 3
  keep_yearly: 1
```

---

# Hinweise

Der Setup-Assistent erstellt diese Datei automatisch und kann ihre wichtigsten operativen
Einstellungen aktualisieren.

Manuelle Bearbeitung sollte normalerweise nur für Aufbewahrungsrichtlinien und andere
fortgeschrittene Einstellungen nötig sein, die der Setup-Assistent nicht anbietet.

Doppelte YAML-Schlüssel werden abgelehnt, da still überschriebene Einstellungen ungewollte
Backup-Pfade oder -Ziele auswählen könnten.

---

Linux Backup Manager Dokumentation

Version 1.3.2
