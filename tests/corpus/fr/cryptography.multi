# Cryptographie - Projet WASM Corpus
# Variante française
#
# Démontre:
# - Chiffre de substitution simple (basé sur XOR)
# - Fonction de hachage (simple mais déterministe)
# - Vérification de mot de passe
# - Opérations calcul-intensif idéales pour WASM

# SPDX-License-Identifier: GPL-3.0-or-later

fonction hachage_simple(texte: chaîne) -> entier:
    """Fonction de hachage simple (non cryptographiquement sûre, pour démo)."""
    valeur_hash = 0
    pour caractère dans texte:
        valeur_hash = ((valeur_hash << 5) - valeur_hash) + ord(caractère)
        valeur_hash = valeur_hash & 0xFFFFFFFF  # Garder comme 32-bit
    retourne valeur_hash


fonction chiffrer_xor(texte_clair: chaîne, clé: chaîne) -> chaîne:
    """Chiffre XOR simple (non sûr, démo uniquement)."""
    resultat = []
    pour i dans intervalle(longueur(texte_clair)):
        caractère_clé = clé[i % longueur(clé)]
        caractère_chiffré = chr(ord(texte_clair[i]) ^ ord(caractère_clé))
        resultat.ajouter(caractère_chiffré)
    retourne "".joindre(resultat)


fonction déchiffrer_xor(texte_chiffré: chaîne, clé: chaîne) -> chaîne:
    """Déchiffrer chiffre XOR (même que le chiffrement pour XOR)."""
    retourne chiffrer_xor(texte_chiffré, clé)


fonction vérifier_mot_passe(mot_passe: chaîne, hachage_mot_passe: entier) -> booléen:
    """Vérifier que le mot de passe correspond au hachage."""
    retourne hachage_simple(mot_passe) est hachage_mot_passe


fonction hachage_chunks(texte: chaîne, taille_chunk: entier) -> liste:
    """Hacher une chaîne par chunks."""
    hachages = []
    pour i dans intervalle(0, longueur(texte), taille_chunk):
        chunk = texte[i : i + taille_chunk]
        hachages.ajouter(hachage_simple(chunk))
    retourne hachages


fonction chiffrer_message(texte_clair: chaîne, clé: chaîne) -> chaîne:
    """Chiffrer un message avec chiffre XOR."""
    retourne chiffrer_xor(texte_clair, clé)


fonction déchiffrer_message(texte_chiffré: chaîne, clé: chaîne) -> chaîne:
    """Déchiffrer un message avec chiffre XOR."""
    retourne déchiffrer_xor(texte_chiffré, clé)


fonction chiffre_caesar(texte: chaîne, décalage: entier) -> chaîne:
    """Chiffre de César simple (décaler chaque lettre)."""
    resultat = []
    pour caractère dans texte:
        si caractère.isalpha():
            si caractère.isupper():
                décalé = chr((ord(caractère) - ord("A") + décalage) % 26 + ord("A"))
            sinon:
                décalé = chr((ord(caractère) - ord("a") + décalage) % 26 + ord("a"))
            resultat.ajouter(décalé)
        sinon:
            resultat.ajouter(caractère)
    retourne "".joindre(resultat)


fonction principal():
    # Tester fonction hachage
    afficher("=== Test de la Fonction de Hachage ===")
    mot_passe = "mySecurePassword123"
    hachage_mot_passe = hachage_simple(mot_passe)
    afficher(f"Hachage de '{mot_passe}': {hachage_mot_passe}")
    afficher(f"Vérification du hachage: {vérifier_mot_passe(mot_passe, hachage_mot_passe)}")
    afficher(f"Vérification mauvais mot de passe: {vérifier_mot_passe('wrongpassword', hachage_mot_passe)}")

    # Tester chiffre XOR
    afficher("\n=== Test du Chiffre XOR ===")
    texte_clair = "Hello World!"
    clé = "secretkey"

    texte_chiffré = chiffrer_xor(texte_clair, clé)
    afficher(f"Original: {texte_clair}")
    afficher(f"Chiffré: {texte_chiffré}")

    texte_déchiffré = déchiffrer_xor(texte_chiffré, clé)
    afficher(f"Déchiffré: {texte_déchiffré}")
    afficher(f"Correspond à l'original: {texte_déchiffré est texte_clair}")

    # Tester chiffre de César
    afficher("\n=== Test du Chiffre de César ===")
    message = "Attack at dawn"
    décalé = chiffre_caesar(message, 3)
    afficher(f"Original: {message}")
    afficher(f"Décalé de 3: {décalé}")
    non_décalé = chiffre_caesar(décalé, -3)
    afficher(f"Décalé retour: {non_décalé}")

    # Tester hachage par chunks
    afficher("\n=== Test du Hachage par Chunks ===")
    long_texte = "This is a longer message that we will split into chunks and hash individually."
    hachages_chunks = hachage_chunks(long_texte, 10)
    afficher(f"Longueur du texte: {longueur(long_texte)}")
    afficher(f"Nombre de chunks: {longueur(hachages_chunks)}")
    afficher(f"Hachage du premier chunk: {hachages_chunks[0]}")

    # Test de stress: chiffrements multiples
    afficher("\n=== Test de Stress: Chiffrements Multiples ===")
    messages = [
        "Secret message 1",
        "Another secret 2",
        "Final secret 3",
    ]
    clé = "masterkey"

    tous_chiffrés = []
    pour msg dans messages:
        texte_chiffré = chiffrer_xor(msg, clé)
        tous_chiffrés.ajouter(texte_chiffré)
        afficher(f"Chiffré: {longueur(texte_chiffré)} octets")

    afficher("\n✓ Toutes les opérations de cryptographie ont été complétées avec succès")


principal()
