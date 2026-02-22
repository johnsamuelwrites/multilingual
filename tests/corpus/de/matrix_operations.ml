# Matrixoperationen - Projekt WASM Corpus
# Deutsche Variante
#
# Demonstriert:
# - Matrizenmultiplikation (rechenintensiv, Stärke von WASM)
# - Matrixtransposition
# - Determinantenberechnung
# - Leistungsempfindliche Operationen

# SPDX-License-Identifier: GPL-3.0-or-later

Funktion erstelle_einheitsmatrix(n: ganze_zahl) -> liste:
    """Erstelle eine n×n Einheitsmatrix."""
    ergebnis = []
    für i in bereich(n):
        zeile = []
        für j in bereich(n):
            falls i ist j:
                zeile.hinzufügen(1)
            sonst:
                zeile.hinzufügen(0)
        ergebnis.hinzufügen(zeile)
    zurückgeben ergebnis


Funktion erstelle_testmatrix(n: ganze_zahl) -> liste:
    """Erstelle eine n×n Matrix mit sequenziellen Werten."""
    ergebnis = []
    zähler = 1
    für i in bereich(n):
        zeile = []
        für j in bereich(n):
            zeile.hinzufügen(zähler)
            zähler = zähler + 1
        ergebnis.hinzufügen(zeile)
    zurückgeben ergebnis


Funktion multipliziere_matrizen(a: liste, b: liste) -> liste:
    """Zwei Matrizen multiplizieren.

    Argumente:
        a: m×n Matrix (Liste von Listen)
        b: n×p Matrix (Liste von Listen)

    Zurückgeben:
        m×p Ergebnismatrix
    """
    m = länge(a)
    n = länge(a[0])
    p = länge(b[0])

    ergebnis = []
    für i in bereich(m):
        zeile = []
        für j in bereich(p):
            summe = 0
            für k in bereich(n):
                summe = summe + (a[i][k] * b[k][j])
            zeile.hinzufügen(summe)
        ergebnis.hinzufügen(zeile)

    zurückgeben ergebnis


Funktion transponiere_matrix(matrix: liste) -> liste:
    """Eine Matrix transponieren (Zeilen und Spalten tauschen)."""
    falls länge(matrix) ist 0:
        zurückgeben []

    zeilen = länge(matrix)
    spalten = länge(matrix[0])

    ergebnis = []
    für j in bereich(spalten):
        zeile = []
        für i in bereich(zeilen):
            zeile.hinzufügen(matrix[i][j])
        ergebnis.hinzufügen(zeile)

    zurückgeben ergebnis


Funktion determinante_2x2(matrix: liste) -> zahl:
    """Berechne die Determinante einer 2×2 Matrix."""
    zurückgeben (matrix[0][0] * matrix[1][1]) - (matrix[0][1] * matrix[1][0])


Funktion determinante_3x3(matrix: liste) -> zahl:
    """Berechne die Determinante einer 3×3 Matrix mit der Regel von Sarrus."""
    a = matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
    b = matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
    c = matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])

    zurückgeben a - b + c


Funktion frobenius_norm(matrix: liste) -> zahl:
    """Berechne die Frobenius-Norm (Wurzel der Summe der Quadrate)."""
    summe_quadrate = 0
    für zeile in matrix:
        für element in zeile:
            summe_quadrate = summe_quadrate + (element * element)

    zurückgeben summe_quadrate ** 0.5


Funktion hauptfunktion():
    # Teste 2×2 Matrizen
    ausgabe("=== Test von 2x2 Matrizen ===")
    a2 = [[1, 2], [3, 4]]
    b2 = [[5, 6], [7, 8]]

    ergebnis2 = multipliziere_matrizen(a2, b2)
    ausgabe("Ergebnis der 2x2 Multiplikation:")
    für zeile in ergebnis2:
        ausgabe(zeile)

    # Teste Einheitsmatrix
    ausgabe("\n=== Test der Einheitsmatrix ===")
    einheit = erstelle_einheitsmatrix(3)
    ausgabe("3x3 Einheitsmatrix:")
    für zeile in einheit:
        ausgabe(zeile)

    # Teste Transposition
    ausgabe("\n=== Test der Transposition ===")
    test_matrix = erstelle_testmatrix(3)
    ausgabe("Ursprüngliche 3x3 Testmatrix:")
    für zeile in test_matrix:
        ausgabe(zeile)

    transponiert = transponiere_matrix(test_matrix)
    ausgabe("Transponiert:")
    für zeile in transponiert:
        ausgabe(zeile)

    # Teste Determinante
    ausgabe("\n=== Test der Determinante ===")
    det2 = determinante_2x2(a2)
    ausgabe(f"Det(2x2) = {det2}")

    det3 = determinante_3x3(test_matrix)
    ausgabe(f"Det(3x3) = {det3}")

    # Teste größere Matrizenmultiplikation
    ausgabe("\n=== Test der Multiplikation von größeren Matrizen ===")
    a_gross = erstelle_testmatrix(4)
    b_gross = erstelle_testmatrix(4)

    ergebnis_gross = multipliziere_matrizen(a_gross, b_gross)
    ausgabe(f"4x4 Matrizenmultiplikation abgeschlossen. Erste Zeile: {ergebnis_gross[0]}")

    ausgabe("\n✓ Alle Matrixoperationen wurden erfolgreich abgeschlossen")


hauptfunktion()
