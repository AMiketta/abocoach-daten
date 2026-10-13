#!/usr/bin/env python3
"""Erzeugt aus dem BNetzA-Ladesäulenregister (CC BY 4.0, Quelle: Bundesnetzagentur.de) die
kompakte Datei stations.txt und evse-prefix.json für Abo-Coach.

Format stations.txt (UTF-8, Zeilen):
  H|<dataAsOf>|<attribution>|<license>|<anzahl stationen>
  O|<index>|<cpoKey oder leer>|<Anzeigename>
  S|<dLat>|<dLon>|<opIndex>|<maxKw>|<evsePrefix oder leer>
Koordinaten in 1e-5 Grad, nach Breite sortiert und delta-kodiert. Ladeeinrichtungen mit gleicher
Position (5 Nachkommastellen) und gleichem Betreiber werden zu einer Station zusammengefasst.

Aufruf: build_stations.py <register.csv> <aliases.json> <out-dir>
"""
import csv, collections, gzip, io, json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anonymize import is_private_person, PRIVATE

def norm_prefix(evse):
    e = re.sub(r"[^A-Za-z0-9]", "", evse or "").upper()
    if len(e) >= 6 and e[:2].isalpha() and (len(e) < 6 or True):
        return e[:5]  # Land (2) + Operator-ID (3)
    return ""

def main(src, aliases_path, out):
    aliases = json.load(open(aliases_path, encoding="utf-8"))["aliases"]
    compiled = [(re.compile(a["match"]), a) for a in aliases]
    with open(src, encoding="utf-8-sig", errors="replace") as f:
        lines = f.read().splitlines()
    as_of = ""
    start = None
    for i, l in enumerate(lines[:40]):
        m = re.search(r"Letzte Aktualisierung vom:\s*(\d\d)\.(\d\d)\.(\d{4})", l)
        if m: as_of = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
        if l.startswith("Ladeeinrichtungs-ID;"): start = i; break
    if start is None: sys.exit("Kopfzeile nicht gefunden")
    reader = csv.DictReader(io.StringIO("\n".join(lines[start:])), delimiter=";")
    ops, op_idx = [], {}
    stations = {}
    anonymized = set()
    prefix_ops = collections.defaultdict(collections.Counter)
    for row in reader:
        if (row.get("Status") or "").strip() not in ("In Betrieb", ""): continue
        try:
            lat = round(float(row["Breitengrad"].replace(",", ".")) * 1e5)
            lon = round(float(row["Längengrad"].replace(",", ".")) * 1e5)
        except (ValueError, KeyError, AttributeError):
            continue
        if not (4_700_000 < lat < 5_600_000 and 500_000 < lon < 1_600_000): continue
        name = " ".join((row.get("Betreiber") or "").split())
        key, disp = "", name
        for rx, a in compiled:
            if rx.search(name): key, disp = a["key"], a["name"]; break
        if not key and is_private_person(name):
            disp = PRIVATE; anonymized.add(name)
        ident = key or disp
        if ident not in op_idx:
            op_idx[ident] = len(ops); ops.append((key, disp))
        oi = op_idx[ident]
        try: kw = float((row.get("Nennleistung Ladeeinrichtung [kW]") or "0").replace(",", "."))
        except ValueError: kw = 0
        pfx = ""
        for n in range(1, 7):
            p = norm_prefix(row.get(f"EVSE-ID{n}"))
            if p:
                pfx = pfx or p; prefix_ops[p][oi] += 1
        k = (lat, lon, oi)
        old = stations.get(k)
        stations[k] = (max(kw, old[0]) if old else kw, (old[1] if old and old[1] else pfx))
    rows = sorted(stations.items())
    os.makedirs(out, exist_ok=True)
    buf = [f"H|{as_of}|Bundesnetzagentur.de|CC BY 4.0|{len(rows)}"]
    buf += [f"O|{i}|{k}|{d.replace('|', '/')}" for i, (k, d) in enumerate(ops)]
    plat = plon = 0
    for (lat, lon, oi), (kw, pfx) in rows:
        buf.append(f"S|{lat-plat}|{lon-plon}|{oi}|{int(round(kw))}|{pfx}")
        plat, plon = lat, lon
    text = "\n".join(buf) + "\n"
    open(os.path.join(out, "stations.txt"), "w", encoding="utf-8").write(text)
    with gzip.open(os.path.join(out, "stations.txt.gz"), "wt", encoding="utf-8", compresslevel=9) as g: g.write(text)
    prefixes = {}
    for p, cnt in sorted(prefix_ops.items()):
        best, _ = cnt.most_common(1)[0]
        k, d = ops[best]
        prefixes[p] = {"key": k, "name": d, "ambiguous": len(cnt) > 1}
    json.dump({"dataAsOf": as_of, "attribution": "Bundesnetzagentur.de", "license": "CC BY 4.0", "prefixes": prefixes},
              open(os.path.join(out, "evse-prefix.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{len(rows)} Stationen, {len(ops)} Betreiber ({len(anonymized)} Privatpersonen → privat), {len(prefixes)} EVSE-Präfixe, Stand {as_of}")

if __name__ == "__main__":
    main(*sys.argv[1:4])
