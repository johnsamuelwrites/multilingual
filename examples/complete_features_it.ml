importa math
da math importa sqrt come root_fn
importa asyncio

sia contatore_condiviso = 3

definisci incrementa_globale():
    globale contatore_condiviso
    contatore_condiviso = contatore_condiviso + 2
    ritorna contatore_condiviso

definisci crea_contatore(inizio):
    sia total = inizio
    definisci passo():
        nonlocale total
        total = total + 1
        ritorna total
    ritorna passo

sia prossimo_contatore = crea_contatore(5)
sia primo_passo = prossimo_contatore()
sia secondo_passo = prossimo_contatore()

con apri("tmp_complete_en.txt", "w", encoding="utf-8") come maniglia_scrittura:
    maniglia_scrittura.write("ok")

sia testo_file = ""
con apri("tmp_complete_en.txt", "r", encoding="utf-8") come maniglia_lettura:
    testo_file = maniglia_lettura.read()

sia coppie_unite = lista(accoppia([1, 2, 3], [4, 5, 6]))
sia valori_unici = insieme([1, 1, 2, 3])
sia valori_fissi = tupla([10, 20, 30])
sia primo_elemento, *elementi_medi, ultimo_elemento = [1, 2, 3, 4]
sia mappa_unita = {**{"x": 1}, **{"y": 2}}

definisci formatta_etichetta(a, /, *, b):
    ritorna f"{a}-{b:.1f}"

sia etichetta_formattata = formatta_etichetta(7, b=3.5)
sia seme = 0
sia valore_morsa = (seme := seme + 9)

classe ScatolaContatore:
    definisci __init__(self, base_iniziale):
        self.valore = base_iniziale

classe ScatolaContatoreFiglia(ScatolaContatore):
    definisci __init__(self, base_iniziale):
        superclasse(ScatolaContatoreFiglia, self).__init__(base_iniziale)
        self.valore = self.valore + 1

definisci produci_tre():
    per indice in intervallo(3):
        produci indice

sia totale_prodotto = somma(produci_tre())
sia gestito = Falso

prova:
    se lunghezza(valori_unici) > 2:
        solleva ValueError("boom")
eccetto ValueError come errore_gestito:
    gestito = Vero
infine:
    sia valore_radice = intero(root_fn(16))

sia valore_temporaneo = 99
elimina valore_temporaneo

sia accumulo_ciclo = 0
per n in intervallo(6):
    se n == 0:
        passa
    se n == 4:
        interrompi
    se n % 2 == 0:
        continua
    accumulo_ciclo = accumulo_ciclo + n

sia flag_ok = Vero e non Falso
asserisci flag_ok

sia scatola_figlia = ScatolaContatoreFiglia(40)

stampa(incrementa_globale())
stampa(primo_passo, secondo_passo)
stampa(testo_file)
stampa(lunghezza(coppie_unite), lunghezza(valori_unici), valori_fissi[1])
stampa(primo_elemento, elementi_medi, ultimo_elemento)
stampa(scatola_figlia.valore)
stampa(totale_prodotto, valore_radice, gestito)
stampa(mappa_unita["x"] + mappa_unita["y"], etichetta_formattata, valore_morsa)
stampa(accumulo_ciclo)
stampa(contatore_condiviso è Nessuno)

# Loop else clauses
sia elementi_trovati = Falso
per elemento in intervallo(3):
    se elemento == 10:
        elementi_trovati = Vero
        interrompi
altrimenti:
    elementi_trovati = "not_found"

sia valore_mentre_altrimenti = 0
mentre valore_mentre_altrimenti < 2:
    valore_mentre_altrimenti = valore_mentre_altrimenti + 1
altrimenti:
    valore_mentre_altrimenti = valore_mentre_altrimenti + 10

# Starred unpacking variations
sia a, *resto = [10, 20, 30, 40]
sia *init, b = [10, 20, 30, 40]
sia c, *mezzo, d = [10, 20, 30, 40]

# Set comprehension
sia insieme_quadrati = {x * x per x in intervallo(5)}

# Extended builtins
sia risultato_potenza = potenza(2, 8)
sia risultato_divmod = divmod(17, 5)

# Yield from generator
definisci gen_delegante():
    produci da intervallo(3)

sia delegato = lista(gen_delegante())

stampa(elementi_trovati, valore_mentre_altrimenti)
stampa(a, resto, init, b, c, mezzo, d)
stampa(ordinato(insieme_quadrati))
stampa(risultato_potenza, risultato_divmod)
stampa(delegato)

# Numeric literals
sia num_esadec = 0xFF
sia num_ott = 0o17
sia num_bin = 0b1010
sia num_sci = 1.5e3

# Augmented assignments
sia aumentato = 10
aumentato += 5
aumentato -= 2
aumentato *= 3
aumentato //= 4
aumentato %= 3

# Bitwise operators
sia bit_e = 0b1010 & 0b1100
sia bit_o = 0b1010 | 0b0101
sia bit_xor = 0b1010 ^ 0b1111
sia bit_sx = 1 << 3
sia bit_dx = 64 >> 2

# Chained assignment
sia catena_a = catena_b = catena_c = 0

# Type annotations
sia tipizzato: intero = 99

definisci annotato(x: intero, y: decimale) -> stringa:
    ritorna stringa(x + y)

# Ternary expression
sia ternario = "yes" se tipizzato > 0 altrimenti "no"

# Default params, *args, **kwargs
definisci multi_parametri(base, extra=1, *args, **kwargs):
    ritorna base + extra + somma(args)
sia risultato_multi = multi_parametri(10, 2, 3, 4, key=5)

# Lambda
sia quadrato = lambda x: x * x

# List/dict comprehensions and generator expression
sia lista_c = [x * 2 per x in intervallo(4)]
sia diz_c = {stringa(k): k * k per k in intervallo(3)}
sia gen_c = lista(x + 1 per x in intervallo(3))
sia annidato_c = [i + j per i in intervallo(2) per j in intervallo(2)]
sia filtro_c = [x per x in intervallo(6) se x % 2 == 0]

# try/except/else
sia prova_altrimenti = 0
prova:
    prova_altrimenti = intero("7")
eccetto ValueError:
    prova_altrimenti = -1
altrimenti:
    prova_altrimenti += 1

# Exception chaining
sia concatenato = Falso
prova:
    prova:
        solleva ValueError("v")
    eccetto ValueError come ve:
        solleva RuntimeError("r") da ve
eccetto RuntimeError:
    concatenato = Vero

# Multiple except handlers
sia multi_eccezione = 0
prova:
    solleva TypeError("t")
eccetto ValueError:
    multi_eccezione = 1
eccetto TypeError:
    multi_eccezione = 2

# Match/case with default
sia valore_match = 2
sia risultato_match = "other"
confronta valore_match:
    caso 1:
        risultato_match = "one"
    caso 2:
        risultato_match = "two"
    predefinito:
        risultato_match = "default"

# Decorator
definisci raddoppiatore(func):
    definisci involucro(*args, **kwargs):
        ritorna func(*args, **kwargs) * 2
    ritorna involucro

@raddoppiatore
definisci dieci():
    ritorna 10

sia risultato_deco = dieci()

# Multiple inheritance, static/class methods, property
classe Misto:
    definisci misto(self):
        ritorna 1

classe BaseDue:
    definisci __init__(self, start):
        self.value = start

classe Combinato(BaseDue, Misto):
    @staticmethod
    definisci etichetta():
        ritorna "combined"
    @classmethod
    definisci costruisci(cls, v):
        ritorna cls(v)
    @property
    definisci raddoppiato(self):
        ritorna self.value * 2

sia combinato_obj = Combinato.costruisci(3)
sia proprieta = combinato_obj.raddoppiato

# Docstring
definisci con_doc():
    """A docstring."""
    ritorna Vero

stampa(num_esadec, num_ott, num_bin, num_sci)
stampa(aumentato, bit_e, bit_o, bit_xor, bit_sx, bit_dx)
stampa(catena_a, catena_b, catena_c)
stampa(tipizzato, annotato(3, 1.5), ternario)
stampa(risultato_multi, quadrato(5))
stampa(lista_c, diz_c, gen_c)
stampa(annidato_c, filtro_c)
stampa(prova_altrimenti, concatenato, multi_eccezione)
stampa(risultato_match, risultato_deco, proprieta)
stampa(con_doc())

# Assegnazioni aumentate bit a bit e potenza (v0.6.0)
sia bau_bits = 0b1111
bau_bits &= 0b1010
bau_bits |= 0b0100
bau_bits ^= 0b0011
bau_bits <<= 1
bau_bits >>= 2
sia pot_aug = 2
pot_aug **= 4

# Letterale di bytes (v0.6.0)
sia dati_bytes = b"ciao"
sia lung_bytes = lunghezza(dati_bytes)

# Concatenazione, indicizzazione e slice di stringa (v0.6.0)
sia stringa_x = "ciao"
sia stringa_y = " mondo"
sia concat_stringa = stringa_x + stringa_y
sia idx_stringa = stringa_x[1]
sia slice_stringa = stringa_x[1:3]

# Letterale di tupla (v0.6.0)
sia tupla_it = (10, 20, 30)
sia elem_tupla_it = tupla_it[1]

# Ciclo for su variabile lista e comprensione (v0.6.0)
sia lista_iter = [10, 20, 30]
sia somma_iter = 0
per val_iter in lista_iter:
    somma_iter = somma_iter + val_iter

sia lista_dop_src = [1, 2, 3, 4]
sia lista_doppia = [v * 2 per v in lista_dop_src]

# Corrispondenza estesa: stringa, Nessuno, numerico, tupla (v0.6.0)
sia stringa_m = "ciao"
sia result_stringa_m = "nessuno"
confronta stringa_m:
    caso "ciao":
        result_stringa_m = "salve"
    caso "arrivederci":
        result_stringa_m = "addio"
    predefinito:
        result_stringa_m = "sconosciuto"

sia val_nessuno = Nessuno
sia result_nessuno = "definito"
confronta val_nessuno:
    caso Nessuno:
        result_nessuno = "vuoto"
    predefinito:
        result_nessuno = "altro"

sia val_num_m = 42
sia result_num_m = 0
confronta val_num_m:
    caso 42:
        result_num_m = val_num_m
    predefinito:
        result_num_m = 0

sia val_tupla_m = (1, 2)
sia result_tupla_m = "no"
confronta val_tupla_m:
    caso (1, 2):
        result_tupla_m = "si"
    predefinito:
        result_tupla_m = "no"

# async def, await, async for, async with (v0.6.0)
asincrono definisci raddoppia_async(n):
    attendi asyncio.sleep(0)
    ritorna n * 2

asincrono definisci gen_async_it():
    per v in range(3):
        produci v

asincrono definisci compito_async_per():
    sia totale_async = 0
    asincrono per av in gen_async_it():
        totale_async = totale_async + av
    ritorna totale_async

classe ContestoAsyncIt:
    asincrono definisci __aenter__(self):
        ritorna 5
    asincrono definisci __aexit__(self, exc_type, exc, tb):
        ritorna Falso

asincrono definisci compito_async_con():
    asincrono con ContestoAsyncIt() come valore:
        ritorna valore

sia risultato_async = asyncio.run(raddoppia_async(5))
sia risultato_async_per = asyncio.run(compito_async_per())
sia risultato_async_con = asyncio.run(compito_async_con())

stampa(bau_bits, pot_aug)
stampa(lung_bytes)
stampa(concat_stringa, idx_stringa, slice_stringa)
stampa(elem_tupla_it, somma_iter)
stampa(lista_doppia)
stampa(result_stringa_m, result_nessuno, result_num_m, result_tupla_m)
stampa(risultato_async, risultato_async_per, risultato_async_con)
