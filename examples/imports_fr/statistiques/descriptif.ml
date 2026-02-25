importer math

# Import relatif depuis le package parent (imports_fr) vers un sous-package
depuis ..geometrie importer Cercle, Rectangle, calcul_surface


déf moyenne(valeurs: liste) -> flottant:
    si longueur(valeurs) == 0:
        lever ValueError("liste vide")
    retour somme(valeurs) / longueur(valeurs)


déf variance(valeurs: liste) -> flottant:
    si longueur(valeurs) == 0:
        lever ValueError("liste vide")
    soit moy = moyenne(valeurs)
    soit ecarts = [(x - moy) * (x - moy) pour x dans valeurs]
    retour somme(ecarts) / longueur(valeurs)


déf ecart_type(valeurs: liste) -> flottant:
    retour math.sqrt(variance(valeurs))


déf surfaces_formes(formes: liste) -> liste:
    retour [calcul_surface(f) pour f dans formes]
