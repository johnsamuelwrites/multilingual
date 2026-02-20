importer math
depuis math importer sqrt comme root_fn

soit total_acc = 0
soit nombres = [1, 2, 3, 4]

pour element dans nombres:
    total_acc = total_acc + element

soit compteur = 0
tantque compteur < 2:
    compteur = compteur + 1
    total_acc = total_acc + compteur

déf ajuster_valeur(valeur):
    si valeur > 5:
        retour valeur - 1
    sinon:
        retour valeur + 1

soit ajustes = [ajuster_valeur(item) pour item dans nombres si item > 2]
soit drapeau_ok = Vrai et non Faux
affirmer drapeau_ok

essayer:
    soit racine = root_fn(16)
sauf Exception comme erreur_geree:
    soit racine = 0
finalement:
    total_acc = total_acc + int(racine)

classe BoiteCompteur:
    déf __init__(self, depart):
        self.valeur = depart

    déf incrementer(self):
        self.valeur = self.valeur + 1
        retour self.valeur

soit boite = BoiteCompteur(total_acc)
soit valeur_incrementee = boite.incrementer()

afficher(total_acc)
afficher(longueur(ajustes))
afficher(valeur_incrementee)
afficher(total_acc est Rien)
