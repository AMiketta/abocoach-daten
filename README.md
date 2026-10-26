# abocoach-daten

Öffentliche Daten für die App **Volteule** (Arbeitstitel: Abo-Coach): Ladetarife, Preistabelle „Karte × Betreiber“, Nutzer-Meldungen und
kompakte Stationsdaten. Der App-Code liegt in einem privaten Repo.

**Veröffentlicht unter:** https://amiketta.github.io/abocoach-daten/

| Datei | Inhalt | Quelle |
|---|---|---|
| `tariffs.json` | Ladetarife (Grundgebühr, AC/DC €/kWh) | `data/tariffs.json`, je Eintrag mit `sourceUrl` und Prüfdatum |
| `network-prices.json` | Preis je Karte × Betreiber | `data/network-prices.json`, je Eintrag mit `sourceUrl` und `checkedAt` |
| `reports.json` | Offene Preis-Meldungen, aggregiert, plus `resolved` (übernommen/abgelehnt der letzten 180 Tage, nur Meldungs-ID) (`abocoach.reports/1`) | Issues mit Label `preis-korrektur`, erzeugt von `scripts/build_reports.py` |
| `stations.txt`, `evse-prefix.json` | Standorte und Betreiber öffentlicher Ladepunkte | BNetzA-Ladesäulenregister, erzeugt von `scripts/build_stations.py` |

## Preis melden (Wiki-Modus)

In der App „Preis korrigieren“ antippen – das öffnet ein vorausgefülltes Issue
([Formular](https://github.com/AMiketta/abocoach-daten/issues/new?template=preis-korrektur.yml), Format `abocoach.correction/1`).
Ohne GitHub-Konto geht es auch per Mail.

Regeln:
- Übernommen wird ein Wert **nur mit öffentlicher Anbieterquelle** (Preisseite oder Preisblatt des Anbieters).
- Bis dahin zeigt die App „von Nutzern gemeldet, in Prüfung“; gerechnet wird mit dem geprüften Wert.
- Änderungen an den Preisdateien nur per Pull Request mit Review durch @AMiketta.
- Status-Labels: `neu` → `in-pruefung` → `bestaetigt` / `abgelehnt` / `quelle-fehlt` / `duplikat` / `spam`, dazu `pr-offen`, `uebernommen`.
- Bitte keine personenbezogenen Daten; Fotos können Standortdaten (EXIF) enthalten.

## Entfernung/Korrektur von Betreibernamen

Die Stationsdaten stammen aus dem **Ladesäulenregister der Bundesnetzagentur** (Lizenz CC BY 4.0). Dort sind auch
Privatpersonen als Betreiber eingetragen. Wir ersetzen deren Namen beim Erzeugen durch **„privat“**
(`scripts/anonymize.py`: Rechtsformen, Behörden und Firmenwörter bleiben, Namen im Muster „Vorname Nachname“ werden ersetzt).
Standort und Leistung bleiben, weil sie für die Säulensuche nötig sind. Eine Heuristik macht Fehler; Ausnahmen stehen in
`scripts/anonymize_overrides.json` (`force_private` als sha256-Hash, damit der Name dort nicht im Klartext steht; `keep` für Firmen).

**Entfernung oder Korrektur beantragen:**
- per **Mail** an **`<DATENSCHUTZ-MAILADRESSE FOLGT>`** (empfohlen, nicht öffentlich), oder
- per [GitHub-Issue „Entfernung/Korrektur eines Betreibernamens“](https://github.com/AMiketta/abocoach-daten/issues/new?template=namensentfernung.yml).
  Issues sind öffentlich; nötig ist nur der Betreibername, wie er in den Daten steht.

Die Änderung wirkt mit der nächsten Veröffentlichung auf Pages und dem nächsten App-Update. Den Eintrag im Register selbst
ändert nur der Betreiber bei der Bundesnetzagentur.

## Lizenzen und Quellen

- **Stationsdaten:** Datenquelle: Bundesnetzagentur, Ladesäulenregister
  ([bundesnetzagentur.de](https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/start.html)),
  Lizenz [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.de). Die Daten wurden verändert: gefiltert
  (nur „In Betrieb“), je Standort und Betreiber zusammengefasst, Koordinaten auf 5 Nachkommastellen gerundet und kodiert,
  Betreibernamen teils auf Marken abgebildet (`data/operator-aliases.json`) und **Namen von Privatpersonen durch „privat“ ersetzt**
  (Heuristik in `scripts/anonymize.py`: Rechtsformen, Behörden und Firmenwörter bleiben, Namen im Muster Vorname Nachname werden ersetzt;
  Standort und Leistung bleiben erhalten). Der Stand steht in der Kopfzeile von `stations.txt`.
  Die Stationsdateien werden nur auf Pages veröffentlicht, nicht im Git-Verlauf gespeichert.
- **Preise:** eigene Recherche aus öffentlichen Anbieterquellen (je Eintrag `sourceUrl`), ohne Gewähr. Maßgeblich ist der
  Preis an der Säule bzw. beim Anbieter. Lizenz für die Preisdateien und Skripte: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.de), © AMiketta.
