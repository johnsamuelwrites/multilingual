# Traitement d'Images - Projet WASM Corpus
# Variante française
#
# Démontre:
# - Filtres d'image simples (flou, détection de contours)
# - Manipulation de pixels
# - Transformation d'image
# - Opérations compatibles SIMD pour WASM

# SPDX-License-Identifier: GPL-3.0-or-later

fonction créer_image_test(largeur: entier, hauteur: entier) -> liste:
    """Créer une image de test simple (valeurs de pixel en niveaux de gris)."""
    image = []
    pour y dans intervalle(hauteur):
        ligne = []
        pour x dans intervalle(largeur):
            # Créer un motif de gradient simple
            pixel = ((x + y) * 255) // (largeur + hauteur)
            ligne.ajouter(pixel)
        image.ajouter(ligne)
    retourne image


fonction flou_filtre(image: liste, taille_kernel: entier) -> liste:
    """Appliquer un filtre de flou simple."""
    hauteur = longueur(image)
    si hauteur est 0:
        retourne []

    largeur = longueur(image[0])
    resultat = []

    pour y dans intervalle(hauteur):
        ligne = []
        pour x dans intervalle(largeur):
            # Calculer la moyenne des pixels environnants
            somme = 0
            count = 0

            pour dy dans intervalle(-taille_kernel, taille_kernel + 1):
                pour dx dans intervalle(-taille_kernel, taille_kernel + 1):
                    ny = y + dy
                    nx = x + dx

                    si (ny >= 0) et (ny < hauteur) et (nx >= 0) et (nx < largeur):
                        somme = somme + image[ny][nx]
                        count = count + 1

            moyenné = somme // count si count > 0 sinon 0
            ligne.ajouter(moyenné)

        resultat.ajouter(ligne)

    retourne resultat


fonction détection_contours(image: liste) -> liste:
    """Détection de contours Sobel simple."""
    hauteur = longueur(image)
    si hauteur < 3:
        retourne image

    largeur = longueur(image[0])
    si largeur < 3:
        retourne image

    resultat = []

    pour y dans intervalle(1, hauteur - 1):
        ligne = []
        pour x dans intervalle(1, largeur - 1):
            # Opérateur Sobel simplifié
            gx = (image[y-1][x+1] + 2*image[y][x+1] + image[y+1][x+1]) - \
                 (image[y-1][x-1] + 2*image[y][x-1] + image[y+1][x-1])

            gy = (image[y+1][x-1] + 2*image[y+1][x] + image[y+1][x+1]) - \
                 (image[y-1][x-1] + 2*image[y-1][x] + image[y-1][x+1])

            # Calculer la magnitude (simplifié)
            magnitude = (gx * gx + gy * gy) ** 0.5
            # Écrêter à 0-255
            magnitude = entier(magnitude) si magnitude < 256 sinon 255
            ligne.ajouter(magnitude)

        resultat.ajouter(ligne)

    retourne resultat


fonction niveaux_gris_en_binaire(image: liste, seuil: entier) -> liste:
    """Convertir l'image en niveaux de gris en binaire (noir et blanc)."""
    binaire = []
    pour ligne dans image:
        ligne_binaire = []
        pour pixel dans ligne:
            val_binaire = 1 si pixel >= seuil sinon 0
            ligne_binaire.ajouter(val_binaire)
        binaire.ajouter(ligne_binaire)
    retourne binaire


fonction inverser_couleurs(image: liste) -> liste:
    """Inverser les couleurs (255 - pixel pour chaque pixel)."""
    inversée = []
    pour ligne dans image:
        ligne_inversée = []
        pour pixel dans ligne:
            ligne_inversée.ajouter(255 - pixel)
        inversée.ajouter(ligne_inversée)
    retourne inversée


fonction calculer_histogramme(image: liste) -> liste:
    """Calculer l'histogramme (fréquence de chaque niveau de luminosité)."""
    histogramme = []
    pour i dans intervalle(256):
        histogramme.ajouter(0)

    pour ligne dans image:
        pour pixel dans ligne:
            si pixel >= 0 et pixel < 256:
                histogramme[pixel] = histogramme[pixel] + 1

    retourne histogramme


fonction principal():
    # Créer image de test
    afficher("=== Démonstration du Traitement d'Images ===")
    afficher("Création d'une image de test (8x8)...")
    image = créer_image_test(8, 8)
    afficher(f"Image créée: {longueur(image)}x{longueur(image[0])}")

    # Afficher l'image originale
    afficher("\nImage originale (première ligne):")
    afficher(image[0])

    # Appliquer le flou
    afficher("\n=== Application du Filtre de Flou ===")
    floutée = flou_filtre(image, 1)
    afficher("Image floutée (première ligne):")
    afficher(floutée[0])

    # Détection de contours
    afficher("\n=== Application de la Détection de Contours ===")
    contours = détection_contours(image)
    afficher(f"Détection de contours complétée: {longueur(contours)}x{longueur(contours[0])}")
    afficher("Carte de contours (première ligne):")
    afficher(contours[0])

    # Inversion de couleurs
    afficher("\n=== Inversion des Couleurs ===")
    inversée = inverser_couleurs(image)
    afficher("Image inversée (première ligne):")
    afficher(inversée[0])

    # Conversion binaire
    afficher("\n=== Conversion en Binaire ===")
    binaire = niveaux_gris_en_binaire(image, 128)
    afficher("Image binaire (première ligne):")
    afficher(binaire[0])

    # Histogramme
    afficher("\n=== Calcul de l'Histogramme ===")
    hist = calculer_histogramme(image)
    # Afficher les 10 premiers buckets d'histogramme
    afficher(f"Histogramme (10 premiers buckets): {hist[0:10]}")

    # Test de charge: grande image
    afficher("\n=== Test de Charge: Traitement d'une Grande Image ===")
    grande_image = créer_image_test(32, 32)
    afficher(f"Créée {longueur(grande_image)}x{longueur(grande_image[0])} image")

    floutée_grande = flou_filtre(grande_image, 2)
    afficher("Filtre de flou appliqué à la grande image")

    contours_grands = détection_contours(grande_image)
    afficher("Détection de contours appliquée à la grande image")

    afficher("\n✓ Toutes les opérations de traitement d'images complétées avec succès")


principal()
