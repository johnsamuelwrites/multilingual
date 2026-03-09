importera math
fran math importera sqrt som root_fn
importera asyncio

lat delad_rackare = 3

definiera okad_global():
    global delad_rackare
    delad_rackare = delad_rackare + 2
    retur delad_rackare

definiera skapa_rackare(start):
    lat total = start
    definiera steg():
        ickelokal total
        total = total + 1
        retur total
    retur steg

lat nasta_rackare = skapa_rackare(5)
lat forsta_steg = nasta_rackare()
lat andra_steg = nasta_rackare()

med oppna("tmp_complete_en.txt", "w", encoding="utf-8") som skriv_handtag:
    skriv_handtag.write("ok")

lat fil_text = ""
med oppna("tmp_complete_en.txt", "r", encoding="utf-8") som las_handtag:
    fil_text = las_handtag.read()

lat ihopkopplade_par = lista(para([1, 2, 3], [4, 5, 6]))
lat unika_varden = mangd([1, 1, 2, 3])
lat fasta_varden = tuppel([10, 20, 30])
lat forsta_element, *mellansta_element, sista_element = [1, 2, 3, 4]
lat sammanslaget_karta = {**{"x": 1}, **{"y": 2}}

definiera formatera_etikett(a, /, *, b):
    retur f"{a}-{b:.1f}"

lat etikett_formaterad = formatera_etikett(7, b=3.5)
lat fro = 0
lat snorsvarde = (fro := fro + 9)

klass RackareLada:
    definiera __init__(self, startbas):
        self.varde = startbas

klass RackareLadaBarn(RackareLada):
    definiera __init__(self, startbas):
        superklass(RackareLadaBarn, self).__init__(startbas)
        self.varde = self.varde + 1

definiera producera_tre():
    for index i intervall(3):
        ge index

lat producerad_summa = summa(producera_tre())
lat hanterad = Falskt

forsok:
    om langd(unika_varden) > 2:
        kasta ValueError("boom")
utom ValueError som hanterat_fel:
    hanterad = Sant
slutligen:
    lat rot_varde = heltal(root_fn(16))

lat tillfalligt_varde = 99
ta_bort tillfalligt_varde

lat loop_accum = 0
for n i intervall(6):
    om n == 0:
        passera
    om n == 4:
        bryt
    om n % 2 == 0:
        fortsatt
    loop_accum = loop_accum + n

lat flagga_ok = Sant och inte Falskt
pasta flagga_ok

lat barn_lada = RackareLadaBarn(40)

skriv(okad_global())
skriv(forsta_steg, andra_steg)
skriv(fil_text)
skriv(langd(ihopkopplade_par), langd(unika_varden), fasta_varden[1])
skriv(forsta_element, mellansta_element, sista_element)
skriv(barn_lada.varde)
skriv(producerad_summa, rot_varde, hanterad)
skriv(sammanslaget_karta["x"] + sammanslaget_karta["y"], etikett_formaterad, snorsvarde)
skriv(loop_accum)
skriv(delad_rackare ar Ingen)

# Loop else clauses
lat element_hittad = Falskt
for element i intervall(3):
    om element == 10:
        element_hittad = Sant
        bryt
annars:
    element_hittad = "not_found"

lat medan_annars_val = 0
medan medan_annars_val < 2:
    medan_annars_val = medan_annars_val + 1
annars:
    medan_annars_val = medan_annars_val + 10

# Starred unpacking variations
lat a, *rest = [10, 20, 30, 40]
lat *init, b = [10, 20, 30, 40]
lat c, *mellan, d = [10, 20, 30, 40]

# Set comprehension
lat kvadrerad_mangd = {x * x for x i intervall(5)}

# Extended builtins
lat potens_resultat = potens(2, 8)
lat divmod_resultat = divmod(17, 5)

# Yield from generator
definiera delegerande_gen():
    ge fran intervall(3)

lat delegerad = lista(delegerande_gen())

skriv(element_hittad, medan_annars_val)
skriv(a, rest, init, b, c, mellan, d)
skriv(sorterad(kvadrerad_mangd))
skriv(potens_resultat, divmod_resultat)
skriv(delegerad)

# Numeric literals
lat hex_tal = 0xFF
lat okt_tal = 0o17
lat bin_tal = 0b1010
lat sci_tal = 1.5e3

# Augmented assignments
lat okad = 10
okad += 5
okad -= 2
okad *= 3
okad //= 4
okad %= 3

# Bitwise operators
lat bit_och = 0b1010 & 0b1100
lat bit_eller = 0b1010 | 0b0101
lat bit_xor = 0b1010 ^ 0b1111
lat bit_vanster = 1 << 3
lat bit_hoger = 64 >> 2

# Chained assignment
lat kedja_a = kedja_b = kedja_c = 0

# Type annotations
lat typad: heltal = 99

definiera annoterad(x: heltal, y: flyttal) -> strang:
    retur strang(x + y)

# Ternary expression
lat ternar = "yes" om typad > 0 annars "no"

# Default params, *args, **kwargs
definiera flera_parametrar(base, extra=1, *args, **kwargs):
    retur base + extra + summa(args)
lat flera_resultat = flera_parametrar(10, 2, 3, 4, key=5)

# Lambda
lat kvadrat = lambda x: x * x

# List/dict comprehensions and generator expression
lat lista_c = [x * 2 for x i intervall(4)]
lat dict_c = {strang(k): k * k for k i intervall(3)}
lat gen_c = lista(x + 1 for x i intervall(3))
lat nastlad_c = [n + m for n i intervall(2) for m i intervall(2)]
lat filter_c = [x for x i intervall(6) om x % 2 == 0]

# try/except/else
lat prova_annars = 0
forsok:
    prova_annars = heltal("7")
utom ValueError:
    prova_annars = -1
annars:
    prova_annars += 1

# Exception chaining
lat kedjad = Falskt
forsok:
    forsok:
        kasta ValueError("v")
    utom ValueError som ve:
        kasta RuntimeError("r") fran ve
utom RuntimeError:
    kedjad = Sant

# Multiple except handlers
lat flera_undantag = 0
forsok:
    kasta TypeError("t")
utom ValueError:
    flera_undantag = 1
utom TypeError:
    flera_undantag = 2

# Match/case with default
lat match_varde = 2
lat match_resultat = "other"
matcha match_varde:
    fall 1:
        match_resultat = "one"
    fall 2:
        match_resultat = "two"
    standard:
        match_resultat = "default"

# Decorator
definiera fordubblare(func):
    definiera omslag(*args, **kwargs):
        retur func(*args, **kwargs) * 2
    retur omslag

@fordubblare
definiera tio():
    retur 10

lat deko_resultat = tio()

# Multiple inheritance, static/class methods, property
klass Blandning:
    definiera blanda(self):
        retur 1

klass BasTva:
    definiera __init__(self, start):
        self.value = start

klass Kombinerad(BasTva, Blandning):
    @staticmethod
    definiera etikett():
        retur "combined"
    @classmethod
    definiera bygg(cls, v):
        retur cls(v)
    @property
    definiera dubblad(self):
        retur self.value * 2

lat komb_obj = Kombinerad.bygg(3)
lat egenskap = komb_obj.dubblad

# Docstring
definiera med_doc():
    """A docstring."""
    retur Sant

skriv(hex_tal, okt_tal, bin_tal, sci_tal)
skriv(okad, bit_och, bit_eller, bit_xor, bit_vanster, bit_hoger)
skriv(kedja_a, kedja_b, kedja_c)
skriv(typad, annoterad(3, 1.5), ternar)
skriv(flera_resultat, kvadrat(5))
skriv(lista_c, dict_c, gen_c)
skriv(nastlad_c, filter_c)
skriv(prova_annars, kedjad, flera_undantag)
skriv(match_resultat, deko_resultat, egenskap)
skriv(med_doc())

# Bit-visa utökade tilldelningar och potens (v0.6.0)
lat bau_bits = 0b1111
bau_bits &= 0b1010
bau_bits |= 0b0100
bau_bits ^= 0b0011
bau_bits <<= 1
bau_bits >>= 2
lat pot_aug = 2
pot_aug **= 4

# Bytes-literal (v0.6.0)
lat byte_data = b"hello"
lat byte_langd = langd(byte_data)

# Strängkonkatenering, indexering och skärning (v0.6.0)
lat strang_x = "hello"
lat strang_y = " world"
lat konkatenerad = strang_x + strang_y
lat strang_idx = strang_x[1]
lat strang_skar = strang_x[1:3]

# Tuppel-literal (v0.6.0)
lat tuppel_sv = (10, 20, 30)
lat elem_tuppel_sv = tuppel_sv[1]

# For-slinga över listvariabel och listförståelse (v0.6.0)
lat iter_lista = [10, 20, 30]
lat iter_summa = 0
for iter_val i iter_lista:
    iter_summa = iter_summa + iter_val

lat dubbel_kalla = [1, 2, 3, 4]
lat dubblad_lista = [v * 2 for v i dubbel_kalla]

# Utökad matchning: sträng, Ingen, numerisk och tuppel (v0.6.0)
lat strang_m = "hello"
lat result_strang_m = "ingen"
matcha strang_m:
    fall "hello":
        result_strang_m = "hi"
    fall "bye":
        result_strang_m = "goodbye"
    standard:
        result_strang_m = "unknown"

lat val_ingen = Ingen
lat result_ingen = "definierad"
matcha val_ingen:
    fall Ingen:
        result_ingen = "null"
    standard:
        result_ingen = "other"

lat val_num_m = 42
lat result_num_m = 0
matcha val_num_m:
    fall 42:
        result_num_m = val_num_m
    standard:
        result_num_m = 0

lat val_tuppel_m = (1, 2)
lat result_tuppel_m = "no"
matcha val_tuppel_m:
    fall (1, 2):
        result_tuppel_m = "yes"
    standard:
        result_tuppel_m = "no"

# async def, await, async for, async with (v0.6.0)
async definiera dubbla_async(n):
    invanta asyncio.sleep(0)
    retur n * 2

async definiera gen_async_sv():
    for v i range(3):
        ge v

async definiera uppgift_async_for():
    lat totalt_async = 0
    async for av i gen_async_sv():
        totalt_async = totalt_async + av
    retur totalt_async

klass KontextAsyncSv:
    async definiera __aenter__(self):
        retur 5
    async definiera __aexit__(self, exc_type, exc, tb):
        retur Falskt

async definiera uppgift_async_med():
    async med KontextAsyncSv() som varde:
        retur varde

lat resultat_async = asyncio.run(dubbla_async(5))
lat resultat_async_for = asyncio.run(uppgift_async_for())
lat resultat_async_med = asyncio.run(uppgift_async_med())

skriv(bau_bits, pot_aug)
skriv(byte_langd)
skriv(konkatenerad, strang_idx, strang_skar)
skriv(elem_tuppel_sv, iter_summa)
skriv(dubblad_lista)
skriv(result_strang_m, result_ingen, result_num_m, result_tuppel_m)
skriv(resultat_async, resultat_async_for, resultat_async_med)
