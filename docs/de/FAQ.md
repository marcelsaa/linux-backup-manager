# Linux Backup Manager

# Häufig gestellte Fragen (FAQ)

**[English version](../FAQ.md)**

**Version:** 1.1.0-rc1

---

# Allgemein

## Wo wird die Konfiguration gespeichert?

Die Konfigurationsdatei wird gespeichert unter:

```text
~/.config/linux-backup-manager/config.yaml
```

Die Datei wird während des Setups automatisch erstellt.

---

## Wo wird das Repository-Passwort gespeichert?

Die Passwortdatei wird gespeichert unter:

```text
~/.config/linux-backup-manager/restic.pass
```

Ihre Dateiberechtigungen werden automatisch auf den aktuellen Nutzer beschränkt.

---

## Kann ich den Setup-Assistenten mehr als einmal ausführen?

Ja.

Der Setup-Assistent ist idempotent und kann gefahrlos mehrfach ausgeführt werden.

Er erstellt nur fehlende Bestandteile und überprüft die bestehende Installation.

---

# Backup

## Warum wird mein USB-Laufwerk nicht erkannt?

Folgendes prüfen:

* Das USB-Laufwerk ist angeschlossen.
* Das Dateisystem-Label stimmt mit der Konfiguration überein.
* Das Laufwerk ist eingehängt.
* Das Laufwerk ist zugänglich.

Der Befehl

```bash
backup-manager doctor
```

meldet die USB-Erreichbarkeit und den Repository-Zustand, ohne etwas davon zu verändern.

---

## Kann ich mehrere USB-Laufwerke verwenden?

Nicht gleichzeitig als zwei unabhängige USB-Ziele. Es kann nur ein USB-Ziel gleichzeitig
konfiguriert werden. Siehe `docs/ROADMAP.md` für geplante Arbeit in diesem Bereich.

---

## Kann ich ein NAS verwenden?

Ja. NAS-Backups auf eine eingehängte Netzwerkfreigabe werden unterstützt, zusätzlich zu USB,
und beide laufen parallel, wenn aktiviert. Siehe `docs/de/CONFIGURATION.md` für die
`targets.nas`-Konfigurationsoptionen.

---

# Wiederherstellung

## Ich habe mein Repository-Passwort vergessen.

Ohne das richtige Repository-Passwort kann auf das Backup-Repository nicht zugegriffen
werden.

Das Passwort kann weder vom Linux Backup Manager noch von Restic oder den
Projektentwicklern zurückgesetzt werden. Eine geschützte Kopie des Passworts oder der
Passwortdatei wiederherstellen. Existiert keine gültige Kopie, kann das verschlüsselte
Repository nicht wiederhergestellt werden.

`backup-manager recovery-info` vor einem Notfall verwenden und `docs/de/RECOVERY.md`
befolgen. Die Passwortkopie getrennt vom Repository aufbewahren.

---

## Kann ich einzelne Dateien wiederherstellen?

Ja.

Der Restore-Befehl erlaubt es, Daten aus einzelnen Snapshots wiederherzustellen.

Aus Sicherheitsgründen wird empfohlen, in ein separates Verzeichnis wiederherzustellen.

---

# Repository

## Sollte ich Repository-Prüfungen durchführen?

Ja.

Regelmäßige Repository-Prüfungen helfen, Probleme zu erkennen, bevor ein Restore nötig wird.

```bash
backup-manager check
```

regelmäßig ausführen.

---

## Wann sollte ich `forget` verwenden?

`forget` entfernt Snapshots gemäß der konfigurierten Aufbewahrungsrichtlinie.

---

## Wann sollte ich `prune` verwenden?

`prune` entfernt Repository-Daten, auf die kein Snapshot mehr verweist.

Normalerweise wird es nach `forget` ausgeführt.

---

# Zukünftige Funktionen

Siehe `docs/ROADMAP.md` für abgeschlossene und geplante Arbeit (nur auf Englisch verfügbar).

---

Linux Backup Manager Dokumentation

Release Candidate 1.1.0-rc1
