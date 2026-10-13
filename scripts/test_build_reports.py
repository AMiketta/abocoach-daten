import unittest, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from build_reports import build, parse_body

BODY = "### Tarif-ID (tariffId)\n\nenbw-m\n\n### Betreiber (cpo)\n\nenbw\n\n### Ladeart (chargeType)\n\nDC\n\n### Feld (field)\n\npricePerKwh\n\n### Richtiger Wert in € brutto (reportedValue)\n\n0,49\n\n### Kommentar (comment)\n\n_No response_\n\n### Meldungs-ID (reportId)\n\nr-7f3c9a\n"

def issue(n, labels=("preis-korrektur", "neu"), body=BODY, created="2026-10-13T08:00:00Z"):
    return {"number": n, "state": "open", "labels": [{"name": l} for l in labels], "body": body, "created_at": created}

class T(unittest.TestCase):
    def test_parse(self):
        f = parse_body(BODY)
        self.assertEqual(f["tariffId"], "enbw-m"); self.assertNotIn("comment", f)
    def test_group(self):
        r = build([issue(1), issue(2, created="2026-10-14T08:00:00Z")], "x")["reports"]
        self.assertEqual(len(r), 1); self.assertEqual(r[0]["count"], 2); self.assertEqual(r[0]["reportedValue"], 0.49)
        self.assertEqual(r[0]["since"], "2026-10-13"); self.assertEqual(r[0]["issues"], [1, 2])
    def test_skip(self):
        self.assertEqual(build([issue(1, labels=("preis-korrektur", "spam")), issue(2, labels=("frage",))], "x")["reports"], [])
    def test_quelle_fehlt(self):
        self.assertEqual(build([issue(1, labels=("preis-korrektur", "quelle-fehlt"))], "x")["reports"][0]["status"], "quelle-fehlt")
    def test_invalid(self):
        self.assertEqual(build([issue(1, body=BODY.replace("DC", "XY"))], "x")["reports"], [])

class Removal(unittest.TestCase):
    def test_name_removal_never_parsed(self):
        body = "### Betreibername wie in den Daten (operatorName)\n\nMax Muster\n"
        self.assertEqual(build([issue(1, labels=("namensentfernung",), body=body),
                                issue(2, labels=("preis-korrektur", "namensentfernung")),
                                issue(3, body=body)], "x")["reports"], [])

if __name__ == "__main__": unittest.main()
