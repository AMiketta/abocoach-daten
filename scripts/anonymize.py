"""Ersetzt Betreibernamen, die nach Privatpersonen aussehen, durch „privat“.

Heuristik (konservativ zugunsten des Datenschutzes, aber ohne Firmen zu verlieren):
1. Enthält der Name eine Rechtsform oder einen öffentlichen Träger (GmbH, AG, KG, e.V., Stadtwerke, Gemeinde …) → bleibt.
2. „Familie …“, „Herr/Frau …“ → privat.
3. 2–5 Wörter, nur Buchstaben/Bindestrich/Punkt, erstes Wort (ohne Titel wie „Dr.“) ist ein bekannter Vorname → privat,
   außer ein weiteres Wort ist ein Firmenwort („Bernhard Schneider Vermietungen“). Der Nachname allein zählt nie als Firmenwort.
   Zusätze wie „(Einzelunternehmer)“, „, Einzelunternehmer“ oder „Fa.“ werden vorher entfernt (Einzelunternehmen = Person).
4. Zwei oder drei Wörter im Muster „Vorname Nachname“ (je Großbuchstabe + Kleinbuchstaben), erstes Wort kein
   Branchen-/Markenwort (Haus, Burg, Edeka, Schreinerei …) → privat. Fängt seltene Vornamen ab.
Alles andere bleibt (z. B. Marken wie „Solarcollect“, „TM Carports“, „Pension Engel“, „Haus Felsenburg“).
"""
import re

PRIVATE = "privat"

# Rechtsformen und öffentliche Träger: immer Firma/Organisation.
LEGAL = re.compile(r"""(?ix)(
 \bgmbh\b|\bggmbh\b|\bmbh\b|\bag\b|\bkg\b|\bkgaa\b|\bohg\b|\bgbr\b|\begbr\b|\bug\b|\bse\b|\beg\b|\be\.\s?g\.|\be\.\s?v\.?|\bev\b|\be\.\s?k(fm|fr)?\.?|
 \bltd\b|\binc\b|\bllc\b|\bb\.v\.|\bs\.a\.|\bsarl\b|\bco\.|&|\+|\bpartg|\bstiftung|\bverein|\bgenossenschaft|\bi\.\s?g\.|
 stadtwerk|aktiengesellschaft|institut|wissenschaft|\bwerke\b|gemeinde|\bstadt\b|landkreis|\bkreis\b|verband|\bamt\b|verwaltung|ministerium|universit|hochschule|kirche|pfarr
)""")

# Firmen-/Branchenwörter (auch als Wortteil). Bei „Vorname Nachname“ nicht auf den Nachnamen angewendet,
# sonst würden Nachnamen wie Stromberg, Althof oder Sportelli fälschlich als Firma gelten.
WEAK = re.compile(r"""(?ix)(
 schule|klinik|krankenhaus|\bbank\b|sparkasse|volksbank|raiffeisen|versicherung|holding|gruppe|group|
 energie|energy|strom|solar|power|elektro|elektrik|electric|mobil|charg|lade|tankstelle|\btank|
 auto|kfz|garage|werkstatt|fahrzeug|motor|\bcars?\b|
 hotel|pension|gasthof|gasthaus|restaurant|ferien|camping|brauerei|bäckerei|metzgerei|weingut|winzer|hof\b|
 markt|handel|service|technik|technolog|\bbau\b|immobilien|vermiet|consult|logistik|transport|spedition|praxis|kanzlei|apotheke|
 zentrum|center|park\b|parkhaus|\binstitut|\bclub\b|sport|\bwerk\b|gesellschaft|betrieb|unternehmen|agentur|studio|shop|
 landwirtschaft|international|deutschland|germany|europe
)""")

# Kompatibilität: alles, was auf eine Firma hindeutet
COMPANY = re.compile(LEGAL.pattern.replace("(?ix)", "") + "|" + WEAK.pattern.replace("(?ix)", ""), re.IGNORECASE | re.VERBOSE)

TITLES = {"dr", "dr.", "prof", "prof.", "dipl.-ing.", "dipl.", "ing.", "von", "van", "de", "der"}

# Häufige Vornamen in Deutschland (klein geschrieben). Erweiterbar; Treffer nur am Wortanfang des Namens.
FIRST_NAMES = set("""
alexander alexandra alfred alois andrea andreas andrej angela angelika anja anke anna anne annette anton antonia armin arne arnold
astrid axel barbara bastian beate benedikt benjamin bernd bernhard bettina birgit björn bodo brigitte bruno carina carl carmen carola
carolin caroline carsten charlotte christa christian christiane christina christine christoph christopher claudia clemens cornelia
dagmar daniel daniela david denis dennis detlef diana dieter dietmar dirk dominik doris dorothea edgar edith egon elke elisabeth
ellen emil erich erik erika ernst erwin eva fabian felix florian frank franz franziska frederik friedrich fritz gabriele georg gerald
gerd gerda gerhard gernot gertrud gisela günter günther guido gudrun hannah hannes hans harald hartmut heike heiko heinrich heinz
helena helga helmut helmuth henning henrik henryk herbert hermann horst hubert hugo ilse ina ines ingo ingrid irene iris isabel
jakob jan jana janina jannik jens jessica joachim jochen johann johanna johannes jonas jonathan josef joseph julia julian juliane
jürgen jutta kai karin karl karl-heinz karsten katharina kathrin katja katrin klaus konrad kristina lars laura lea lena leon leonie
lisa lothar lucas ludwig luis lukas lutz magdalena maik malte manfred manuel manuela marc marcel marco marcus margarete maria
marianne mario marion marius mark markus marlene martha martin martina mathias matthias max maximilian melanie michael michaela
mike miriam monika moritz nadine natalie nicole niklas nico nils nina norbert olaf oliver otmar otto pascal patricia patrick paul
peter petra philipp rainer ralf ralph regina reinhard reinhold renate rene richard robert roland rolf roman rosemarie rudolf ruth
sabine sabrina sandra sarah sascha sebastian siegfried silke simon simone sonja stefan stefanie steffen stephan stephanie stephen
susanne sven svenja tanja thomas thorsten tim timo tobias torsten udo ulf ulrich ulrike ursula ute uwe valentin vanessa verena
viktor volker walter waltraud werner wilhelm willi wolfgang yvonne
jörg holger heino inge inken marita knut finn adrian eduard john boris rafael gregor anneliese antonio hendrik ronald dino
steven christin andre andré robin marvin gerrit derek jean nicolai frithjof falk waldemar winnie silvia tatiana silvio rico
dietlind marek marten joana yannic philippe birk janusz jirka krzysztof erkan oussama robbyn gerburgis aissenguil
""".split())

# Erstes Wort eines Zwei-Wort-Namens, das auf ein Geschäft/Ort statt einen Vornamen hindeutet (klein geschrieben).
BUSINESS_FIRST = set("""
haus burg schloss kloster villa gut mühle alm hütte ranch farm hof café cafe bistro bar salon atelier studio living wohnen
edeka rewe aldi lidl netto penny kaufland globus norma tegut famila marktkauf rossmann dm ikea obi hornbach bauhaus toom
zahnärzte zahnarzt ärzte arzt tierarzt steuerberater architekten architekt schreinerei tischlerei zimmerei malerei dachdecker
bäckerei metzgerei fleischerei friseur optik physio pflege senioren kita kinderhaus jugendhaus feuerwehr polizei rathaus
freizeit wellness therme bad camping golf reit reiterhof tennis fitness crossfit yoga sportpark kultur museum theater kino
landwirtschaft agrar bio öko photovoltaik fotovoltaik pv zeltwiese gaststätte landhaus deele ingenieurbüro investment real weingut wein bier brauhaus hofladen gärtnerei baumschule blumen garten
""".split())

_NAME = re.compile(r"^[A-ZÄÖÜ][a-zäöüßéèáàëïçñ]+(-[A-ZÄÖÜ][a-zäöüßéèáàëïçñ]+)?$")

_WORD = re.compile(r"^[A-Za-zÄÖÜäöüßéèáàëïçñ.'-]+$")

_SOLE = re.compile(r"(?i)\(?\s*,?\s*einzel(unternehmer(in)?|unternehmung|kaufmann|kauffrau)\s*\)?|^fa\.\s*")
_BUSINESS_SUFFIX = ("büro", "technik", "service", "haus", "hof", "bau", "tik", "markt", "handel")

def is_private_person(name: str) -> bool:
    n = " ".join(_SOLE.sub(" ", name or "").replace(",", " ").split())
    if not n or LEGAL.search(n):
        return False
    low = n.lower()
    if re.match(r"^(familie|fam\.|herr|frau|eheleute)\b", low):
        return True
    words = n.split(" ")
    if not (2 <= len(words) <= 5) or not all(_WORD.match(w) for w in words):
        return False
    rest = [w for w in words if w.lower() not in TITLES]
    if len(rest) < 2:
        return False
    first = rest[0].lower()
    if first in FIRST_NAMES or first.split("-")[0] in FIRST_NAMES:
        # „Vorname Nachname“ ist immer eine Person; bei weiteren Wörtern (außer Titeln) deutet ein Firmenwort auf ein Geschäft hin
        extra = rest[1:-1] + ([rest[-1]] if len(rest) > 2 else [])
        return not any(WEAK.search(w) or w.lower() in BUSINESS_FIRST for w in extra)
    if WEAK.search(n):
        return False
    return (len(words) in (2, 3) and all(_NAME.match(w) for w in words)
            and not any(w.lower() in BUSINESS_FIRST or w.lower().endswith(_BUSINESS_SUFFIX) for w in words))

def display_name(name: str) -> str:
    return PRIVATE if is_private_person(name) else name
