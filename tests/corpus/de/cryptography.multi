# Kryptografie - Projekt WASM Corpus
# Deutsche Variante
#
# Demonstriert:
# - Einfache Substitutionsziffre (XOR-basiert)
# - Hashfunktion (einfach aber deterministisch)
# - Passwortverifikation
# - Rechenintensive Operationen ideal für WASM

# SPDX-License-Identifier: GPL-3.0-or-later

Funktion einfacher_hash(text: string) -> ganze_zahl:
    """Einfache Hashfunktion (nicht kryptographisch sicher, nur für Demo)."""
    hash_wert = 0
    für zeichen in text:
        hash_wert = ((hash_wert << 5) - hash_wert) + ord(zeichen)
        hash_wert = hash_wert & 0xFFFFFFFF  # Als 32-Bit behalten
    zurückgeben hash_wert


Funktion xor_verschlüsseln(klartext: string, schlüssel: string) -> string:
    """Einfache XOR-Ziffre (nicht sicher, nur für Demo)."""
    ergebnis = []
    für i in bereich(länge(klartext)):
        schlüssel_zeichen = schlüssel[i % länge(schlüssel)]
        verschlüsseltes_zeichen = chr(ord(klartext[i]) ^ ord(schlüssel_zeichen))
        ergebnis.hinzufügen(verschlüsseltes_zeichen)
    zurückgeben "".verbinden(ergebnis)


Funktion xor_entschlüsseln(geheimtext: string, schlüssel: string) -> string:
    """XOR-Ziffre entschlüsseln (gleich wie Verschlüsselung für XOR)."""
    zurückgeben xor_verschlüsseln(geheimtext, schlüssel)


Funktion passwort_verifizieren(passwort: string, passwort_hash: ganze_zahl) -> wahrheitswert:
    """Verifiziere, dass Passwort dem Hash entspricht."""
    zurückgeben einfacher_hash(passwort) ist passwort_hash


Funktion hash_chunks(text: string, chunk_größe: ganze_zahl) -> liste:
    """Hashiere einen String in Chunks."""
    hashes = []
    für i in bereich(0, länge(text), chunk_größe):
        chunk = text[i : i + chunk_größe]
        hashes.hinzufügen(einfacher_hash(chunk))
    zurückgeben hashes


Funktion nachricht_verschlüsseln(klartext: string, schlüssel: string) -> string:
    """Verschlüssele eine Nachricht mit XOR-Ziffre."""
    zurückgeben xor_verschlüsseln(klartext, schlüssel)


Funktion nachricht_entschlüsseln(geheimtext: string, schlüssel: string) -> string:
    """Entschlüssele eine Nachricht mit XOR-Ziffre."""
    zurückgeben xor_entschlüsseln(geheimtext, schlüssel)


Funktion cäsar_ziffre(text: string, versatz: ganze_zahl) -> string:
    """Einfache Caesar-Ziffre (jeden Buchstaben verschieben)."""
    ergebnis = []
    für zeichen in text:
        falls zeichen.isalpha():
            falls zeichen.isupper():
                verschoben = chr((ord(zeichen) - ord("A") + versatz) % 26 + ord("A"))
            sonst:
                verschoben = chr((ord(zeichen) - ord("a") + versatz) % 26 + ord("a"))
            ergebnis.hinzufügen(verschoben)
        sonst:
            ergebnis.hinzufügen(zeichen)
    zurückgeben "".verbinden(ergebnis)


Funktion hauptfunktion():
    # Teste Hash-Funktion
    ausgabe("=== Test der Hash-Funktion ===")
    passwort = "mySecurePassword123"
    passwort_hash = einfacher_hash(passwort)
    ausgabe(f"Hash von '{passwort}': {passwort_hash}")
    ausgabe(f"Hash-Verifizierung: {passwort_verifizieren(passwort, passwort_hash)}")
    ausgabe(f"Falsches Passwort-Verifizierung: {passwort_verifizieren('wrongpassword', passwort_hash)}")

    # Teste XOR-Ziffre
    ausgabe("\n=== Test der XOR-Ziffre ===")
    klartext = "Hello World!"
    schlüssel = "secretkey"

    geheimtext = xor_verschlüsseln(klartext, schlüssel)
    ausgabe(f"Original: {klartext}")
    ausgabe(f"Verschlüsselt: {geheimtext}")

    entschlüsselter_text = xor_entschlüsseln(geheimtext, schlüssel)
    ausgabe(f"Entschlüsselt: {entschlüsselter_text}")
    ausgabe(f"Stimmt mit Original überein: {entschlüsselter_text ist klartext}")

    # Teste Caesar-Ziffre
    ausgabe("\n=== Test der Caesar-Ziffre ===")
    nachricht = "Attack at dawn"
    verschoben = cäsar_ziffre(nachricht, 3)
    ausgabe(f"Original: {nachricht}")
    ausgabe(f"Verschoben um 3: {verschoben}")
    nicht_verschoben = cäsar_ziffre(verschoben, -3)
    ausgabe(f"Zurück verschoben: {nicht_verschoben}")

    # Teste Hash-Chunks
    ausgabe("\n=== Test der Hash-Chunks ===")
    langer_text = "This is a longer message that we will split into chunks and hash individually."
    hash_chunks_liste = hash_chunks(langer_text, 10)
    ausgabe(f"Textlänge: {länge(langer_text)}")
    ausgabe(f"Anzahl Chunks: {länge(hash_chunks_liste)}")
    ausgabe(f"Hash des ersten Chunks: {hash_chunks_liste[0]}")

    # Belastungstest: mehrfache Verschlüsselungen
    ausgabe("\n=== Belastungstest: Mehrfache Verschlüsselungen ===")
    nachrichten = [
        "Secret message 1",
        "Another secret 2",
        "Final secret 3",
    ]
    schlüssel = "masterkey"

    alle_verschlüsselt = []
    für msg in nachrichten:
        geheimtext = xor_verschlüsseln(msg, schlüssel)
        alle_verschlüsselt.hinzufügen(geheimtext)
        ausgabe(f"Verschlüsselt: {länge(geheimtext)} Bytes")

    ausgabe("\n✓ Alle Kryptografie-Operationen erfolgreich abgeschlossen")


hauptfunktion()
