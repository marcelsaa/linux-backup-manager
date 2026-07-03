# Recovery und Passwort-Sicherheit

**[English version](../RECOVERY.md)**

**Version:** 1.3.0

---

# Zweck

Repositories des Linux Backup Manager werden von Restic verschlüsselt. Das
Repository-Passwort wird benötigt, um Snapshots zu lesen oder Dateien wiederherzustellen. Es
kann weder vom Linux Backup Manager noch von Restic, den Projektentwicklern oder einem
Speicheranbieter zurückgesetzt oder wiederhergestellt werden.

Dieses Recovery-Konzept verhindert vermeidbaren Passwortverlust und dokumentiert die
Informationen, die nötig sind, um eine Linux-Backup-Manager-Installation nach einem
Systemausfall wiederaufzubauen.

---

# Recovery-kritische Bestandteile

Eine vollständige Wiederherstellung erfordert drei unabhängige Bestandteile:

1. Das Backup-Repository mit den verschlüsselten Snapshots.
2. Das Repository-Passwort oder eine geschützte Kopie der Passwortdatei.
3. Die Konfiguration oder eine Notiz zu Repository-Ziel und Backup-Einstellungen.

Die einzige Passwortkopie innerhalb des eigenen verschlüsselten Repositorys aufzubewahren
reicht nicht aus: Das Passwort wird benötigt, bevor dieses Repository überhaupt geöffnet
werden kann.

Die lokalen Standarddateien sind:

```text
~/.config/linux-backup-manager/config.yaml
~/.config/linux-backup-manager/restic.pass
```

Die Passwortdatei enthält das Repository-Passwort und hat normalerweise die Rechte `0600`.

---

# Befehl für Recovery-Informationen

Die aktuellen Recovery-Metadaten anzeigen mit:

```bash
backup-manager recovery-info
```

Der Befehl meldet:

* Pfade zu Konfiguration und Passwortdatei;
* Vorhandensein und Rechte der Passwortdatei;
* konfigurierte USB- und NAS-Repository-Orte;
* einen knappen Notfall-Wiederherstellungsablauf.

Er öffnet niemals die Passwortdatei und gibt niemals das Passwort aus.

---

# Sichere Passwortaufbewahrung

Mindestens eine geschützte Passwortkopie getrennt vom Backup-Repository und dem zu
sichernden Computer aufbewahren. Geeignete Optionen sind:

* ein vertrauenswürdiger Passwort-Manager;
* ein verschlüsseltes Offline-Medium, das separat aufbewahrt wird;
* eine versiegelte Papierkopie an einem physisch sicheren Ort;
* eine geschützte Kopie von `restic.pass` auf einem separaten Recovery-Medium.

Vermeiden:

* die Passwortdatei in Git zu committen;
* sie unverschlüsselt per E-Mail oder Messaging zu versenden;
* eine ungeschützte Klartextkopie in allgemeinem Cloud-Speicher abzulegen;
* die einzige Kopie auf demselben USB-Laufwerk wie das Repository aufzubewahren;
* das Passwort selbst in ein automatisch erzeugtes Recovery-Dokument zu schreiben.

Wer sowohl das Repository als auch dessen Passwort erhält, kann die Backup-Inhalte lesen.

---

# Checkliste zur Vorbereitung

Bevor man sich auf ein Repository verlässt:

1. `backup-manager recovery-info` ausführen und alle Pfade und Ziele prüfen.
2. Das Passwort oder die Passwortdatei an einem geschützten, separaten Ort aufbewahren.
3. Eine Kopie von `config.yaml` aufbewahren oder die Zieleinstellungen notieren.
4. `backup-manager check` ausführen.
5. Einen echten Restore-Test durchführen und überprüfen.
6. Die Recovery-Prüfungen wiederholen, wann immer sich Passwort, Ziel oder Konfiguration
   ändern.

---

# Notfall-Wiederherstellungsablauf

Nach dem Austausch oder der Neuinstallation des Computers:

1. Python 3.12 oder neuer, Restic und die passende Linux-Backup-Manager-Version installieren.
2. Das USB- oder NAS-Repository anschließen und einhängen.
3. `config.yaml` nach `~/.config/linux-backup-manager/config.yaml` wiederherstellen.
4. Die geschützte Passwortdatei-Kopie an den konfigurierten Passwortpfad wiederherstellen.
5. Ihre Rechte einschränken:

   ```bash
   chmod 600 ~/.config/linux-backup-manager/restic.pass
   ```

6. Zugriff überprüfen:

   ```bash
   backup-manager health
   backup-manager snapshots
   backup-manager check
   ```

7. In ein separates Verzeichnis wiederherstellen:

   ```bash
   backup-manager restore
   ```

8. Wichtige wiederhergestellte Dateien mit bekannten Originalen oder Prüfsummen vergleichen,
   bevor Daten zurückkopiert werden.

Ist die ursprüngliche Konfiguration nicht verfügbar, sie mit `backup-manager setup` unter
Verwendung desselben Repository-Ziels und der ursprünglichen Passwortdatei neu erstellen.
Das bestehende Repository dabei nicht initialisieren oder überschreiben.

---

# Vergessenes Passwort

Existiert weder das richtige Passwort noch eine gültige Kopie der Passwortdatei, kann das
verschlüsselte Restic-Repository nicht geöffnet werden. Es gibt kein Verfahren zum
Zurücksetzen oder Umgehen des Passworts.

Das unzugängliche Repository nicht sofort löschen: Möglicherweise findet sich noch eine
weitere geschützte Passwortkopie. Für künftige Backups ein neues Repository mit einem neuen,
sicher aufbewahrten Passwort anlegen, aber getrennt vom alten Repository halten.

---

# Recovery-Dokument

Ein optionales Recovery-Dokument erstellen mit:

```bash
backup-manager recovery-sheet
```

Die Standardausgabe ist:

```text
~/linux-backup-manager-recovery.txt
```

Der Befehl fragt vor dem Überschreiben einer bestehenden Datei und schreibt das Ergebnis
atomar mit den Rechten `0600`. Das Dokument enthält:

* Linux-Backup-Manager-Version, Host und Erstellungszeitpunkt;
* Pfade zu Konfiguration und Passwortdatei;
* USB- und NAS-Repository-Orte;
* leere Felder für die separat aufbewahrte Passwortkopie, Konfigurationskopie und den
  letzten Restore-Test;
* Notfall-Befehle zur Überprüfung und Wiederherstellung.

Das Dokument liest oder enthält bewusst nicht das Repository-Passwort. Es ist ein
Orientierungs- und Ablaufdokument, keine Passwortsicherung. Es ausdrucken oder an einen
geschützten Ort kopieren, getrennt vom Computer und Repository.

---

Linux Backup Manager Dokumentation

Version 1.3.0
