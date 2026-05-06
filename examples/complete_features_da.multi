importer math
fra math importer sqrt som root_fn
importer asyncio

lad delt_taeller = 3

definer oeg_global():
    global delt_taeller
    delt_taeller = delt_taeller + 2
    returner delt_taeller

definer opret_taeller(startvaerdi):
    lad total = startvaerdi
    definer skridt():
        ikke_lokal total
        total = total + 1
        returner total
    returner skridt

lad naeste_taeller = opret_taeller(5)
lad foerste_skridt = naeste_taeller()
lad anden_skridt = naeste_taeller()

med aabn("tmp_complete_en.txt", "w", encoding="utf-8") som fil_skriv:
    fil_skriv.write("ok")

lad fil_tekst = ""
med aabn("tmp_complete_en.txt", "r", encoding="utf-8") som fil_laes:
    fil_tekst = fil_laes.read()

lad sammenkoblede_par = liste(zip([1, 2, 3], [4, 5, 6]))
lad unikke_vaerdier = maengde([1, 1, 2, 3])
lad faste_vaerdier = tupel([10, 20, 30])
lad foerste_element, *mellem_elementer, sidste_element = [1, 2, 3, 4]
lad kombineret_kort = {**{"x": 1}, **{"y": 2}}

definer formater_maerke(a, /, *, b):
    returner f"{a}-{b:.1f}"

lad maerke_formateret = formater_maerke(7, b=3.5)
lad froe = 0
lad snevaerde = (froe := froe + 9)

klasse TaellerBoks:
    definer __init__(self, startbasis):
        self.vaerdi = startbasis

klasse TaellerBoksBarn(TaellerBoks):
    definer __init__(self, startbasis):
        superklasse(TaellerBoksBarn, self).__init__(startbasis)
        self.vaerdi = self.vaerdi + 1

definer producer_tre():
    for indeks i interval(3):
        giv indeks

lad produceret_total = summering(producer_tre())
lad behandlet = Falsk

prov:
    hvis laengde(unikke_vaerdier) > 2:
        kast ValueError("boom")
undtagen ValueError som haandteret_fejl:
    behandlet = Sand
endelig:
    lad kvadratrod_vaerdi = heltal(root_fn(16))

lad midlertidig_vaerdi = 99
slet midlertidig_vaerdi

lad slyfe_akkum = 0
for n i interval(6):
    hvis n == 0:
        pass
    hvis n == 4:
        afbryd
    hvis n % 2 == 0:
        fortsaet
    slyfe_akkum = slyfe_akkum + n

lad flag_ok = Sand og ikke Falsk
haevd flag_ok

lad boern_boks = TaellerBoksBarn(40)

skriv(oeg_global())
skriv(foerste_skridt, anden_skridt)
skriv(fil_tekst)
skriv(laengde(sammenkoblede_par), laengde(unikke_vaerdier), faste_vaerdier[1])
skriv(foerste_element, mellem_elementer, sidste_element)
skriv(boern_boks.vaerdi)
skriv(produceret_total, kvadratrod_vaerdi, behandlet)
skriv(kombineret_kort["x"] + kombineret_kort["y"], maerke_formateret, snevaerde)
skriv(slyfe_akkum)
skriv(delt_taeller er Ingen)

# Loop else clauses
lad elementer_fundet = Falsk
for element i interval(3):
    hvis element == 10:
        elementer_fundet = Sand
        afbryd
ellers:
    elementer_fundet = "not_found"

lad mens_ellers_val = 0
mens mens_ellers_val < 2:
    mens_ellers_val = mens_ellers_val + 1
ellers:
    mens_ellers_val = mens_ellers_val + 10

# Starred unpacking variations
lad a, *rest = [10, 20, 30, 40]
lad *init, b = [10, 20, 30, 40]
lad c, *midten, d = [10, 20, 30, 40]

# Set comprehension
lad kvadreret_maengde = {x * x for x i interval(5)}

# Extended builtins
lad potens_resultat = potens(2, 8)
lad divmod_resultat = divmod(17, 5)

# Yield from generator
definer delegerende_gen():
    giv fra interval(3)

lad delegeret = liste(delegerende_gen())

skriv(elementer_fundet, mens_ellers_val)
skriv(a, rest, init, b, c, midten, d)
skriv(sorteret(kvadreret_maengde))
skriv(potens_resultat, divmod_resultat)
skriv(delegeret)

# Numeric literals
lad hex_tal = 0xFF
lad okt_tal = 0o17
lad bin_tal = 0b1010
lad sci_tal = 1.5e3

# Augmented assignments
lad foroget = 10
foroget += 5
foroget -= 2
foroget *= 3
foroget //= 4
foroget %= 3

# Bitwise operators
lad bit_og = 0b1010 & 0b1100
lad bit_eller = 0b1010 | 0b0101
lad bit_xor = 0b1010 ^ 0b1111
lad bit_venstre = 1 << 3
lad bit_hojre = 64 >> 2

# Chained assignment
lad kaede_a = kaede_b = kaede_c = 0

# Type annotations
lad typet: heltal = 99

definer annoteret(x: heltal, y: flydetal) -> streng:
    returner streng(x + y)

# Ternary expression
lad ternar = "yes" hvis typet > 0 ellers "no"

# Default params, *args, **kwargs
definer flere_parametre(base, extra=1, *args, **kwargs):
    returner base + extra + summering(args)
lad flere_resultat = flere_parametre(10, 2, 3, 4, key=5)

# Lambda
lad kvadrat = lambda x: x * x

# List/dict comprehensions and generator expression
lad liste_c = [x * 2 for x i interval(4)]
lad dict_c = {streng(k): k * k for k i interval(3)}
lad gen_c = liste(x + 1 for x i interval(3))
lad indlejret_c = [n + m for n i interval(2) for m i interval(2)]
lad filter_c = [x for x i interval(6) hvis x % 2 == 0]

# try/except/else
lad prov_ellers = 0
prov:
    prov_ellers = heltal("7")
undtagen ValueError:
    prov_ellers = -1
ellers:
    prov_ellers += 1

# Exception chaining
lad kaedet = Falsk
prov:
    prov:
        kast ValueError("v")
    undtagen ValueError som ve:
        kast RuntimeError("r") fra ve
undtagen RuntimeError:
    kaedet = Sand

# Multiple except handlers
lad flere_undtag = 0
prov:
    kast TypeError("t")
undtagen ValueError:
    flere_undtag = 1
undtagen TypeError:
    flere_undtag = 2

# Match/case with default
lad match_vaerdi = 2
lad match_resultat = "other"
match match_vaerdi:
    sag 1:
        match_resultat = "one"
    sag 2:
        match_resultat = "two"
    standard:
        match_resultat = "default"

# Decorator
definer fordobler(func):
    definer omslag(*args, **kwargs):
        returner func(*args, **kwargs) * 2
    returner omslag

@fordobler
definer ti():
    returner 10

lad deko_resultat = ti()

# Multiple inheritance, static/class methods, property
klasse Blanding:
    definer bland(self):
        returner 1

klasse BaseTo:
    definer __init__(self, start):
        self.value = start

klasse Kombineret(BaseTo, Blanding):
    @staticmethod
    definer etiket():
        returner "combined"
    @classmethod
    definer byg(cls, v):
        returner cls(v)
    @property
    definer fordoblet(self):
        returner self.value * 2

lad komb_obj = Kombineret.byg(3)
lad egenskab = komb_obj.fordoblet

# Docstring
definer med_doc():
    """A docstring."""
    returner Sand

skriv(hex_tal, okt_tal, bin_tal, sci_tal)
skriv(foroget, bit_og, bit_eller, bit_xor, bit_venstre, bit_hojre)
skriv(kaede_a, kaede_b, kaede_c)
skriv(typet, annoteret(3, 1.5), ternar)
skriv(flere_resultat, kvadrat(5))
skriv(liste_c, dict_c, gen_c)
skriv(indlejret_c, filter_c)
skriv(prov_ellers, kaedet, flere_undtag)
skriv(match_resultat, deko_resultat, egenskab)
skriv(med_doc())

# Bit-vise udvidede tildelinger og potens (v0.6.0)
lad bau_bits = 0b1111
bau_bits &= 0b1010
bau_bits |= 0b0100
bau_bits ^= 0b0011
bau_bits <<= 1
bau_bits >>= 2
lad pot_aug = 2
pot_aug **= 4

# Bytes-literal (v0.6.0)
lad byte_data = b"hello"
lad byte_laengde = laengde(byte_data)

# Streng sammenkædning, indeksering og udskæring (v0.6.0)
lad streng_x = "hello"
lad streng_y = " world"
lad sammenkat = streng_x + streng_y
lad streng_idx = streng_x[1]
lad streng_udskaer = streng_x[1:3]

# Tupel-literal (v0.6.0)
lad tupel_da = (10, 20, 30)
lad elem_tupel_da = tupel_da[1]

# For-løkke over listevariabel og listeforståelse (v0.6.0)
lad iter_liste = [10, 20, 30]
lad iter_sum = 0
for iter_val i iter_liste:
    iter_sum = iter_sum + iter_val

lad dobbelt_kilde = [1, 2, 3, 4]
lad dobbelt_liste = [v * 2 for v i dobbelt_kilde]

# Udvidet match: streng, Ingen, numerisk og tupel (v0.6.0)
lad streng_m = "hello"
lad result_streng_m = "ingen"
match streng_m:
    sag "hello":
        result_streng_m = "hi"
    sag "bye":
        result_streng_m = "goodbye"
    standard:
        result_streng_m = "unknown"

lad val_ingen = Ingen
lad result_ingen = "defineret"
match val_ingen:
    sag Ingen:
        result_ingen = "null"
    standard:
        result_ingen = "other"

lad val_num_m = 42
lad result_num_m = 0
match val_num_m:
    sag 42:
        result_num_m = val_num_m
    standard:
        result_num_m = 0

lad val_tupel_m = (1, 2)
lad result_tupel_m = "no"
match val_tupel_m:
    sag (1, 2):
        result_tupel_m = "yes"
    standard:
        result_tupel_m = "no"

# async def, await, async for, async with (v0.6.0)
async definer fordobl_async(n):
    afvent asyncio.sleep(0)
    returner n * 2

async definer gen_async_da():
    for v i range(3):
        giv v

async definer opgave_async_for():
    lad total_async = 0
    async for av i gen_async_da():
        total_async = total_async + av
    returner total_async

klasse KontekstAsyncDa:
    async definer __aenter__(self):
        returner 5
    async definer __aexit__(self, exc_type, exc, tb):
        returner Falsk

async definer opgave_async_med():
    async med KontekstAsyncDa() som vaerdi:
        returner vaerdi

lad resultat_async = asyncio.run(fordobl_async(5))
lad resultat_async_for = asyncio.run(opgave_async_for())
lad resultat_async_med = asyncio.run(opgave_async_med())

skriv(bau_bits, pot_aug)
skriv(byte_laengde)
skriv(sammenkat, streng_idx, streng_udskaer)
skriv(elem_tupel_da, iter_sum)
skriv(dobbelt_liste)
skriv(result_streng_m, result_ingen, result_num_m, result_tupel_m)
skriv(resultat_async, resultat_async_for, resultat_async_med)
