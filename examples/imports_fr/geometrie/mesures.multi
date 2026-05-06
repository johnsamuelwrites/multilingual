# Import relatif depuis le même package (geometrie)
depuis . importer formes


déf calcul_perimetre(forme) -> flottant:
    retour forme.perimetre()


déf calcul_surface(forme) -> flottant:
    retour forme.surface()


déf comparer_surfaces(forme_a, forme_b) -> chaine:
    soit sa = calcul_surface(forme_a)
    soit sb = calcul_surface(forme_b)
    si sa > sb:
        retour f"{forme_a} est plus grande que {forme_b}"
    sinon si sa < sb:
        retour f"{forme_a} est plus petite que {forme_b}"
    sinon:
        retour f"{forme_a} et {forme_b} ont la même surface"
