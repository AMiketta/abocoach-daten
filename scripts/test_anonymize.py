import unittest, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from anonymize import is_private_person, display_name, PRIVATE, name_hash, load_overrides
import json, tempfile

PERSONS = ["Christian Uhlrich", "hans-joachim mayer", "Katrin Schneiderhan", "Stefan Diem Diem", "Dr. Thomas Decker",
           "Familie Müller", "Gunther Lämmermann", "Hans-Jürgen Keßler", "Claus Peter Spiegel",
           "Florian Dohn (Einzelunternehmer)", "Hajro Mujevic, Einzelunternehmer", "Fa. Elisabeth Schubert", "Johann Hofer - Hofer",
           "Christian Althof", "Thomas Stromberg", "Peter Park", "Michael Sportelli", "Andreas Autenrieth", "Thomas S", "Martin Egbert"]
KEEP = ["EnBW mobility+ AG", "Stadtwerke Bremen", "swb Vertrieb Bremen GmbH", "Tesla Germany GmbH", "Schmidt & Söhne KG",
        "Tennisverein Grün-Weiß e.V.", "Gemeinde Musterdorf", "Pension Engel", "Landgasthof Krone", "Solarcollect", "TM Carports",
        "VINOTHEUM", "Haus Felsenburg", "Edeka Klein", "Schreinerei Berger", "Photovoltaik Holstein", "Gaststätte Reinermann",
        "Färber Ingenieurbüro", "Horse Lake Ranch", "Christian Müller GmbH", "Thomas Bauer e.K.", "Bernhard Schneider Vermietungen",
        "Autohaus Meyer", "Hotel Adler", "Union Investment Real", "IONITY GmbH", "Diako Nordfriesland gGmbH", "Gerd Krumland Landwirtschaft", "Kreis Herford", "Max-Planck-Institut f. Multidisziplinäre Naturwissenschaften", "Mark-E Aktiengesellschaft", ""]

class T(unittest.TestCase):
    def test_persons(self):
        for n in PERSONS:
            self.assertTrue(is_private_person(n), n)
            self.assertEqual(display_name(n), PRIVATE)
    def test_keep(self):
        for n in KEEP:
            self.assertFalse(is_private_person(n), n)
            self.assertEqual(display_name(n), n)

class Overrides(unittest.TestCase):
    def test_known_rest_cases_are_private(self):
        for n in ["Steuerberater Michael Lommen", "DetlefMelanie Schneider", "  detlefmelanie   SCHNEIDER "]:
            self.assertTrue(is_private_person(n), n)
    def test_file_contains_no_plain_names(self):
        raw = open(os.path.join(os.path.dirname(__file__), "anonymize_overrides.json"), encoding="utf-8").read()
        self.assertNotIn("Lommen", raw); self.assertNotIn("DetlefMelanie", raw)
    def test_keep_and_force(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump({"force_private": ["Solarcollect", name_hash("TM Carports")], "keep": ["Christian Uhlrich", "Peter Park"]}, f)
        ov = load_overrides(f.name); os.unlink(f.name)
        self.assertTrue(is_private_person("Solarcollect", ov))
        self.assertTrue(is_private_person("tm  carports", ov))
        self.assertFalse(is_private_person("Christian Uhlrich", ov))
        self.assertFalse(is_private_person("Peter Park", ov))
        self.assertTrue(is_private_person("Thomas Stromberg", ov), "Heuristik greift weiter")
    def test_missing_file(self):
        self.assertEqual(load_overrides("/nonexistent.json"), (set(), set()))

if __name__ == "__main__": unittest.main()
