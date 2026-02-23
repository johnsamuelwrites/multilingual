tuo math
kohteesta math tuo sqrt nimella root_fn

olkoon jaettu_laskuri = 3

maarittele kasvata_globaali():
    globaali jaettu_laskuri
    jaettu_laskuri = jaettu_laskuri + 2
    palauta jaettu_laskuri

maarittele luo_laskuri(alku):
    olkoon total = alku
    maarittele askel():
        epapaikallinen total
        total = total + 1
        palauta total
    palauta askel

olkoon seuraava_laskuri = luo_laskuri(5)
olkoon ensimmainen_askel = seuraava_laskuri()
olkoon toinen_askel = seuraava_laskuri()

kanssa avaa("tmp_complete_en.txt", "w", encoding="utf-8") nimella kirjoitus_kahva:
    kirjoitus_kahva.write("ok")

olkoon tiedosto_teksti = ""
kanssa avaa("tmp_complete_en.txt", "r", encoding="utf-8") nimella luku_kahva:
    tiedosto_teksti = luku_kahva.read()

olkoon yhdistetyt_parit = lista(parita([1, 2, 3], [4, 5, 6]))
olkoon ainutkertaiset_arvot = joukko([1, 1, 2, 3])
olkoon kiinteat_arvot = monikko([10, 20, 30])
olkoon ensimmainen_alkio, *keskimmaiset_alkiot, viimeinen_alkio = [1, 2, 3, 4]
olkoon yhdistetty_kartta = {**{"x": 1}, **{"y": 2}}

maarittele muotoile_tunniste(a, /, *, b):
    palauta f"{a}-{b:.1f}"

olkoon tunniste_muotoiltu = muotoile_tunniste(7, b=3.5)
olkoon siemen = 0
olkoon mursu_arvo = (siemen := siemen + 9)

luokka LaskuriLaatikko:
    maarittele __init__(self, alku_perusta):
        self.arvo = alku_perusta

luokka LaskuriLaatikkoLapsi(LaskuriLaatikko):
    maarittele __init__(self, alku_perusta):
        ylaluokka(LaskuriLaatikkoLapsi, self).__init__(alku_perusta)
        self.arvo = self.arvo + 1

maarittele tuota_kolme():
    jokaiselle indeksi sisalla vali(3):
        tuota indeksi

olkoon tuotettu_summa = summa(tuota_kolme())
olkoon kasitelty = Epatosi

yrita:
    jos pituus(ainutkertaiset_arvot) > 2:
        nosta ValueError("boom")
paitsi ValueError nimella kasitelty_virhe:
    kasitelty = Tosi
lopuksi:
    olkoon juuri_arvo = kokonaisluku(root_fn(16))

olkoon valiaikainen_arvo = 99
poista valiaikainen_arvo

olkoon silmukka_kertyma = 0
jokaiselle n sisalla vali(6):
    jos n == 0:
        ohita
    jos n == 4:
        keskeyta
    jos n % 2 == 0:
        jatka
    silmukka_kertyma = silmukka_kertyma + n

olkoon lippu_ok = Tosi ja ei Epatosi
varmista lippu_ok

olkoon lapsi_laatikko = LaskuriLaatikkoLapsi(40)

tulosta(kasvata_globaali())
tulosta(ensimmainen_askel, toinen_askel)
tulosta(tiedosto_teksti)
tulosta(pituus(yhdistetyt_parit), pituus(ainutkertaiset_arvot), kiinteat_arvot[1])
tulosta(ensimmainen_alkio, keskimmaiset_alkiot, viimeinen_alkio)
tulosta(lapsi_laatikko.arvo)
tulosta(tuotettu_summa, juuri_arvo, kasitelty)
tulosta(yhdistetty_kartta["x"] + yhdistetty_kartta["y"], tunniste_muotoiltu, mursu_arvo)
tulosta(silmukka_kertyma)
tulosta(jaettu_laskuri on EiMitaan)

# Loop else clauses
olkoon alkiot_loydetty = Epatosi
jokaiselle alkio sisalla vali(3):
    jos alkio == 10:
        alkiot_loydetty = Tosi
        keskeyta
muuten:
    alkiot_loydetty = "not_found"

olkoon kun_muuten_arvo = 0
kun kun_muuten_arvo < 2:
    kun_muuten_arvo = kun_muuten_arvo + 1
muuten:
    kun_muuten_arvo = kun_muuten_arvo + 10

# Starred unpacking variations
olkoon a, *jaljella = [10, 20, 30, 40]
olkoon *init, b = [10, 20, 30, 40]
olkoon c, *keskiosa, d = [10, 20, 30, 40]

# Set comprehension
olkoon neliot_jarjestelma = {x * x jokaiselle x sisalla vali(5)}

# Extended builtins
olkoon potenssi_tulos = potenssi(2, 8)
olkoon divmod_tulos = jakojaannos(17, 5)

# Yield from generator
maarittele delegoiva_gen():
    tuota kohteesta vali(3)

olkoon delegoitu = lista(delegoiva_gen())

tulosta(alkiot_loydetty, kun_muuten_arvo)
tulosta(a, jaljella, init, b, c, keskiosa, d)
tulosta(jarjestetty(neliot_jarjestelma))
tulosta(potenssi_tulos, divmod_tulos)
tulosta(delegoitu)

# Numeric literals
olkoon heks_luku = 0xFF
olkoon okta_luku = 0o17
olkoon bin_luku = 0b1010
olkoon sci_luku = 1.5e3

# Augmented assignments
olkoon kasvatettu = 10
kasvatettu += 5
kasvatettu -= 2
kasvatettu *= 3
kasvatettu //= 4
kasvatettu %= 3

# Bitwise operators
olkoon bitti_ja = 0b1010 & 0b1100
olkoon bitti_tai = 0b1010 | 0b0101
olkoon bitti_xor = 0b1010 ^ 0b1111
olkoon bitti_vasen = 1 << 3
olkoon bitti_oikea = 64 >> 2

# Chained assignment
olkoon ketju_a = ketju_b = ketju_c = 0

# Type annotations
olkoon tyypitetty: kokonaisluku = 99

maarittele annotoitu(x: kokonaisluku, y: liukuluku) -> merkkijono:
    palauta merkkijono(x + y)

# Ternary expression
olkoon kolmihaara = "yes" jos tyypitetty > 0 muuten "no"

# Default params, *args, **kwargs
maarittele usea_parametri(base, extra=1, *args, **kwargs):
    palauta base + extra + summa(args)
olkoon usea_tulos = usea_parametri(10, 2, 3, 4, key=5)

# Lambda
olkoon nelio = lambda x: x * x

# List/dict comprehensions and generator expression
olkoon lista_c = [x * 2 jokaiselle x sisalla vali(4)]
olkoon sanakirja_c = {merkkijono(k): k * k jokaiselle k sisalla vali(3)}
olkoon gen_c = lista(x + 1 jokaiselle x sisalla vali(3))
olkoon sisakkais_c = [i + j jokaiselle i sisalla vali(2) jokaiselle j sisalla vali(2)]
olkoon suodatin_c = [x jokaiselle x sisalla vali(6) jos x % 2 == 0]

# try/except/else
olkoon yrita_muuten = 0
yrita:
    yrita_muuten = kokonaisluku("7")
paitsi ValueError:
    yrita_muuten = -1
muuten:
    yrita_muuten += 1

# Exception chaining
olkoon ketjutettu = Epatosi
yrita:
    yrita:
        nosta ValueError("v")
    paitsi ValueError nimella ve:
        nosta RuntimeError("r") kohteesta ve
paitsi RuntimeError:
    ketjutettu = Tosi

# Multiple except handlers
olkoon moni_poikkeus = 0
yrita:
    nosta TypeError("t")
paitsi ValueError:
    moni_poikkeus = 1
paitsi TypeError:
    moni_poikkeus = 2

# Match/case with default
olkoon sovitus_arvo = 2
olkoon sovitus_tulos = "other"
taysmatch sovitus_arvo:
    tapaus 1:
        sovitus_tulos = "one"
    tapaus 2:
        sovitus_tulos = "two"
    oletus:
        sovitus_tulos = "default"

# Decorator
maarittele tuplaaja(func):
    maarittele kiedo(*args, **kwargs):
        palauta func(*args, **kwargs) * 2
    palauta kiedo

@tuplaaja
maarittele kymmenen():
    palauta 10

olkoon deko_tulos = kymmenen()

# Multiple inheritance, static/class methods, property
luokka Sekoitus:
    maarittele sekoita(self):
        palauta 1

luokka PerusKaksi:
    maarittele __init__(self, start):
        self.value = start

luokka Yhdistetty(PerusKaksi, Sekoitus):
    @staticmethod
    maarittele nimike():
        palauta "combined"
    @classmethod
    maarittele rakenna(cls, v):
        palauta cls(v)
    @property
    maarittele tuplattu(self):
        palauta self.value * 2

olkoon yhd_obj = Yhdistetty.rakenna(3)
olkoon ominaisuus = yhd_obj.tuplattu

# Docstring
maarittele doc_kanssa():
    """A docstring."""
    palauta Tosi

tulosta(heks_luku, okta_luku, bin_luku, sci_luku)
tulosta(kasvatettu, bitti_ja, bitti_tai, bitti_xor, bitti_vasen, bitti_oikea)
tulosta(ketju_a, ketju_b, ketju_c)
tulosta(tyypitetty, annotoitu(3, 1.5), kolmihaara)
tulosta(usea_tulos, nelio(5))
tulosta(lista_c, sanakirja_c, gen_c)
tulosta(sisakkais_c, suodatin_c)
tulosta(yrita_muuten, ketjutettu, moni_poikkeus)
tulosta(sovitus_tulos, deko_tulos, ominaisuus)
tulosta(doc_kanssa())
