import unittest, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from anonymize import is_private_person, display_name, PRIVATE

PERSONS = ["Christian Uhlrich", "hans-joachim mayer", "Katrin Schneiderhan", "Stefan Diem Diem", "Dr. Thomas Decker",
           "Familie Müller", "Gunther Lämmermann", "Hans-Jürgen Keßler", "Claus Peter Spiegel",
           "Florian Dohn (Einzelunternehmer)", "Hajro Mujevic, Einzelunternehmer", "Fa. Elisabeth Schubert", "Johann Hofer - Hofer",
           "Christian Althof", "Thomas Stromberg", "Peter Park", "Michael Sportelli", "Andreas Autenrieth", "Thomas S", "Martin Egbert"]
KEEP = ["EnBW mobility+ AG", "Stadtwerke Bremen", "swb Vertrieb Bremen GmbH", "Tesla Germany GmbH", "Schmidt & Söhne KG",
        "Tennisverein Grün-Weiß e.V.", "Gemeinde Musterdorf", "Pension Engel", "Landgasthof Krone", "Solarcollect", "TM Carports",
        "VINOTHEUM", "Haus Felsenburg", "Edeka Klein", "Schreinerei Berger", "Photovoltaik Holstein", "Gaststätte Reinermann",
        "Färber Ingenieurbüro", "Horse Lake Ranch", "Christian Müller GmbH", "Thomas Bauer e.K.", "Bernhard Schneider Vermietungen",
        "Autohaus Meyer", "Hotel Adler", "Union Investment Real", "IONITY GmbH", "Diako Nordfriesland gGmbH", "Gerd Krumland Landwirtschaft", "Kreis Herford", ""]

class T(unittest.TestCase):
    def test_persons(self):
        for n in PERSONS:
            self.assertTrue(is_private_person(n), n)
            self.assertEqual(display_name(n), PRIVATE)
    def test_keep(self):
        for n in KEEP:
            self.assertFalse(is_private_person(n), n)
            self.assertEqual(display_name(n), n)

if __name__ == "__main__": unittest.main()
