importer math
depuis math importer sqrt comme root_fn

soit compteur_global = 3

def augmenter_global():
    global compteur_global
    compteur_global = compteur_global + 2
    retour compteur_global

def creer_compteur(depart):
    soit total = depart
    def etape():
        nonlocale total
        total = total + 1
        retour total
    retour etape

soit compteur_suivant = creer_compteur(5)
soit premiere = compteur_suivant()
soit deuxieme = compteur_suivant()

avec ouvrir("tmp_complete_fr.txt", "w", encoding="utf-8") comme ecriture:
    ecriture.write("ok")

soit texte_fichier = ""
avec ouvrir("tmp_complete_fr.txt", "r", encoding="utf-8") comme lecture:
    texte_fichier = lecture.read()

classe BoiteCompteur:
    def __init__(self, base):
        self.valeur = base

classe BoiteCompteurEnfant(BoiteCompteur):
    def __init__(self, base):
        superieur(BoiteCompteurEnfant, self).__init__(base)
        self.valeur = self.valeur + 1

def produire_trois():
    pour i dans intervalle(3):
        produire i

soit paires = list(fusionner([1, 2, 3], [4, 5, 6]))
soit uniques = ensemble([1, 1, 2, 3])
soit fixes = nuplet([10, 20, 30])
soit premier, *milieu, dernier = [1, 2, 3, 4]
soit fusionne = {**{"x": 1}, **{"y": 2}}

def etiquetter(a, /, *, b):
    retour f"{a}-{b:.1f}"

soit etiquette = etiquetter(7, b=3.5)
soit graine = 0
soit valeur_morsure = (graine := graine + 9)
soit total_produit = somme(produire_trois())
soit gere = Faux

essayer:
    si longueur(uniques) > 2:
        lever ValueError("boom")
sauf ValueError comme erreur_geree:
    gere = Vrai
finalement:
    soit racine = entier(root_fn(16))

soit temporaire = 99
supprimer temporaire

soit accum = 0
pour n dans intervalle(6):
    si n == 0:
        passer
    si n == 4:
        arrêter
    si n % 2 == 0:
        continuer
    accum = accum + n

soit drapeau_ok = Vrai et non Faux
affirmer drapeau_ok

soit enfant = BoiteCompteurEnfant(40)

afficher(augmenter_global())
afficher(premiere, deuxieme)
afficher(texte_fichier)
afficher(longueur(paires), longueur(uniques), fixes[1])
afficher(premier, milieu, dernier)
afficher(enfant.valeur)
afficher(total_produit, racine, gere)
afficher(fusionne["x"] + fusionne["y"], etiquette, valeur_morsure)
afficher(accum)
afficher(compteur_global est Rien)

