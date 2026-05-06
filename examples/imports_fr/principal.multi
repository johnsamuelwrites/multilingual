# Point d'entrée du package imports_fr.
# Démontre les imports absolus multi-niveaux depuis un point d'entrée externe.

depuis imports_fr.geometrie.formes importer Cercle, Rectangle
depuis imports_fr.geometrie.mesures importer calcul_surface, calcul_perimetre, comparer_surfaces
depuis imports_fr.statistiques.descriptif importer moyenne, ecart_type, surfaces_formes

# Créer des formes
soit c1 = Cercle(5.0)
soit c2 = Cercle(3.0)
soit r1 = Rectangle(4.0, 6.0)
soit r2 = Rectangle(2.0, 8.0)

afficher("=== Formes ===")
afficher(c1)
afficher(r1)

afficher("\n=== Mesures ===")
afficher(f"Surface {c1} : {calcul_surface(c1):.4f}")
afficher(f"Périmètre {c1} : {calcul_perimetre(c1):.4f}")
afficher(f"Surface {r1} : {calcul_surface(r1):.4f}")
afficher(f"Périmètre {r1} : {calcul_perimetre(r1):.4f}")

afficher("\n=== Comparaisons ===")
afficher(comparer_surfaces(c1, r1))
afficher(comparer_surfaces(c2, r2))

afficher("\n=== Statistiques sur les surfaces ===")
soit formes = [c1, c2, r1, r2]
soit surfaces = surfaces_formes(formes)
afficher(f"Surfaces : {[round(s, 4) pour s dans surfaces]}")
afficher(f"Moyenne  : {moyenne(surfaces):.4f}")
afficher(f"Écart-type : {ecart_type(surfaces):.4f}")
