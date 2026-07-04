# Linux Backup Manager

# Anleitungen

**[English Version](../TUTORIAL.md)**

**Version:** 1.3.0

---

# Einleitung

Diese Anleitung führt Schritt für Schritt durch typische, praxisnahe Aufgaben. Sie setzt
voraus, dass Linux Backup Manager bereits installiert und eingerichtet ist – siehe
`docs/de/INSTALL.md`, falls das noch nicht der Fall ist. Eine vollständige Liste aller Befehle
und Konfigurationsoptionen steht in `docs/de/USER_GUIDE.md` und `docs/de/CONFIGURATION.md`.

---

# Anleitung 1: Die erste Woche

Ein kurzer Überblick, was nach der Ersteinrichtung normalerweise passiert.

1. **Tag 1 – Einrichtung.** `backup-manager setup` fragt nach den zu sichernden Ordnern, dem
   Backup-Ziel (USB-Laufwerk und/oder NAS-Freigabe) und einem Repository-Passwort und legt
   danach nach Bestätigung automatisch das erste Backup an.
2. **Tag 1 – Ergebnis prüfen.** Das geführte Hauptmenü öffnen (`backup-manager`) und "Status"
   wählen, oder `backup-manager doctor` für eine ausführlichere, rein lesende
   Gesundheitsprüfung ausführen. Beides funktioniert, ohne sich Restic-Befehle merken zu
   müssen.
3. **Jeder Tag danach.** Wurden automatische Backups bei der Einrichtung aktiviert, ist nichts
   weiter nötig – ein systemd-Timer legt zur konfigurierten Zeit ein neues Backup an. Das
   Hauptmenü zeigt bei jeder Anzeige oberhalb der Menüpunkte den Zeitpunkt des letzten
   erfolgreichen Backups, ein Blick genügt also, um zu bestätigen, dass Backups weiterhin
   laufen.
4. **Ende der Woche – Stichprobe.** Einmal `backup-manager doctor` ausführen. Es meldet
   Backup-Ziele, Repository, Passwortdatei und den Automatik-Timer an einer Stelle, jeweils
   als OK, Warnung oder Fehler markiert.

---

# Anleitung 2: Eine versehentlich gelöschte Datei wiederherstellen

Der häufigste Wiederherstellungsfall braucht keine vollständige Wiederherstellung – nur eine
oder wenige Dateien.

1. Das geführte Hauptmenü öffnen (`backup-manager`) und **"Dateien wiederherstellen"** wählen
   (oder direkt `backup-manager mount` ausführen).
2. Den zu durchsuchenden Snapshot auswählen – meist den neuesten, außer die Datei wurde weiter
   zurückliegend gelöscht.
3. Der Snapshot wird schreibgeschützt eingehängt und, falls ein Dateimanager verfügbar ist,
   automatisch geöffnet. Zur Datei navigieren, dann kopieren oder an den gewünschten Ort
   ziehen.
4. Nach Abschluss zum Terminal zurückkehren und Enter drücken, um den Snapshot sauber
   auszuhängen.

Dateien innerhalb des eingehängten Snapshots können nicht verändert werden – das macht das
Durchsuchen risikofrei, ohne das Backup selbst versehentlich zu verändern. Siehe
`docs/de/RESTORE.md` für den vollständigen Wiederherstellungs-Workflow, einschließlich der
Wiederherstellung eines kompletten Snapshots auf einmal.

---

# Anleitung 3: Ein zweites Backup-Ziel hinzufügen

Mit einem einzelnen USB-Laufwerk zu starten und später eine NAS-Freigabe zu ergänzen (oder
umgekehrt) ist ein gängiger Ausbauschritt.

1. Sicherstellen, dass das neue Ziel erreichbar ist: das USB-Laufwerk ist angeschlossen und
   eingehängt, oder die NAS-Freigabe ist vom Betriebssystem bereits am konfigurierten Pfad
   eingehängt.
2. Das geführte Hauptmenü öffnen und **"Einstellungen"** wählen (oder `backup-manager
   settings` ausführen).
3. Das zu aktivierende Ziel auswählen und bestätigen. Linux Backup Manager legt das
   Repository auf dem neuen Ziel automatisch an, falls es noch nicht existiert.
4. Einmal `backup-manager backup` ausführen, um zu bestätigen, dass beide Ziele jetzt parallel
   ein Backup erhalten, oder auf den nächsten automatischen Lauf warten.

Ab diesem Zeitpunkt erhält jedes Backup jedes aktivierte und erreichbare Ziel – es gibt kein
separates "primäres" und "sekundäres" Ziel.

---

# Anleitung 4: Bestehende Backups auf ein neues Laufwerk umziehen

Ein alterndes USB-Laufwerk ersetzen, ohne die Backup-Historie von vorne beginnen zu müssen.

1. Das neue Laufwerk als Backup-Ziel konfigurieren (siehe Anleitung 3) – altes und neues Ziel
   müssen für diesen Schritt gleichzeitig aktiviert und erreichbar sein.
2. Geführtes Hauptmenü → **Administration → Expertenfunktionen → "Repository migrieren"**
   öffnen (oder `backup-manager migrate` ausführen) und bestätigen.
3. Alle Snapshots werden vom alten zum neuen Ziel kopiert. Das kann bei großen Repositories
   eine Weile dauern – genau deswegen gibt es die Bestätigungsabfrage.
4. Nach erfolgreicher Kopie das alte Ziel in **Einstellungen** deaktivieren (oder das alte
   Laufwerk physisch entfernen, nachdem `backup-manager doctor` das neue Repository als
   erreichbar bestätigt hat).

---

# Anleitung 5: Falls das Repository-Passwort einmal vergessen wird

Es gibt bewusst keine Möglichkeit, ein vergessenes Restic-Repository-Passwort
wiederherzustellen – das ist Restics eigenes Design, keine Einschränkung von Linux Backup
Manager. Sich im Voraus darauf vorzubereiten kostet ein paar Minuten und verhindert später den
Verlust des Zugriffs auf sämtliche Backups.

1. `backup-manager recovery-sheet` einmal direkt nach der Einrichtung ausführen. Es erstellt
   ein druckbares, passwortfreies Dokument mit allem Nötigen, um das Repository zu finden und
   zu identifizieren, mit Rechten `0600` gespeichert.
2. Das eigentliche Passwort dauerhaft und getrennt von diesem Computer aufbewahren – ein
   Passwort-Manager oder eine handschriftliche Notiz an einem sicheren Ort funktionieren
   beide.
3. Siehe `docs/de/RECOVERY.md` für die vollständige Begründung und die
   Notfallwiederherstellungs-Schritte, falls der Zugriff trotzdem einmal verloren geht.

---

Linux Backup Manager Dokumentation

Version 1.3.0
