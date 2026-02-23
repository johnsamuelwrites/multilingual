importieren math
von math importieren sqrt als root_fn

sei gemeinsamer_zaehler = 3

def erhoehe_global():
    global gemeinsamer_zaehler
    gemeinsamer_zaehler = gemeinsamer_zaehler + 2
    rückgabe gemeinsamer_zaehler

def erstelle_zaehler(startwert):
    sei total = startwert
    def schritt():
        nichtlokal total
        total = total + 1
        rückgabe total
    rückgabe schritt

sei naechster_zaehler = erstelle_zaehler(5)
sei erster_schritt = naechster_zaehler()
sei zweiter_schritt = naechster_zaehler()

mit oeffnen("tmp_complete_en.txt", "w", encoding="utf-8") als datei_schreiben:
    datei_schreiben.write("ok")

sei datei_text = ""
mit oeffnen("tmp_complete_en.txt", "r", encoding="utf-8") als datei_lesen:
    datei_text = datei_lesen.read()

sei gezippte_paare = liste(zippen([1, 2, 3], [4, 5, 6]))
sei einzigartig_werte = menge([1, 1, 2, 3])
sei feste_werte = tupel([10, 20, 30])
sei erstes_element, *mittlere_elemente, letztes_element = [1, 2, 3, 4]
sei zusammengefuehrte_karte = {**{"x": 1}, **{"y": 2}}

def etikett_format(a, /, *, b):
    rückgabe f"{a}-{b:.1f}"

sei formatiert = etikett_format(7, b=3.5)
sei samen = 0
sei walrus_wert = (samen := samen + 9)

klasse ZaehlerBox:
    def __init__(self, startbasis):
        self.wert = startbasis

klasse ZaehlerBoxKind(ZaehlerBox):
    def __init__(self, startbasis):
        oberklasse(ZaehlerBoxKind, self).__init__(startbasis)
        self.wert = self.wert + 1

def erzeuge_drei():
    für index in bereich(3):
        erzeugen index

sei produzierter_gesamt = summe(erzeuge_drei())
sei verarbeitet = Falsch

versuchen:
    wenn laenge(einzigartig_werte) > 2:
        auslösen ValueError("boom")
ausnahme ValueError als behandelter_fehler:
    verarbeitet = Wahr
schließlich:
    sei wurzel_wert = ganz(root_fn(16))

sei temp_wert = 99
loschen temp_wert

sei schleife_aku = 0
für n in bereich(6):
    wenn n == 0:
        pass
    wenn n == 4:
        abbrechen
    wenn n % 2 == 0:
        weiter
    schleife_aku = schleife_aku + n

sei flagge_ok = Wahr und nicht Falsch
behaupten flagge_ok

sei kind_box = ZaehlerBoxKind(40)

ausgeben(erhoehe_global())
ausgeben(erster_schritt, zweiter_schritt)
ausgeben(datei_text)
ausgeben(laenge(gezippte_paare), laenge(einzigartig_werte), feste_werte[1])
ausgeben(erstes_element, mittlere_elemente, letztes_element)
ausgeben(kind_box.wert)
ausgeben(produzierter_gesamt, wurzel_wert, verarbeitet)
ausgeben(zusammengefuehrte_karte["x"] + zusammengefuehrte_karte["y"], formatiert, walrus_wert)
ausgeben(schleife_aku)
ausgeben(gemeinsamer_zaehler ist Nichts)

# Loop else clauses
sei elemente_gefunden = Falsch
für element in bereich(3):
    wenn element == 10:
        elemente_gefunden = Wahr
        abbrechen
sonst:
    elemente_gefunden = "not_found"

sei waehrend_sonst_val = 0
solange waehrend_sonst_val < 2:
    waehrend_sonst_val = waehrend_sonst_val + 1
sonst:
    waehrend_sonst_val = waehrend_sonst_val + 10

# Starred unpacking variations
sei a, *rest = [10, 20, 30, 40]
sei *init, b = [10, 20, 30, 40]
sei c, *mittlere, d = [10, 20, 30, 40]

# Set comprehension
sei quadrierte_menge = {x * x für x in bereich(5)}

# Extended builtins
sei potenz_ergebnis = potenz(2, 8)
sei divmod_ergebnis = divmod(17, 5)

# Yield from generator
def delegierer_gen():
    erzeugen von bereich(3)

sei delegiert = liste(delegierer_gen())

ausgeben(elemente_gefunden, waehrend_sonst_val)
ausgeben(a, rest, init, b, c, mittlere, d)
ausgeben(sortiert(quadrierte_menge))
ausgeben(potenz_ergebnis, divmod_ergebnis)
ausgeben(delegiert)

# Numeric literals
sei hex_zahl = 0xFF
sei okt_zahl = 0o17
sei bin_zahl = 0b1010
sei wiss_zahl = 1.5e3

# Augmented assignments
sei erweitert = 10
erweitert += 5
erweitert -= 2
erweitert *= 3
erweitert //= 4
erweitert %= 3

# Bitwise operators
sei bit_und = 0b1010 & 0b1100
sei bit_oder = 0b1010 | 0b0101
sei bit_xor = 0b1010 ^ 0b1111
sei bit_links = 1 << 3
sei bit_rechts = 64 >> 2

# Chained assignment
sei kette_a = kette_b = kette_c = 0

# Type annotations
sei typisiert: ganz = 99

def annotiert(x: ganz, y: gleitkomma) -> zeichenkette:
    rückgabe zeichenkette(x + y)

# Ternary expression
sei ternar = "yes" wenn typisiert > 0 sonst "no"

# Default params, *args, **kwargs
def mehrfach_parameter(base, extra=1, *args, **kwargs):
    rückgabe base + extra + summe(args)
sei mehrfach_ergebnis = mehrfach_parameter(10, 2, 3, 4, key=5)

# Lambda
sei quadrat = lambda x: x * x

# List/dict comprehensions and generator expression
sei liste_c = [x * 2 für x in bereich(4)]
sei dict_c = {zeichenkette(k): k * k für k in bereich(3)}
sei gen_c = liste(x + 1 für x in bereich(3))
sei verschachtelt_c = [i + j für i in bereich(2) für j in bereich(2)]
sei filter_c = [x für x in bereich(6) wenn x % 2 == 0]

# try/except/else
sei versuch_sonst = 0
versuchen:
    versuch_sonst = ganz("7")
ausnahme ValueError:
    versuch_sonst = -1
sonst:
    versuch_sonst += 1

# Exception chaining
sei verkettet = Falsch
versuchen:
    versuchen:
        auslösen ValueError("v")
    ausnahme ValueError als ve:
        auslösen RuntimeError("r") von ve
ausnahme RuntimeError:
    verkettet = Wahr

# Multiple except handlers
sei mehrfach_ausnahme = 0
versuchen:
    auslösen TypeError("t")
ausnahme ValueError:
    mehrfach_ausnahme = 1
ausnahme TypeError:
    mehrfach_ausnahme = 2

# Match/case with default
sei zuordnungs_wert = 2
sei zuordnungs_resultat = "other"
zuordnen zuordnungs_wert:
    fall 1:
        zuordnungs_resultat = "one"
    fall 2:
        zuordnungs_resultat = "two"
    standard:
        zuordnungs_resultat = "default"

# Decorator
def verdoppler(func):
    def huelle(*args, **kwargs):
        rückgabe func(*args, **kwargs) * 2
    rückgabe huelle

@verdoppler
def zehn():
    rückgabe 10

sei deko_resultat = zehn()

# Multiple inheritance, static/class methods, property
klasse Mischung:
    def mischen(self):
        rückgabe 1

klasse BasisZwei:
    def __init__(self, start):
        self.value = start

klasse Kombiniert(BasisZwei, Mischung):
    @staticmethod
    def bezeichnung():
        rückgabe "combined"
    @classmethod
    def bauen(cls, v):
        rückgabe cls(v)
    @property
    def verdoppelt(self):
        rückgabe self.value * 2

sei kombi_obj = Kombiniert.bauen(3)
sei eigenschaft = kombi_obj.verdoppelt

# Docstring
def mit_doc():
    """A docstring."""
    rückgabe Wahr

ausgeben(hex_zahl, okt_zahl, bin_zahl, wiss_zahl)
ausgeben(erweitert, bit_und, bit_oder, bit_xor, bit_links, bit_rechts)
ausgeben(kette_a, kette_b, kette_c)
ausgeben(typisiert, annotiert(3, 1.5), ternar)
ausgeben(mehrfach_ergebnis, quadrat(5))
ausgeben(liste_c, dict_c, gen_c)
ausgeben(verschachtelt_c, filter_c)
ausgeben(versuch_sonst, verkettet, mehrfach_ausnahme)
ausgeben(zuordnungs_resultat, deko_resultat, eigenschaft)
ausgeben(mit_doc())
