# Opérations Matricielles - Projet WASM Corpus
# Variante française
#
# Démontre:
# - Multiplication matricielle (calcul intensif, point fort WASM)
# - Transposée de matrice
# - Calcul de déterminant
# - Opérations sensibles à la performance

# SPDX-License-Identifier: GPL-3.0-or-later

fonction creer_matrice_identite(n: entier) -> liste:
    """Créer une matrice identité n×n."""
    resultat = []
    pour i dans intervalle(n):
        ligne = []
        pour j dans intervalle(n):
            si i est j:
                ligne.ajouter(1)
            sinon:
                ligne.ajouter(0)
        resultat.ajouter(ligne)
    retourne resultat


fonction creer_matrice_test(n: entier) -> liste:
    """Créer une matrice n×n avec des valeurs séquentielles."""
    resultat = []
    compteur = 1
    pour i dans intervalle(n):
        ligne = []
        pour j dans intervalle(n):
            ligne.ajouter(compteur)
            compteur = compteur + 1
        resultat.ajouter(ligne)
    retourne resultat


fonction multiplier_matrices(a: liste, b: liste) -> liste:
    """Multiplier deux matrices.

    Arguments:
        a: matrice m×n (liste de listes)
        b: matrice n×p (liste de listes)

    Retourne:
        matrice m×p résultante
    """
    m = longueur(a)
    n = longueur(a[0])
    p = longueur(b[0])

    resultat = []
    pour i dans intervalle(m):
        ligne = []
        pour j dans intervalle(p):
            somme = 0
            pour k dans intervalle(n):
                somme = somme + (a[i][k] * b[k][j])
            ligne.ajouter(somme)
        resultat.ajouter(ligne)

    retourne resultat


fonction transposer_matrice(matrice: liste) -> liste:
    """Transposer une matrice (échanger lignes et colonnes)."""
    si longueur(matrice) est 0:
        retourne []

    lignes = longueur(matrice)
    colonnes = longueur(matrice[0])

    resultat = []
    pour j dans intervalle(colonnes):
        ligne = []
        pour i dans intervalle(lignes):
            ligne.ajouter(matrice[i][j])
        resultat.ajouter(ligne)

    retourne resultat


fonction determinant_2x2(matrice: liste) -> nombre:
    """Calculer le déterminant d'une matrice 2×2."""
    retourne (matrice[0][0] * matrice[1][1]) - (matrice[0][1] * matrice[1][0])


fonction determinant_3x3(matrice: liste) -> nombre:
    """Calculer le déterminant d'une matrice 3×3 avec la règle de Sarrus."""
    a = matrice[0][0] * (matrice[1][1] * matrice[2][2] - matrice[1][2] * matrice[2][1])
    b = matrice[0][1] * (matrice[1][0] * matrice[2][2] - matrice[1][2] * matrice[2][0])
    c = matrice[0][2] * (matrice[1][0] * matrice[2][1] - matrice[1][1] * matrice[2][0])

    retourne a - b + c


fonction norme_frobenius(matrice: liste) -> nombre:
    """Calculer la norme de Frobenius (racine de la somme des carrés)."""
    somme_carres = 0
    pour ligne dans matrice:
        pour element dans ligne:
            somme_carres = somme_carres + (element * element)

    retourne somme_carres ** 0.5


fonction principal():
    # Tester matrices 2×2
    afficher("=== Test des Matrices 2x2 ===")
    a2 = [[1, 2], [3, 4]]
    b2 = [[5, 6], [7, 8]]

    resultat2 = multiplier_matrices(a2, b2)
    afficher("Résultat de la multiplication 2x2:")
    pour ligne dans resultat2:
        afficher(ligne)

    # Tester matrice identité
    afficher("\n=== Test de la Matrice Identité ===")
    identite = creer_matrice_identite(3)
    afficher("Matrice identité 3x3:")
    pour ligne dans identite:
        afficher(ligne)

    # Tester transposée
    afficher("\n=== Test de la Transposée ===")
    matrice_test = creer_matrice_test(3)
    afficher("Matrice de test 3x3 originale:")
    pour ligne dans matrice_test:
        afficher(ligne)

    transposee = transposer_matrice(matrice_test)
    afficher("Transposée:")
    pour ligne dans transposee:
        afficher(ligne)

    # Tester déterminant
    afficher("\n=== Test du Déterminant ===")
    det2 = determinant_2x2(a2)
    afficher(f"Det(2x2) = {det2}")

    det3 = determinant_3x3(matrice_test)
    afficher(f"Det(3x3) = {det3}")

    # Tester multiplication de matrices plus grandes
    afficher("\n=== Test de Multiplication de Matrices Plus Grandes ===")
    a_grand = creer_matrice_test(4)
    b_grand = creer_matrice_test(4)

    resultat_grand = multiplier_matrices(a_grand, b_grand)
    afficher(f"Multiplication matricielle 4x4 terminée. Première ligne: {resultat_grand[0]}")

    afficher("\n✓ Toutes les opérations matricielles ont été complétées avec succès")


principal()
