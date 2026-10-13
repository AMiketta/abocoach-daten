#!/usr/bin/env bash
# Lädt die aktuelle CSV des BNetzA-Ladesäulenregisters (CC BY 4.0, Quelle: Bundesnetzagentur.de).
# Der Dateiname enthält das Datum, deshalb wird der Link von der Download-Seite gelesen.
set -euo pipefail
out="${1:-register.csv}"
page="https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/DownloadundKontakt.html"
url=$(curl -fsSL -A "Mozilla/5.0 (AboCoach data pipeline)" "$page" | grep -oE 'https://data\.bundesnetzagentur\.de/[^"]*Ladesaeulenregister[^"]*\.csv' | head -1)
[ -n "$url" ] || { echo "CSV-Link nicht gefunden" >&2; exit 1; }
echo "Lade $url"
curl -fsSL -A "Mozilla/5.0 (AboCoach data pipeline)" -o "$out" "$url"
