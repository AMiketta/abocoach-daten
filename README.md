# abocoach-daten

Öffentliche Daten für die App **Abo-Coach**: Ladetarife, Preistabelle „Karte × Betreiber“, Nutzer-Meldungen und
kompakte Stationsdaten. Der App-Code liegt in einem privaten Repo.

**Veröffentlicht unter:** https://amiketta.github.io/abocoach-daten/

| Datei | Inhalt | Quelle |
|---|---|---|
| `tariffs.json` | Ladetarife (Grundgebühr, AC/DC €/kWh) | `data/tariffs.json`, je Eintrag mit `sourceUrl` und Prüfdatum |
| `network-prices.json` | Preis je Karte × Betreiber | `data/network-prices.json`, je Eintrag mit `sourceUrl` und `checkedAt` |
| `reports.json` | Offene Preis-Meldungen, aggregiert (`abocoach.reports/1`) | Issues mit Label `preis-korrektur`, erzeugt von `scripts/build_reports.py` |
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
