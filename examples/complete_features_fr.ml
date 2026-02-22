importer math
depuis math importer sqrt comme root_fn

soit compteur_partage = 3

déf augmenter_global():
    global compteur_partage
    compteur_partage = compteur_partage + 2
    retour compteur_partage

déf creer_compteur(depart):
    soit total = depart
    déf etape():
        nonlocale total
        total = total + 1
        retour total
    retour etape

soit compteur_suivant = creer_compteur(5)
soit premiere_etape = compteur_suivant()
soit deuxieme_etape = compteur_suivant()

avec ouvrir("tmp_complete_en.txt", "w", encoding="utf-8") comme poignee_ecriture:
    poignee_ecriture.write("ok")

soit texte_fichier = ""
avec ouvrir("tmp_complete_en.txt", "r", encoding="utf-8") comme poignee_lecture:
    texte_fichier = poignee_lecture.read()

soit paires_zippees = liste(fusionner([1, 2, 3], [4, 5, 6]))
soit valeurs_uniques = ensemble([1, 1, 2, 3])
soit valeurs_fixes = nuplet([10, 20, 30])
soit premier_element, *elements_milieu, dernier_element = [1, 2, 3, 4]
soit carte_fusionnee = {**{"x": 1}, **{"y": 2}}

déf etiquetter(a, /, *, b):
    retour f"{a}-{b:.1f}"

soit etiquette_formatee = etiquetter(7, b=3.5)
soit graine = 0
soit valeur_morsure = (graine := graine + 9)

classe BoiteCompteur:
    déf __init__(self, base_depart):
        self.valeur = base_depart

classe BoiteCompteurEnfant(BoiteCompteur):
    déf __init__(self, base_depart):
        superieur(BoiteCompteurEnfant, self).__init__(base_depart)
        self.valeur = self.valeur + 1

déf produire_trois():
    pour indice dans intervalle(3):
        produire indice

soit total_produit = somme(produire_trois())
soit gere = Faux

essayer:
    si longueur(valeurs_uniques) > 2:
        lever ValueError("boom")
sauf ValueError comme erreur_geree:
    gere = Vrai
finalement:
    soit valeur_racine = entier(root_fn(16))

soit valeur_temporaire = 99
supprimer valeur_temporaire

soit accum_boucle = 0
pour n dans intervalle(6):
    si n == 0:
        passer
    si n == 4:
        arrêter
    si n % 2 == 0:
        continuer
    accum_boucle = accum_boucle + n

soit drapeau_ok = Vrai et non Faux
affirmer drapeau_ok

soit boite_enfant = BoiteCompteurEnfant(40)

afficher(augmenter_global())
afficher(premiere_etape, deuxieme_etape)
afficher(texte_fichier)
afficher(longueur(paires_zippees), longueur(valeurs_uniques), valeurs_fixes[1])
afficher(premier_element, elements_milieu, dernier_element)
afficher(boite_enfant.valeur)
afficher(total_produit, valeur_racine, gere)
afficher(carte_fusionnee["x"] + carte_fusionnee["y"], etiquette_formatee, valeur_morsure)
afficher(accum_boucle)
afficher(compteur_partage est Rien)

# Loop else clauses
soit elements_trouves = Faux
pour element dans intervalle(3):
    si element == 10:
        elements_trouves = Vrai
        arrêter
sinon:
    elements_trouves = "not_found"

soit valeur_tantque_sinon = 0
tantque valeur_tantque_sinon < 2:
    valeur_tantque_sinon = valeur_tantque_sinon + 1
sinon:
    valeur_tantque_sinon = valeur_tantque_sinon + 10

# Starred unpacking variations
soit a, *reste = [10, 20, 30, 40]
soit *init, b = [10, 20, 30, 40]
soit c, *milieu, d = [10, 20, 30, 40]

# Set comprehension
soit ensemble_carres = {x * x pour x dans intervalle(5)}

# Extended builtins
soit resultat_puissance = puissance(2, 8)
soit resultat_divmod = divmod(17, 5)

# Yield from generator
déf gen_delegue():
    produire depuis intervalle(3)

soit delegue = liste(gen_delegue())

afficher(elements_trouves, valeur_tantque_sinon)
afficher(a, reste, init, b, c, milieu, d)
afficher(trier(ensemble_carres))
afficher(resultat_puissance, resultat_divmod)
afficher(delegue)
