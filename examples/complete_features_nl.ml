importeer math
van math importeer sqrt zoals root_fn
importeer asyncio

laat gedeelde_teller = 3

definieer verhoog_globaal():
    globaal gedeelde_teller
    gedeelde_teller = gedeelde_teller + 2
    retourneer gedeelde_teller

definieer maak_teller(begin):
    laat total = begin
    definieer stap():
        niet_lokaal total
        total = total + 1
        retourneer total
    retourneer stap

laat volgende_teller = maak_teller(5)
laat eerste_stap = volgende_teller()
laat tweede_stap = volgende_teller()

met openen("tmp_complete_en.txt", "w", encoding="utf-8") zoals schrijf_handvat:
    schrijf_handvat.write("ok")

laat bestand_tekst = ""
met openen("tmp_complete_en.txt", "r", encoding="utf-8") zoals lees_handvat:
    bestand_tekst = lees_handvat.read()

laat gekoppelde_paren = lijst(koppel([1, 2, 3], [4, 5, 6]))
laat unieke_waarden = verzameling([1, 1, 2, 3])
laat vaste_waarden = tuple([10, 20, 30])
laat eerste_element, *middelste_elementen, laatste_element = [1, 2, 3, 4]
laat samengevoegde_kaart = {**{"x": 1}, **{"y": 2}}

definieer label_opmaken(a, /, *, b):
    retourneer f"{a}-{b:.1f}"

laat geformatteerd_label = label_opmaken(7, b=3.5)
laat zaad = 0
laat snor_waarde = (zaad := zaad + 9)

klasse TellerDoos:
    definieer __init__(self, begin_basis):
        self.waarde = begin_basis

klasse TellerDoosKind(TellerDoos):
    definieer __init__(self, begin_basis):
        superklasse(TellerDoosKind, self).__init__(begin_basis)
        self.waarde = self.waarde + 1

definieer produceer_drie():
    voor index in bereik(3):
        lever index

laat geproduceerd_totaal = som(produceer_drie())
laat afgehandeld = Onwaar

probeer:
    als lengte(unieke_waarden) > 2:
        werp ValueError("boom")
behalve ValueError zoals afgehandelde_fout:
    afgehandeld = Waar
eindelijk:
    laat wortel_waarde = geheel(root_fn(16))

laat tijdelijke_waarde = 99
verwijder tijdelijke_waarde

laat lus_accumulatie = 0
voor n in bereik(6):
    als n == 0:
        sla_over
    als n == 4:
        breek
    als n % 2 == 0:
        ga_door
    lus_accumulatie = lus_accumulatie + n

laat vlag_ok = Waar en niet Onwaar
bevestig vlag_ok

laat kind_doos = TellerDoosKind(40)

afdrukken(verhoog_globaal())
afdrukken(eerste_stap, tweede_stap)
afdrukken(bestand_tekst)
afdrukken(lengte(gekoppelde_paren), lengte(unieke_waarden), vaste_waarden[1])
afdrukken(eerste_element, middelste_elementen, laatste_element)
afdrukken(kind_doos.waarde)
afdrukken(geproduceerd_totaal, wortel_waarde, afgehandeld)
afdrukken(samengevoegde_kaart["x"] + samengevoegde_kaart["y"], geformatteerd_label, snor_waarde)
afdrukken(lus_accumulatie)
afdrukken(gedeelde_teller is Geen)

# Loop else clauses
laat elementen_gevonden = Onwaar
voor element in bereik(3):
    als element == 10:
        elementen_gevonden = Waar
        breek
anders:
    elementen_gevonden = "not_found"

laat terwijl_anders_waarde = 0
terwijl terwijl_anders_waarde < 2:
    terwijl_anders_waarde = terwijl_anders_waarde + 1
anders:
    terwijl_anders_waarde = terwijl_anders_waarde + 10

# Starred unpacking variations
laat a, *rest = [10, 20, 30, 40]
laat *init, b = [10, 20, 30, 40]
laat c, *midden, d = [10, 20, 30, 40]

# Set comprehension
laat gekwadrateerde_verzameling = {x * x voor x in bereik(5)}

# Extended builtins
laat macht_resultaat = macht(2, 8)
laat divmod_resultaat = deelrest(17, 5)

# Yield from generator
definieer delegerende_gen():
    lever van bereik(3)

laat gedelegeerd = lijst(delegerende_gen())

afdrukken(elementen_gevonden, terwijl_anders_waarde)
afdrukken(a, rest, init, b, c, midden, d)
afdrukken(gesorteerd(gekwadrateerde_verzameling))
afdrukken(macht_resultaat, divmod_resultaat)
afdrukken(gedelegeerd)

# Numeric literals
laat hex_getal = 0xFF
laat oct_getal = 0o17
laat bin_getal = 0b1010
laat sci_getal = 1.5e3

# Augmented assignments
laat verhoogd = 10
verhoogd += 5
verhoogd -= 2
verhoogd *= 3
verhoogd //= 4
verhoogd %= 3

# Bitwise operators
laat bit_en = 0b1010 & 0b1100
laat bit_of = 0b1010 | 0b0101
laat bit_xor = 0b1010 ^ 0b1111
laat bit_links = 1 << 3
laat bit_rechts = 64 >> 2

# Chained assignment
laat keten_a = keten_b = keten_c = 0

# Type annotations
laat getypt: geheel = 99

definieer geannoteerd(x: geheel, y: drijvend) -> tekenreeks:
    retourneer tekenreeks(x + y)

# Ternary expression
laat ternair = "yes" als getypt > 0 anders "no"

# Default params, *args, **kwargs
definieer multi_params_nl(base, extra=1, *args, **kwargs):
    retourneer base + extra + som(args)
laat multi_resultaat = multi_params_nl(10, 2, 3, 4, key=5)

# Lambda
laat kwadraat = lambda x: x * x

# List/dict comprehensions and generator expression
laat lijst_c = [x * 2 voor x in bereik(4)]
laat dict_c = {tekenreeks(k): k * k voor k in bereik(3)}
laat gen_c = lijst(x + 1 voor x in bereik(3))
laat genest_c = [i + j voor i in bereik(2) voor j in bereik(2)]
laat filter_c = [x voor x in bereik(6) als x % 2 == 0]

# try/except/else
laat probeer_anders = 0
probeer:
    probeer_anders = geheel("7")
behalve ValueError:
    probeer_anders = -1
anders:
    probeer_anders += 1

# Exception chaining
laat gekoppeld = Onwaar
probeer:
    probeer:
        werp ValueError("v")
    behalve ValueError zoals ve:
        werp RuntimeError("r") van ve
behalve RuntimeError:
    gekoppeld = Waar

# Multiple except handlers
laat multi_uitz = 0
probeer:
    werp TypeError("t")
behalve ValueError:
    multi_uitz = 1
behalve TypeError:
    multi_uitz = 2

# Match/case with default
laat match_waarde = 2
laat match_resultaat = "other"
vergelijk match_waarde:
    geval 1:
        match_resultaat = "one"
    geval 2:
        match_resultaat = "two"
    standaard:
        match_resultaat = "default"

# Decorator
definieer verdubbelaar(func):
    definieer omhul(*args, **kwargs):
        retourneer func(*args, **kwargs) * 2
    retourneer omhul

@verdubbelaar
definieer tien():
    retourneer 10

laat deco_resultaat = tien()

# Multiple inheritance, static/class methods, property
klasse MixInNl:
    definieer meng(self):
        retourneer 1

klasse BasisTwee:
    definieer __init__(self, start):
        self.value = start

klasse Gecombineerd(BasisTwee, MixInNl):
    @staticmethod
    definieer label_nl():
        retourneer "combined"
    @classmethod
    definieer bouw(cls, v):
        retourneer cls(v)
    @property
    definieer verdubbeld(self):
        retourneer self.value * 2

laat comb_obj = Gecombineerd.bouw(3)
laat eigenschap = comb_obj.verdubbeld

# Docstring
definieer met_doc():
    """A docstring."""
    retourneer Waar

afdrukken(hex_getal, oct_getal, bin_getal, sci_getal)
afdrukken(verhoogd, bit_en, bit_of, bit_xor, bit_links, bit_rechts)
afdrukken(keten_a, keten_b, keten_c)
afdrukken(getypt, geannoteerd(3, 1.5), ternair)
afdrukken(multi_resultaat, kwadraat(5))
afdrukken(lijst_c, dict_c, gen_c)
afdrukken(genest_c, filter_c)
afdrukken(probeer_anders, gekoppeld, multi_uitz)
afdrukken(match_resultaat, deco_resultaat, eigenschap)
afdrukken(met_doc())

# Bit-gewijze uitgebreide toewijzingen en macht (v0.6.0)
laat bau_bits = 0b1111
bau_bits &= 0b1010
bau_bits |= 0b0100
bau_bits ^= 0b0011
bau_bits <<= 1
bau_bits >>= 2
laat macht_aug = 2
macht_aug **= 4

# Bytes-literal (v0.6.0)
laat byte_data = b"hello"
laat byte_len = lengte(byte_data)

# Tekenreeks samenvoegen, indexeren en segmenteren (v0.6.0)
laat tekstr_x = "hello"
laat tekstr_y = " world"
laat samengev = tekstr_x + tekstr_y
laat tekstr_idx = tekstr_x[1]
laat tekstr_seg = tekstr_x[1:3]

# Tupel-literal (v0.6.0)
laat tupel_nl = (10, 20, 30)
laat elem_tupel_nl = tupel_nl[1]

# For-lus over lijstvariabele en lijstcomprehensie (v0.6.0)
laat iter_lijst = [10, 20, 30]
laat iter_som = 0
voor iter_val in iter_lijst:
    iter_som = iter_som + iter_val

laat dubb_bron = [1, 2, 3, 4]
laat dubbele_lijst = [v * 2 voor v in dubb_bron]

# Uitgebreide vergelijking: tekenreeks, Geen, getal, tupel (v0.6.0)
laat tekstr_m = "hello"
laat result_tekstr_m = "geen"
vergelijk tekstr_m:
    geval "hello":
        result_tekstr_m = "hi"
    geval "bye":
        result_tekstr_m = "goodbye"
    standaard:
        result_tekstr_m = "unknown"

laat val_geen = Geen
laat result_geen = "gedefinieerd"
vergelijk val_geen:
    geval Geen:
        result_geen = "null"
    standaard:
        result_geen = "other"

laat val_num_m = 42
laat result_num_m = 0
vergelijk val_num_m:
    geval 42:
        result_num_m = val_num_m
    standaard:
        result_num_m = 0

laat val_tupel_m = (1, 2)
laat result_tupel_m = "no"
vergelijk val_tupel_m:
    geval (1, 2):
        result_tupel_m = "yes"
    standaard:
        result_tupel_m = "no"

# async def, await, async for, async with (v0.6.0)
async definieer verdubbel_async(n):
    wacht asyncio.sleep(0)
    retourneer n * 2

async definieer gen_async_nl():
    voor v in range(3):
        lever v

async definieer taak_async_voor():
    laat totaal_async = 0
    async voor av in gen_async_nl():
        totaal_async = totaal_async + av
    retourneer totaal_async

klasse ContextAsyncNl:
    async definieer __aenter__(self):
        retourneer 5
    async definieer __aexit__(self, exc_type, exc, tb):
        retourneer Onwaar

async definieer taak_async_met():
    async met ContextAsyncNl() zoals waarde:
        retourneer waarde

laat uitkomst_async = asyncio.run(verdubbel_async(5))
laat uitkomst_async_voor = asyncio.run(taak_async_voor())
laat uitkomst_async_met = asyncio.run(taak_async_met())

afdrukken(bau_bits, macht_aug)
afdrukken(byte_len)
afdrukken(samengev, tekstr_idx, tekstr_seg)
afdrukken(elem_tupel_nl, iter_som)
afdrukken(dubbele_lijst)
afdrukken(result_tekstr_m, result_geen, result_num_m, result_tupel_m)
afdrukken(uitkomst_async, uitkomst_async_voor, uitkomst_async_met)
