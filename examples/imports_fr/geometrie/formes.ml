importer math

classe Cercle:
    déf __init__(soi, rayon: flottant):
        soi.rayon = rayon

    déf surface(soi) -> flottant:
        retour math.pi * soi.rayon * soi.rayon

    déf perimetre(soi) -> flottant:
        retour 2 * math.pi * soi.rayon

    déf __repr__(soi) -> chaine:
        retour f"Cercle(rayon={soi.rayon})"


classe Rectangle:
    déf __init__(soi, largeur: flottant, hauteur: flottant):
        soi.largeur = largeur
        soi.hauteur = hauteur

    déf surface(soi) -> flottant:
        retour soi.largeur * soi.hauteur

    déf perimetre(soi) -> flottant:
        retour 2 * (soi.largeur + soi.hauteur)

    déf __repr__(soi) -> chaine:
        retour f"Rectangle(largeur={soi.largeur}, hauteur={soi.hauteur})"
