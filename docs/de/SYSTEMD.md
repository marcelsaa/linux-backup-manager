# Automatische Backups mit systemd

**[English version](../SYSTEMD.md)**

Der Linux Backup Manager verwendet systemd-User-Timer. Es wird kein dauerhaft laufender
Backup-Prozess benötigt.

## Verhalten

Zwei unabhängige Timer werden installiert:

* Der geplante Timer prüft das konfigurierte Intervall zur nutzerseitig gewählten Uhrzeit.
  Standard ist täglich um 20:00 Uhr.
* Der Start-Timer läuft kurz nach dem Systemstart oder Nutzer-Login. Er startet sofort ein
  Backup, wenn das gewählte Intervall seit dem letzten vollständig erfolgreichen Backup
  abgelaufen ist.

Nur ein Backup, das für jedes aktivierte Ziel erfolgreich ist, aktualisiert den
Erfolgs-Zeitstempel.

## Befehle

```bash
backup-manager schedule-install
backup-manager schedule-status
backup-manager schedule-remove
```

Die Unit-Dateien liegen unter:

```text
~/.config/systemd/user/
```

## Diagnose

Aktive Timer anzeigen:

```bash
systemctl --user list-timers 'linux-backup-manager-*'
```

Aktuelle Logs anzeigen:

```bash
journalctl --user -u linux-backup-manager-daily.service
journalctl --user -u linux-backup-manager-due.service
```

Der User-Level-systemd-Manager startet normalerweise beim Login. Backup-Laufwerke und
NAS-Einhängungen müssen für den Nutzer verfügbar sein, wenn das Backup beginnt. Systeme, die
Backups ohne interaktiven Login ausführen müssen, benötigen separat konfiguriertes
User-Lingering und system-seitig verfügbare Einhängungen.
