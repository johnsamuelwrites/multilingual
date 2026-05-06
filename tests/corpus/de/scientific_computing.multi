# Wissenschaftliches Rechnen - Projekt WASM Corpus
# Deutsche Variante
#
# Demonstriert:
# - Monte-Carlo-Simulationen
# - Numerische Näherungen
# - Statistische Berechnungen
# - Gleitkommaintensive Operationen ideal für WASM

# SPDX-License-Identifier: GPL-3.0-or-later

Funktion zufallsfließkommazahl(saat: ganze_zahl) -> zahl:
    """Einfacher Pseudo-Zufallszahlengenerator."""
    # Linearer Kongruenzgenerator
    a = 1103515245
    c = 12345
    m = 2147483648  # 2^31
    saat = (a * saat + c) % m
    zurückgeben (saat / m)


Funktion pi_monte_carlo_schätzen(num_stichproben: ganze_zahl) -> zahl:
    """PI mit Monte-Carlo-Methode schätzen.

    Zufallspunkte im Quadrat [0,1] x [0,1] generieren.
    Zählen, wie viele im Einheitskreis (x^2 + y^2 <= 1) liegen.
    Verhältnis der Punkte im Kreis zum Total approximiert PI/4.
    """
    im_kreis = 0
    saat = 42  # Feste Saat für Reproduzierbarkeit

    für i in bereich(num_stichproben):
        # Zufallspunkt generieren
        saat = (1103515245 * saat + 12345) % 2147483648
        x = (saat % 10000) / 10000.0

        saat = (1103515245 * saat + 12345) % 2147483648
        y = (saat % 10000) / 10000.0

        # Prüfe, ob Punkt im Einheitskreis liegt
        abstand_quadrat = x * x + y * y
        falls abstand_quadrat <= 1.0:
            im_kreis = im_kreis + 1

    # PI schätzen
    pi_schätzung = 4.0 * im_kreis / num_stichproben
    zurückgeben pi_schätzung


Funktion standardabweichung(werte: liste) -> zahl:
    """Standardabweichung einer Liste von Werten berechnen."""
    falls länge(werte) ist 0:
        zurückgeben 0.0

    # Mittelwert berechnen
    mittelwert = 0.0
    für wert in werte:
        mittelwert = mittelwert + wert
    mittelwert = mittelwert / länge(werte)

    # Varianz berechnen
    varianz = 0.0
    für wert in werte:
        differenz = wert - mittelwert
        varianz = varianz + (differenz * differenz)
    varianz = varianz / länge(werte)

    # Standardabweichung ist Quadratwurzel der Varianz
    zurückgeben varianz ** 0.5


Funktion statistiken_berechnen(werte: liste) -> objekt:
    """Verschiedene Statistiken für einen Datensatz berechnen."""
    falls länge(werte) ist 0:
        zurückgeben {"mittelwert": 0, "stdabw": 0, "min": 0, "max": 0}

    # Mittelwert
    mittelwert = 0.0
    für wert in werte:
        mittelwert = mittelwert + wert
    mittelwert = mittelwert / länge(werte)

    # Min und max
    min_wert = werte[0]
    max_wert = werte[0]
    für wert in werte:
        falls wert < min_wert:
            min_wert = wert
        falls wert > max_wert:
            max_wert = wert

    # Standardabweichung
    stdabw = standardabweichung(werte)

    zurückgeben {
        "mittelwert": mittelwert,
        "stdabw": stdabw,
        "min": min_wert,
        "max": max_wert,
        "anzahl": länge(werte),
    }


Funktion primzahlanzahl_schätzen(n: ganze_zahl) -> zahl:
    """Anzahl der Primzahlen <= n mit dem Primzahlsatz schätzen."""
    # Primzahlsatz: π(n) ≈ n / ln(n)
    falls n <= 1:
        zurückgeben 0.0
    falls n < 10:
        zurückgeben zahl(n)

    ln_n = 0.0
    # Einfache Logarithmus-Approximation
    temp = n
    für _ in bereich(10):
        ln_n = ln_n + 1.0 / temp
        temp = temp / 2.718  # Grobe Approximation

    zurückgeben n / ln_n


Funktion fakultät_schätzen(n: ganze_zahl) -> zahl:
    """n! mit Stirlings Approximation schätzen."""
    falls n <= 0:
        zurückgeben 1.0
    falls n ist 1:
        zurückgeben 1.0

    # Stirling: n! ≈ sqrt(2πn) * (n/e)^n
    # Vereinfacht: ln(n!) ≈ n*ln(n) - n
    ln_fakultät = 0.0
    für i in bereich(1, n + 1):
        ln_fakultät = ln_fakultät + (i)  # Sehr vereinfacht

    zurückgeben ln_fakultät ** 1.5


Funktion hauptfunktion():
    ausgabe("=== Wissenschaftliches Rechnen-Demonstration ===")

    # PI schätzen
    ausgabe("\n1. PI-Schätzung mit Monte-Carlo-Methode...")
    stichprobenliste = [1000, 10000, 100000]

    für stichproben in stichprobenliste:
        pi_schätz = pi_monte_carlo_schätzen(stichproben)
        fehler = abs(pi_schätz - 3.14159265359)
        ausgabe(f"   Stichproben: {stichproben:6d}, PI-Schätzung: {pi_schätz:.6f}, Fehler: {fehler:.6f}")

    # Statistische Berechnungen
    ausgabe("\n2. Statistische Analyse...")
    testdaten = [1.5, 2.3, 3.1, 2.8, 4.5, 3.2, 2.9, 5.1, 3.8, 4.2]
    stats = statistiken_berechnen(testdaten)
    ausgabe(f"   Mittelwert: {stats['mittelwert']:.4f}")
    ausgabe(f"   Std.abw.: {stats['stdabw']:.4f}")
    ausgabe(f"   Min: {stats['min']:.4f}")
    ausgabe(f"   Max: {stats['max']:.4f}")
    ausgabe(f"   Anzahl: {stats['anzahl']}")

    # Primzahl-Approximation
    ausgabe("\n3. Primzahlsatz-Approximation...")
    primes_testwerte = [10, 100, 1000]
    für n in primes_testwerte:
        primes_approx = primzahlanzahl_schätzen(n)
        ausgabe(f"   Geschätzte Primzahlen <= {n}: {zahl(primes_approx):.1f}")

    # Fakultäts-Approximation
    ausgabe("\n4. Fakultäts-Approximation (Stirling)...")
    fakultät_testwerte = [5, 10, 20, 50]
    für n in fakultät_testwerte:
        fak_approx = fakultät_schätzen(n)
        ausgabe(f"   Fakultät {n}! ≈ {fak_approx:.2f}")

    # Belastungstest: viele Simulationen
    ausgabe("\n5. Belastungstest: mehrere PI-Schätzungen...")
    pi_schätzungen = []
    für versuch in bereich(10):
        pi_schätz = pi_monte_carlo_schätzen(100000)
        pi_schätzungen.hinzufügen(pi_schätz)

    pi_stats = statistiken_berechnen(pi_schätzungen)
    ausgabe(f"   Mittlere PI-Schätzung: {pi_stats['mittelwert']:.6f}")
    ausgabe(f"   Std.abw.: {pi_stats['stdabw']:.6f}")
    ausgabe(f"   Bereich: [{pi_stats['min']:.6f}, {pi_stats['max']:.6f}]")

    # Numerische Integration (Trapezregel)
    ausgabe("\n6. Numerische Integration (einfaches Beispiel)...")
    # Integriere y=x^2 von 0 bis 1, sollte 1/3 ≈ 0.333 sein
    intervalle = 100
    summe = 0.0
    für i in bereich(intervalle):
        x1 = i / zahl(intervalle)
        x2 = (i + 1) / zahl(intervalle)
        y1 = x1 * x1
        y2 = x2 * x2
        trapezfläche = (y1 + y2) / 2.0 * (x2 - x1)
        summe = summe + trapezfläche

    ausgabe(f"   Integral von x^2 von 0 bis 1: {summe:.6f} (erwartet: 0.333333)")

    ausgabe("\n✓ Alle wissenschaftlichen Rechnen-Operationen erfolgreich abgeschlossen")


hauptfunktion()
