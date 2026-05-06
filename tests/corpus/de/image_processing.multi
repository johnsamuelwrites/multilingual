# Bildverarbeitung - Projekt WASM Corpus
# Deutsche Variante
#
# Demonstriert:
# - Einfache Bildfilter (Unschärfe, Kantenerkennung)
# - Pixelmanipulation
# - Bildtransformation
# - SIMD-geeignete Operationen für WASM

# SPDX-License-Identifier: GPL-3.0-or-later

Funktion erstelle_testbild(breite: ganze_zahl, höhe: ganze_zahl) -> liste:
    """Erstelle ein einfaches Testbild (Grauwert-Pixelwerte)."""
    bild = []
    für y in bereich(höhe):
        zeile = []
        für x in bereich(breite):
            # Einfaches Gradienten-Muster erstellen
            pixel = ((x + y) * 255) // (breite + höhe)
            zeile.hinzufügen(pixel)
        bild.hinzufügen(zeile)
    zurückgeben bild


Funktion unschärfe_filter(bild: liste, kernel_größe: ganze_zahl) -> liste:
    """Einfachen Kastenunschärfe-Filter anwenden."""
    höhe = länge(bild)
    falls höhe ist 0:
        zurückgeben []

    breite = länge(bild[0])
    ergebnis = []

    für y in bereich(höhe):
        zeile = []
        für x in bereich(breite):
            # Durchschnitt der umgebenden Pixel berechnen
            summe = 0
            anzahl = 0

            für dy in bereich(-kernel_größe, kernel_größe + 1):
                für dx in bereich(-kernel_größe, kernel_größe + 1):
                    ny = y + dy
                    nx = x + dx

                    falls (ny >= 0) und (ny < höhe) und (nx >= 0) und (nx < breite):
                        summe = summe + bild[ny][nx]
                        anzahl = anzahl + 1

            durchschnitt = summe // anzahl falls anzahl > 0 sonst 0
            zeile.hinzufügen(durchschnitt)

        ergebnis.hinzufügen(zeile)

    zurückgeben ergebnis


Funktion kantenerkennung(bild: liste) -> liste:
    """Einfache Sobel-Kantenerkennung."""
    höhe = länge(bild)
    falls höhe < 3:
        zurückgeben bild

    breite = länge(bild[0])
    falls breite < 3:
        zurückgeben bild

    ergebnis = []

    für y in bereich(1, höhe - 1):
        zeile = []
        für x in bereich(1, breite - 1):
            # Vereinfachter Sobel-Operator
            gx = (bild[y-1][x+1] + 2*bild[y][x+1] + bild[y+1][x+1]) - \
                 (bild[y-1][x-1] + 2*bild[y][x-1] + bild[y+1][x-1])

            gy = (bild[y+1][x-1] + 2*bild[y+1][x] + bild[y+1][x+1]) - \
                 (bild[y-1][x-1] + 2*bild[y-1][x] + bild[y-1][x+1])

            # Größe berechnen (vereinfacht)
            größe = (gx * gx + gy * gy) ** 0.5
            # Auf 0-255 begrenzen
            größe = ganze_zahl(größe) falls größe < 256 sonst 255
            zeile.hinzufügen(größe)

        ergebnis.hinzufügen(zeile)

    zurückgeben ergebnis


Funktion grauwert_zu_binär(bild: liste, schwellenwert: ganze_zahl) -> liste:
    """Konvertiere Grauwertbild zu Binärbild (Schwarz und Weiß)."""
    binär = []
    für zeile in bild:
        binärzeile = []
        für pixel in zeile:
            binärwert = 1 falls pixel >= schwellenwert sonst 0
            binärzeile.hinzufügen(binärwert)
        binär.hinzufügen(binärzeile)
    zurückgeben binär


Funktion farben_invertieren(bild: liste) -> liste:
    """Farben invertieren (255 - Pixel für jeden Pixel)."""
    invertiert = []
    für zeile in bild:
        invertierte_zeile = []
        für pixel in zeile:
            invertierte_zeile.hinzufügen(255 - pixel)
        invertiert.hinzufügen(invertierte_zeile)
    zurückgeben invertiert


Funktion histogramm_berechnen(bild: liste) -> liste:
    """Histogramm berechnen (Häufigkeit jeder Helligkeitsstufe)."""
    histogramm = []
    für i in bereich(256):
        histogramm.hinzufügen(0)

    für zeile in bild:
        für pixel in zeile:
            falls pixel >= 0 und pixel < 256:
                histogramm[pixel] = histogramm[pixel] + 1

    zurückgeben histogramm


Funktion hauptfunktion():
    # Testbild erstellen
    ausgabe("=== Bildverarbeitungs-Demonstration ===")
    ausgabe("Erstelle Testbild (8x8)...")
    bild = erstelle_testbild(8, 8)
    ausgabe(f"Bild erstellt: {länge(bild)}x{länge(bild[0])}")

    # Originalbild anzeigen
    ausgabe("\nOriginalbild (erste Zeile):")
    ausgabe(bild[0])

    # Unschärfefilter anwenden
    ausgabe("\n=== Anwendung des Unschärfe-Filters ===")
    unscharfes_bild = unschärfe_filter(bild, 1)
    ausgabe("Unscharfes Bild (erste Zeile):")
    ausgabe(unscharfes_bild[0])

    # Kantenerkennung
    ausgabe("\n=== Anwendung der Kantenerkennung ===")
    kanten = kantenerkennung(bild)
    ausgabe(f"Kantenerkennung abgeschlossen: {länge(kanten)}x{länge(kanten[0])}")
    ausgabe("Kantenkarte (erste Zeile):")
    ausgabe(kanten[0])

    # Farben invertieren
    ausgabe("\n=== Farben Invertieren ===")
    invertiert = farben_invertieren(bild)
    ausgabe("Invertiertes Bild (erste Zeile):")
    ausgabe(invertiert[0])

    # Binär-Umwandlung
    ausgabe("\n=== Konvertierung zu Binär ===")
    binär = grauwert_zu_binär(bild, 128)
    ausgabe("Binärbild (erste Zeile):")
    ausgabe(binär[0])

    # Histogramm
    ausgabe("\n=== Histogramm-Berechnung ===")
    hist = histogramm_berechnen(bild)
    # Die ersten 10 Histogramm-Werte anzeigen
    ausgabe(f"Histogramm (erste 10 Buckets): {hist[0:10]}")

    # Belastungstest: großes Bild
    ausgabe("\n=== Belastungstest: Verarbeitung eines großen Bildes ===")
    großes_bild = erstelle_testbild(32, 32)
    ausgabe(f"Erstellt {länge(großes_bild)}x{länge(großes_bild[0])} Bild")

    unscharfes_großes_bild = unschärfe_filter(großes_bild, 2)
    ausgabe("Unschärfefilter auf großes Bild angewendet")

    kanten_große = kantenerkennung(großes_bild)
    ausgabe("Kantenerkennung auf großes Bild angewendet")

    ausgabe("\n✓ Alle Bildverarbeitungsoperationen erfolgreich abgeschlossen")


hauptfunktion()
