# Analyse JSON - Projet WASM Corpus
# Variante française
#
# Démontre:
# - Analyse JSON (traitement de chaînes)
# - Sérialisation JSON
# - Manipulation de structures de données
# - Opérations intensives en données idéales pour WASM

# SPDX-License-Identifier: GPL-3.0-or-later

fonction analyser_json_simple(chaîne_json: chaîne) -> objet:
    """Analyser JSON simple (en utilisant l'analyseur intégré)."""
    importer json
    retourne json.charges(chaîne_json)


fonction stringify_json(obj: objet) -> chaîne:
    """Convertir un objet en chaîne JSON."""
    importer json
    retourne json.dumps(obj)


fonction créer_données_exemple() -> objet:
    """Créer une structure de données exemple."""
    données = {
        "utilisateurs": [
            {
                "id": 1,
                "nom": "Alice",
                "email": "alice@example.com",
                "rôles": ["admin", "utilisateur"],
            },
            {
                "id": 2,
                "nom": "Bob",
                "email": "bob@example.com",
                "rôles": ["utilisateur"],
            },
            {
                "id": 3,
                "nom": "Charlie",
                "email": "charlie@example.com",
                "rôles": ["utilisateur", "modérateur"],
            },
        ],
        "métadonnées": {
            "version": "1.0",
            "timestamp": "2024-02-22T10:00:00Z",
            "total_utilisateurs": 3,
        },
    }
    retourne données


fonction filtrer_utilisateurs_par_rôle(utilisateurs: liste, rôle: chaîne) -> liste:
    """Filtrer les utilisateurs qui ont un rôle spécifique."""
    filtrés = []
    pour utilisateur dans utilisateurs:
        si "rôles" dans utilisateur:
            si rôle dans utilisateur["rôles"]:
                filtrés.ajouter(utilisateur)
    retourne filtrés


fonction compter_utilisateurs_par_rôle(utilisateurs: liste) -> objet:
    """Compter les occurrences de chaque rôle."""
    comptage_rôles = {}
    pour utilisateur dans utilisateurs:
        si "rôles" dans utilisateur:
            pour rôle dans utilisateur["rôles"]:
                si rôle non dans comptage_rôles:
                    comptage_rôles[rôle] = 0
                comptage_rôles[rôle] = comptage_rôles[rôle] + 1
    retourne comptage_rôles


fonction extraire_emails(utilisateurs: liste) -> liste:
    """Extraire les adresses email de la liste des utilisateurs."""
    emails = []
    pour utilisateur dans utilisateurs:
        si "email" dans utilisateur:
            emails.ajouter(utilisateur["email"])
    retourne emails


fonction transformer_noms_utilisateurs(utilisateurs: liste) -> liste:
    """Transformer les noms d'utilisateurs en majuscules."""
    transformés = []
    pour utilisateur dans utilisateurs:
        copie_utilisateur = {
            "id": utilisateur.obtenir("id"),
            "nom": utilisateur.obtenir("nom", "").majuscule(),
            "email": utilisateur.obtenir("email"),
        }
        transformés.ajouter(copie_utilisateur)
    retourne transformés


fonction fusionner_objets_json(obj1: objet, obj2: objet) -> objet:
    """Fusionner deux objets JSON."""
    fusionné = obj1.copie()
    pour clé, valeur dans obj2.éléments():
        fusionné[clé] = valeur
    retourne fusionné


fonction valider_utilisateur(utilisateur: objet) -> booléen:
    """Valider que l'objet utilisateur a les champs requis."""
    champs_requis = ["id", "nom", "email"]
    pour champ dans champs_requis:
        si champ non dans utilisateur:
            retourne faux
    retourne vrai


fonction principal():
    afficher("=== Démonstration de l'Analyse JSON ===")

    # Créer et sérialiser les données exemple
    afficher("\n1. Création des données exemple...")
    données = créer_données_exemple()
    afficher(f"Structure de données créée avec {longueur(données['utilisateurs'])} utilisateurs")

    # Convertir en JSON
    afficher("\n2. Sérialisation en JSON...")
    chaîne_json = stringify_json(données)
    afficher(f"Longueur de chaîne JSON: {longueur(chaîne_json)} caractères")
    afficher(f"Premiers 100 caractères: {chaîne_json[0:100]}")

    # Analyser depuis JSON
    afficher("\n3. Analyse JSON retour vers objet...")
    données_analysées = analyser_json_simple(chaîne_json)
    afficher(f"Analyse réussie: {longueur(données_analysées['utilisateurs'])} utilisateurs")

    # Opérations de filtrage
    afficher("\n4. Filtrage des utilisateurs par rôle...")
    utilisateurs_admin = filtrer_utilisateurs_par_rôle(données["utilisateurs"], "admin")
    afficher(f"Trouvé {longueur(utilisateurs_admin)} utilisateur(s) admin")

    utilisateurs_modérateur = filtrer_utilisateurs_par_rôle(données["utilisateurs"], "modérateur")
    afficher(f"Trouvé {longueur(utilisateurs_modérateur)} utilisateur(s) modérateur")

    # Compter les rôles
    afficher("\n5. Comptage des rôles...")
    comptage_rôles = compter_utilisateurs_par_rôle(données["utilisateurs"])
    afficher(f"Distribution des rôles: {comptage_rôles}")

    # Extraire les emails
    afficher("\n6. Extraction des emails...")
    emails = extraire_emails(données["utilisateurs"])
    afficher(f"Emails: {emails}")

    # Transformer les données
    afficher("\n7. Transformation des noms d'utilisateurs en majuscules...")
    utilisateurs_majuscules = transformer_noms_utilisateurs(données["utilisateurs"])
    pour utilisateur dans utilisateurs_majuscules:
        afficher(f"  {utilisateur['nom']} ({utilisateur['email']})")

    # Valider les utilisateurs
    afficher("\n8. Validation des utilisateurs...")
    comptage_valides = 0
    pour utilisateur dans données["utilisateurs"]:
        si valider_utilisateur(utilisateur):
            comptage_valides = comptage_valides + 1
    afficher(f"Utilisateurs valides: {comptage_valides}/{longueur(données['utilisateurs'])}")

    # Fusionner les objets
    afficher("\n9. Fusion des objets JSON...")
    nouvelles_métadonnées = {"auteur": "test", "révision": 2}
    fusionné = fusionner_objets_json(données["métadonnées"], nouvelles_métadonnées)
    afficher(f"Clés de métadonnées fusionnées: {longueur(fusionné)}")

    # Test de charge: grand JSON
    afficher("\n10. Test de charge: traitement du grand JSON...")
    grandes_données = {
        "éléments": [],
    }
    pour i dans intervalle(100):
        grandes_données["éléments"].ajouter({
            "id": i,
            "valeur": i * 10,
            "traité": faux,
        })

    grand_json = stringify_json(grandes_données)
    afficher(f"Grand JSON créé: {longueur(grand_json)} caractères")

    grandes_données_analysées = analyser_json_simple(grand_json)
    afficher(f"Grand JSON analysé: {longueur(grandes_données_analysées['éléments'])} éléments")

    afficher("\n✓ Toutes les opérations JSON ont été complétées avec succès")


principal()
