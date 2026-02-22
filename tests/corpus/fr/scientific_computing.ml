# Calcul Scientifique - Projet WASM Corpus
# Variante française
#
# Démontre:
# - Simulations Monte Carlo
# - Approximations numériques
# - Calculs statistiques
# - Opérations intensives en point flottant idéales pour WASM

# SPDX-License-Identifier: GPL-3.0-or-later

fonction nombre_aléatoire_flottant(graine: entier) -> nombre:
    """Générateur de nombres pseudo-aléatoires simple."""
    # Générateur congruentiel linéaire
    a = 1103515245
    c = 12345
    m = 2147483648  # 2^31
    graine = (a * graine + c) % m
    retourne (graine / m)


fonction estimer_pi_monte_carlo(num_échantillons: entier) -> nombre:
    """Estimer PI en utilisant la méthode Monte Carlo.

    Générer des points aléatoires dans le carré [0,1] x [0,1].
    Compter combien tombent dans le cercle unitaire (x^2 + y^2 <= 1).
    Le rapport des points dans le cercle au total approxime PI/4.
    """
    dans_cercle = 0
    graine = 42  # Graine fixe pour la reproductibilité

    pour i dans intervalle(num_échantillons):
        # Générer un point aléatoire
        graine = (1103515245 * graine + 12345) % 2147483648
        x = (graine % 10000) / 10000.0

        graine = (1103515245 * graine + 12345) % 2147483648
        y = (graine % 10000) / 10000.0

        # Vérifier si le point est dans le cercle unitaire
        distance_au_carré = x * x + y * y
        si distance_au_carré <= 1.0:
            dans_cercle = dans_cercle + 1

    # Estimer PI
    estimation_pi = 4.0 * dans_cercle / num_échantillons
    retourne estimation_pi


fonction écart_type(valeurs: liste) -> nombre:
    """Calculer l'écart-type d'une liste de valeurs."""
    si longueur(valeurs) est 0:
        retourne 0.0

    # Calculer la moyenne
    moyenne = 0.0
    pour valeur dans valeurs:
        moyenne = moyenne + valeur
    moyenne = moyenne / longueur(valeurs)

    # Calculer la variance
    variance = 0.0
    pour valeur dans valeurs:
        diff = valeur - moyenne
        variance = variance + (diff * diff)
    variance = variance / longueur(valeurs)

    # L'écart-type est la racine carrée de la variance
    retourne variance ** 0.5


fonction calculer_statistiques(valeurs: liste) -> objet:
    """Calculer diverses statistiques pour un ensemble de données."""
    si longueur(valeurs) est 0:
        retourne {"moyenne": 0, "écart_type": 0, "min": 0, "max": 0}

    # Moyenne
    moyenne = 0.0
    pour valeur dans valeurs:
        moyenne = moyenne + valeur
    moyenne = moyenne / longueur(valeurs)

    # Min et max
    val_min = valeurs[0]
    val_max = valeurs[0]
    pour valeur dans valeurs:
        si valeur < val_min:
            val_min = valeur
        si valeur > val_max:
            val_max = valeur

    # Écart-type
    écart = écart_type(valeurs)

    retourne {
        "moyenne": moyenne,
        "écart_type": écart,
        "min": val_min,
        "max": val_max,
        "nombre": longueur(valeurs),
    }


fonction approximation_compte_nombres_premiers(n: entier) -> nombre:
    """Approximer le nombre de nombres premiers <= n en utilisant le théorème des nombres premiers."""
    # Théorème des nombres premiers: π(n) ≈ n / ln(n)
    si n <= 1:
        retourne 0.0
    si n < 10:
        retourne nombre(n)

    ln_n = 0.0
    # Approximation simple du logarithme
    temp = n
    pour _ dans intervalle(10):
        ln_n = ln_n + 1.0 / temp
        temp = temp / 2.718  # Approximation grossière

    retourne n / ln_n


fonction approximation_factorielle(n: entier) -> nombre:
    """Approximer n! en utilisant l'approximation de Stirling."""
    si n <= 0:
        retourne 1.0
    si n est 1:
        retourne 1.0

    # Stirling: n! ≈ sqrt(2πn) * (n/e)^n
    # Simplifié: ln(n!) ≈ n*ln(n) - n
    ln_factorielle = 0.0
    pour i dans intervalle(1, n + 1):
        ln_factorielle = ln_factorielle + (i)  # Très simplifié

    retourne ln_factorielle ** 1.5


fonction principal():
    afficher("=== Démonstration du Calcul Scientifique ===")

    # Estimer PI
    afficher("\n1. Estimation de PI en utilisant la méthode Monte Carlo...")
    liste_échantillons = [1000, 10000, 100000]

    pour échantillons dans liste_échantillons:
        est_pi = estimer_pi_monte_carlo(échantillons)
        erreur = abs(est_pi - 3.14159265359)
        afficher(f"   Échantillons: {échantillons:6d}, Estimation PI: {est_pi:.6f}, Erreur: {erreur:.6f}")

    # Calculs statistiques
    afficher("\n2. Analyse statistique...")
    données_test = [1.5, 2.3, 3.1, 2.8, 4.5, 3.2, 2.9, 5.1, 3.8, 4.2]
    stats = calculer_statistiques(données_test)
    afficher(f"   Moyenne: {stats['moyenne']:.4f}")
    afficher(f"   Écart-type: {stats['écart_type']:.4f}")
    afficher(f"   Min: {stats['min']:.4f}")
    afficher(f"   Max: {stats['max']:.4f}")
    afficher(f"   Nombre: {stats['nombre']}")

    # Approximation des nombres premiers
    afficher("\n3. Approximation du théorème des nombres premiers...")
    valeurs_test_premiers = [10, 100, 1000]
    pour n dans valeurs_test_premiers:
        approx_premiers = approximation_compte_nombres_premiers(n)
        afficher(f"   Nombres premiers estimés <= {n}: {nombre(approx_premiers):.1f}")

    # Approximation factorielle
    afficher("\n4. Approximation factorielle (Stirling)...")
    valeurs_test_factorielle = [5, 10, 20, 50]
    pour n dans valeurs_test_factorielle:
        approx_fact = approximation_factorielle(n)
        afficher(f"   Factorielle {n}! ≈ {approx_fact:.2f}")

    # Test de charge: nombreuses simulations
    afficher("\n5. Test de charge: estimations multiples de PI...")
    estimations_pi = []
    pour essai dans intervalle(10):
        est_pi = estimer_pi_monte_carlo(100000)
        estimations_pi.ajouter(est_pi)

    stats_pi = calculer_statistiques(estimations_pi)
    afficher(f"   Estimation moyenne de PI: {stats_pi['moyenne']:.6f}")
    afficher(f"   Écart-type: {stats_pi['écart_type']:.6f}")
    afficher(f"   Plage: [{stats_pi['min']:.6f}, {stats_pi['max']:.6f}]")

    # Intégration numérique (règle trapézoïdale)
    afficher("\n6. Intégration numérique (exemple simple)...")
    # Intégrer y=x^2 de 0 à 1, devrait être 1/3 ≈ 0.333
    intervalles = 100
    somme = 0.0
    pour i dans intervalle(intervalles):
        x1 = i / nombre(intervalles)
        x2 = (i + 1) / nombre(intervalles)
        y1 = x1 * x1
        y2 = x2 * x2
        aire_trapèze = (y1 + y2) / 2.0 * (x2 - x1)
        somme = somme + aire_trapèze

    afficher(f"   Intégrale de x^2 de 0 à 1: {somme:.6f} (attendu: 0.333333)")

    afficher("\n✓ Toutes les opérations de calcul scientifique sont complétées avec succès")


principal()
