importuj math
zmodulu math importuj sqrt jako root_fn

niech licznik_globalny = 3

funkcja zwiekszaj_globalny():
    globalne licznik_globalny
    licznik_globalny = licznik_globalny + 2
    zwroc licznik_globalny

funkcja stworz_licznik(start):
    niech total = start
    funkcja krok():
        nielokalne total
        total = total + 1
        zwroc total
    zwroc krok

niech nastepny_licznik = stworz_licznik(5)
niech pierwszy_krok = nastepny_licznik()
niech drugi_krok = nastepny_licznik()

z otworz("tmp_complete_en.txt", "w", encoding="utf-8") jako uchwyt_zapis:
    uchwyt_zapis.write("ok")

niech tekst_pliku = ""
z otworz("tmp_complete_en.txt", "r", encoding="utf-8") jako uchwyt_odczyt:
    tekst_pliku = uchwyt_odczyt.read()

niech pary_polaczone = lista(polacz([1, 2, 3], [4, 5, 6]))
niech wartosci_unikalne = zbior([1, 1, 2, 3])
niech wartosci_stale = krotka([10, 20, 30])
niech pierwszy_element, *srodkowe_elementy, ostatni_element = [1, 2, 3, 4]
niech mapa_polaczona = {**{"x": 1}, **{"y": 2}}

funkcja formatuj_etykiete(a, /, *, b):
    zwroc f"{a}-{b:.1f}"

niech etykieta_sformatowana = formatuj_etykiete(7, b=3.5)
niech ziarno = 0
niech wartosc_wasy = (ziarno := ziarno + 9)

klasa PudelkoLicznika:
    funkcja __init__(self, baza_startowa):
        self.wartosc = baza_startowa

klasa PudelkoLicznikaPochodne(PudelkoLicznika):
    funkcja __init__(self, baza_startowa):
        nadklasa(PudelkoLicznikaPochodne, self).__init__(baza_startowa)
        self.wartosc = self.wartosc + 1

funkcja produkuj_trzy():
    dla indeks w zakres(3):
        zwroc_wartosc indeks

niech calkowita_produkowana = suma(produkuj_trzy())
niech obsluzony = Falsz

sprobuj:
    jesli dlugosc(wartosci_unikalne) > 2:
        podnies ValueError("boom")
wyjatek ValueError jako obsluzony_blad:
    obsluzony = Prawda
w_koncu:
    niech wartosc_pierwiastka = calkowita(root_fn(16))

niech wartosc_tymczasowa = 99
usun wartosc_tymczasowa

niech akumulacja_petli = 0
dla n w zakres(6):
    jesli n == 0:
        pomin
    jesli n == 4:
        przerwij
    jesli n % 2 == 0:
        kontynuuj
    akumulacja_petli = akumulacja_petli + n

niech flaga_ok = Prawda oraz nie Falsz
asercja flaga_ok

niech pudelko_pochodne = PudelkoLicznikaPochodne(40)

drukuj(zwiekszaj_globalny())
drukuj(pierwszy_krok, drugi_krok)
drukuj(tekst_pliku)
drukuj(dlugosc(pary_polaczone), dlugosc(wartosci_unikalne), wartosci_stale[1])
drukuj(pierwszy_element, srodkowe_elementy, ostatni_element)
drukuj(pudelko_pochodne.wartosc)
drukuj(calkowita_produkowana, wartosc_pierwiastka, obsluzony)
drukuj(mapa_polaczona["x"] + mapa_polaczona["y"], etykieta_sformatowana, wartosc_wasy)
drukuj(akumulacja_petli)
drukuj(licznik_globalny jest Brak)

# Loop else clauses
niech elementy_znalezione = Falsz
dla element w zakres(3):
    jesli element == 10:
        elementy_znalezione = Prawda
        przerwij
inaczej:
    elementy_znalezione = "not_found"

niech wartosc_dopoki_else = 0
dopoki wartosc_dopoki_else < 2:
    wartosc_dopoki_else = wartosc_dopoki_else + 1
inaczej:
    wartosc_dopoki_else = wartosc_dopoki_else + 10

# Starred unpacking variations
niech a, *reszta = [10, 20, 30, 40]
niech *init, b = [10, 20, 30, 40]
niech c, *srodek, d = [10, 20, 30, 40]

# Set comprehension
niech zbior_kwadratow = {x * x dla x w zakres(5)}

# Extended builtins
niech wynik_potegowania = potega(2, 8)
niech wynik_divmod = dzielmod(17, 5)

# Yield from generator
funkcja generator_delegujacy():
    zwroc_wartosc zmodulu zakres(3)

niech delegowany = lista(generator_delegujacy())

drukuj(elementy_znalezione, wartosc_dopoki_else)
drukuj(a, reszta, init, b, c, srodek, d)
drukuj(posortowane(zbior_kwadratow))
drukuj(wynik_potegowania, wynik_divmod)
drukuj(delegowany)
