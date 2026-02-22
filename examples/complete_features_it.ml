importa math
da math importa sqrt come root_fn

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
