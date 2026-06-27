# LBM QA-Testplan für Version 1.0

## Ziel

Vor dem Release Candidate 1.0 wird Linux Backup Manager gezielt auf Stabilität, Bedienfehler, Installierbarkeit und einfache Sicherheitsrisiken geprüft.

## Testbereiche

1. Code-Qualität
2. Unit-Tests
3. CLI-Tests
4. Integrationstests mit Restic
5. Installationstest in frischer Umgebung
6. Fehlerfalltests
7. Layer-8-Tests
8. Injection-/Robustheitstests
9. End-to-End-Test

## Keine neuen Features

Während dieses Sprints werden keine neuen Funktionen aufgenommen, außer sie sind für ein stabiles Release zwingend erforderlich.

## Abnahmekriterien

- ruff check . läuft fehlerfrei
- pytest läuft fehlerfrei
- LBM lässt sich frisch installieren
- Setup-Assistent funktioniert
- Backup funktioniert
- Restore funktioniert
- ungültige Eingaben führen nicht zum Absturz
- Injection-ähnliche Eingaben werden nicht ausgeführt
- Logging funktioniert
- git status ist sauber
