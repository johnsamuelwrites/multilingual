# JSON-Analyse - Projekt WASM Corpus
# Deutsche Variante
#
# Demonstriert:
# - JSON-Analyse (String-Verarbeitung)
# - JSON-Serialisierung
# - Datenstruktur-Manipulation
# - Datenintensive Operationen ideal für WASM

# SPDX-License-Identifier: GPL-3.0-or-later

Funktion einfache_json_analyse(json_string: string) -> objekt:
    """Einfache JSON-Analyse (mit eingebautem Parser)."""
    importieren json
    zurückgeben json.laden(json_string)


Funktion json_stringifizieren(obj: objekt) -> string:
    """Objekt in JSON-String konvertieren."""
    importieren json
    zurückgeben json.dump(obj)


Funktion beispieldaten_erstellen() -> objekt:
    """Beispiel-Datenstruktur erstellen."""
    daten = {
        "benutzer": [
            {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "rollen": ["admin", "benutzer"],
            },
            {
                "id": 2,
                "name": "Bob",
                "email": "bob@example.com",
                "rollen": ["benutzer"],
            },
            {
                "id": 3,
                "name": "Charlie",
                "email": "charlie@example.com",
                "rollen": ["benutzer", "moderator"],
            },
        ],
        "metadaten": {
            "version": "1.0",
            "timestamp": "2024-02-22T10:00:00Z",
            "gesamtbenutzer": 3,
        },
    }
    zurückgeben daten


Funktion benutzer_nach_rolle_filtern(benutzer: liste, rolle: string) -> liste:
    """Benutzer filtern, die eine bestimmte Rolle haben."""
    gefiltert = []
    für benutzer_obj in benutzer:
        falls "rollen" in benutzer_obj:
            falls rolle in benutzer_obj["rollen"]:
                gefiltert.hinzufügen(benutzer_obj)
    zurückgeben gefiltert


Funktion benutzer_pro_rolle_zählen(benutzer: liste) -> objekt:
    """Vorkommen jeder Rolle zählen."""
    rollenzähler = {}
    für benutzer_obj in benutzer:
        falls "rollen" in benutzer_obj:
            für rolle in benutzer_obj["rollen"]:
                falls rolle not in rollenzähler:
                    rollenzähler[rolle] = 0
                rollenzähler[rolle] = rollenzähler[rolle] + 1
    zurückgeben rollenzähler


Funktion e_mails_extrahieren(benutzer: liste) -> liste:
    """E-Mail-Adressen aus Benutzerliste extrahieren."""
    e_mails = []
    für benutzer_obj in benutzer:
        falls "email" in benutzer_obj:
            e_mails.hinzufügen(benutzer_obj["email"])
    zurückgeben e_mails


Funktion benutzernamen_transformieren(benutzer: liste) -> liste:
    """Benutzernamen in Großbuchstaben umwandeln."""
    transformiert = []
    für benutzer_obj in benutzer:
        benutzer_kopie = {
            "id": benutzer_obj.abrufen("id"),
            "name": benutzer_obj.abrufen("name", "").großbuchstaben(),
            "email": benutzer_obj.abrufen("email"),
        }
        transformiert.hinzufügen(benutzer_kopie)
    zurückgeben transformiert


Funktion json_objekte_fusionieren(obj1: objekt, obj2: objekt) -> objekt:
    """Zwei JSON-Objekte zusammenführen."""
    fusioniert = obj1.kopieren()
    für schlüssel, wert in obj2.elemente():
        fusioniert[schlüssel] = wert
    zurückgeben fusioniert


Funktion benutzer_validieren(benutzer_obj: objekt) -> wahrheitswert:
    """Validieren, dass Benutzer-Objekt erforderliche Felder hat."""
    erforderliche_felder = ["id", "name", "email"]
    für feld in erforderliche_felder:
        falls feld not in benutzer_obj:
            zurückgeben falsch
    zurückgeben wahr


Funktion hauptfunktion():
    ausgabe("=== JSON-Analyse-Demonstration ===")

    # Beispieldaten erstellen und serialisieren
    ausgabe("\n1. Beispieldaten erstellen...")
    daten = beispieldaten_erstellen()
    ausgabe(f"Datenstruktur mit {länge(daten['benutzer'])} Benutzern erstellt")

    # In JSON konvertieren
    ausgabe("\n2. Serialisierung zu JSON...")
    json_string = json_stringifizieren(daten)
    ausgabe(f"JSON-String-Länge: {länge(json_string)} Zeichen")
    ausgabe(f"Erste 100 Zeichen: {json_string[0:100]}")

    # Aus JSON zurück analysieren
    ausgabe("\n3. JSON zurück zu Objekt analysieren...")
    analysierte_daten = einfache_json_analyse(json_string)
    ausgabe(f"Erfolgreich analysiert: {länge(analysierte_daten['benutzer'])} Benutzer")

    # Filter-Operationen
    ausgabe("\n4. Benutzer nach Rolle filtern...")
    admin_benutzer = benutzer_nach_rolle_filtern(daten["benutzer"], "admin")
    ausgabe(f"Gefunden: {länge(admin_benutzer)} Admin-Benutzer")

    moderator_benutzer = benutzer_nach_rolle_filtern(daten["benutzer"], "moderator")
    ausgabe(f"Gefunden: {länge(moderator_benutzer)} Moderator-Benutzer")

    # Rollen zählen
    ausgabe("\n5. Rollen zählen...")
    rollenzähler = benutzer_pro_rolle_zählen(daten["benutzer"])
    ausgabe(f"Rollenverteilung: {rollenzähler}")

    # E-Mails extrahieren
    ausgabe("\n6. E-Mails extrahieren...")
    e_mails = e_mails_extrahieren(daten["benutzer"])
    ausgabe(f"E-Mails: {e_mails}")

    # Daten transformieren
    ausgabe("\n7. Benutzernamen in Großbuchstaben umwandeln...")
    großbuchstaben_benutzer = benutzernamen_transformieren(daten["benutzer"])
    für benutzer_obj in großbuchstaben_benutzer:
        ausgabe(f"  {benutzer_obj['name']} ({benutzer_obj['email']})")

    # Benutzer validieren
    ausgabe("\n8. Benutzer validieren...")
    gültig_zähler = 0
    für benutzer_obj in daten["benutzer"]:
        falls benutzer_validieren(benutzer_obj):
            gültig_zähler = gültig_zähler + 1
    ausgabe(f"Gültige Benutzer: {gültig_zähler}/{länge(daten['benutzer'])}")

    # Objekte fusionieren
    ausgabe("\n9. JSON-Objekte fusionieren...")
    neue_metadaten = {"autor": "test", "überarbeitung": 2}
    fusioniert = json_objekte_fusionieren(daten["metadaten"], neue_metadaten)
    ausgabe(f"Fusionierte Metadaten-Schlüssel: {länge(fusioniert)}")

    # Belastungstest: großes JSON
    ausgabe("\n10. Belastungstest: großes JSON verarbeiten...")
    große_daten = {
        "elemente": [],
    }
    für i in bereich(100):
        große_daten["elemente"].hinzufügen({
            "id": i,
            "wert": i * 10,
            "verarbeitet": falsch,
        })

    großes_json = json_stringifizieren(große_daten)
    ausgabe(f"Großes JSON erstellt: {länge(großes_json)} Zeichen")

    analysierte_große_daten = einfache_json_analyse(großes_json)
    ausgabe(f"Großes JSON analysiert: {länge(analysierte_große_daten['elemente'])} Elemente")

    ausgabe("\n✓ Alle JSON-Operationen erfolgreich abgeschlossen")


hauptfunktion()
