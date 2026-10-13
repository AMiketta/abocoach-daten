#!/usr/bin/env python3
"""Schreibt reports.json (abocoach.reports/1) aus offenen Issues mit Label `preis-korrektur`.

Nur aggregierte Fachfelder, keine Namen/Konten. Gruppiert nach Tarif × Betreiber × Ladeart × Feld.
Aufruf: build_reports.py <issues.json (gh api …/issues)> <out reports.json>
"""
import json, re, sys, datetime

SKIP = {"spam", "duplikat", "abgelehnt", "uebernommen", "namensentfernung"}
NUM_FIELDS = {"reportedValue", "appValue"}

def parse_body(body):
    out, key = {}, None
    for line in (body or "").splitlines():
        m = re.match(r"^###\s+.*\((\w+)[^)]*\)\s*$", line)
        if m:
            key = m.group(1); out[key] = ""; continue
        if key is not None: out[key] += line + "\n"
    res = {}
    for k, v in out.items():
        v = v.strip()
        if not v or v == "_No response_": continue
        res[k] = v
    return res

def num(s):
    try: return round(float(str(s).replace(",", ".").replace("€", "").strip()), 4)
    except ValueError: return None

RESOLVED = {"uebernommen": "uebernommen", "abgelehnt": "abgelehnt"}
RESOLVED_DAYS = 180

def resolved_entries(issues, now):
    """Geschlossene Preis-Issues mit Ergebnis (übernommen/abgelehnt) der letzten 180 Tage: nur reportId, Nr., Status."""
    try:
        cutoff = (datetime.datetime.strptime(now[:10], "%Y-%m-%d") - datetime.timedelta(days=RESOLVED_DAYS)).strftime("%Y-%m-%d")
    except ValueError:
        cutoff = ""
    out = []
    for it in issues:
        if "pull_request" in it or it.get("state") != "closed": continue
        labels = {l["name"] for l in it.get("labels", [])}
        if "preis-korrektur" not in labels or "namensentfernung" in labels: continue
        status = next((RESOLVED[l] for l in ("uebernommen", "abgelehnt") if l in labels), None)
        closed = (it.get("closed_at") or "")[:10]
        if status is None or closed < cutoff: continue
        rid = parse_body(it.get("body")).get("reportId", "").strip()
        if not re.fullmatch(r"r-[0-9a-f]{4,16}", rid): continue
        out.append({"reportId": rid, "issue": it["number"], "status": status, "closedAt": closed})
    return sorted(out, key=lambda e: e["issue"])

def build(issues, now):
    groups = {}
    for it in issues:
        if "pull_request" in it or it.get("state") != "open": continue
        labels = {l["name"] for l in it.get("labels", [])}
        if "preis-korrektur" not in labels or labels & SKIP: continue
        # Nur Issues aus dem Preis-Formular (andere Formulare, z. B. namensentfernung.yml, nie als Preis werten)
        if "(tariffId)" not in (it.get("body") or ""): continue
        f = parse_body(it.get("body"))
        tid, cpo = f.get("tariffId", "").strip(), f.get("cpo", "").strip() or "*"
        ct = f.get("chargeType", "").strip().upper()
        field = f.get("field", "pricePerKwh").strip()
        val = num(f.get("reportedValue", ""))
        if not re.fullmatch(r"[a-z0-9-]{1,40}", tid) or ct not in ("AC", "DC") or val is None: continue
        if field not in ("pricePerKwh", "monthlyFee", "blockingFee"): continue
        if not (cpo == "*" or re.fullmatch(r"[a-z0-9-]{1,40}", cpo)): continue
        k = (tid, cpo, ct, field)
        g = groups.setdefault(k, {"tariffId": tid, "cpo": cpo, "chargeType": ct, "field": field,
                                  "reportedValue": val, "count": 0, "since": None, "status": "in-pruefung",
                                  "issues": [], "reportIds": [], "_latest": ""})
        created = it.get("created_at", "")
        g["count"] += 1
        g["issues"].append(it["number"])
        rid = f.get("reportId", "").strip()
        if re.fullmatch(r"r-[0-9a-f]{4,16}", rid): g["reportIds"].append(rid)
        day = created[:10]
        if g["since"] is None or day < g["since"]: g["since"] = day
        if created >= g["_latest"]: g["_latest"], g["reportedValue"] = created, val
        if "quelle-fehlt" in labels and g["status"] == "in-pruefung": g["status"] = "quelle-fehlt"
        if "pr-offen" in labels or "bestaetigt" in labels: g["status"] = "bestaetigt"
    reports = []
    for g in sorted(groups.values(), key=lambda g: (g["tariffId"], g["cpo"], g["chargeType"], g["field"])):
        g.pop("_latest"); g["issues"].sort(); reports.append(g)
    return {"schema": "abocoach.reports/1", "generatedAt": now, "reports": reports, "resolved": resolved_entries(issues, now)}

if __name__ == "__main__":
    issues = json.load(open(sys.argv[1], encoding="utf-8"))
    if issues and isinstance(issues[0], list): issues = [i for page in issues for i in page]
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = build(issues, now)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1); f.write("\n")
    print(f"{len(data['reports'])} Gruppen aus {sum(r['count'] for r in data['reports'])} Meldungen")
