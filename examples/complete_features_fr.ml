importer math
depuis math importer sqrt comme root_fn
importer asyncio

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

# Numeric literals
soit nombre_hex = 0xFF
soit nombre_oct = 0o17
soit nombre_bin = 0b1010
soit nombre_sci = 1.5e3

# Augmented assignments
soit augmente = 10
augmente += 5
augmente -= 2
augmente *= 3
augmente //= 4
augmente %= 3

# Bitwise operators
soit bit_et = 0b1010 & 0b1100
soit bit_ou = 0b1010 | 0b0101
soit bit_xou = 0b1010 ^ 0b1111
soit bit_gauche = 1 << 3
soit bit_droite = 64 >> 2

# Chained assignment
soit chaine_a = chaine_b = chaine_c = 0

# Type annotations
soit typee: entier = 99

déf annotee(x: entier, y: flottant) -> chaine:
    retour chaine(x + y)

# Ternary expression
soit ternaire = "yes" si typee > 0 sinon "no"

# Default params, *args, **kwargs
déf multi_parametres(base, extra=1, *args, **kwargs):
    retour base + extra + somme(args)
soit resultat_multi = multi_parametres(10, 2, 3, 4, key=5)

# Lambda
soit carre = lambda x: x * x

# List/dict comprehensions and generator expression
soit liste_c = [x * 2 pour x dans intervalle(4)]
soit dico_c = {chaine(k): k * k pour k dans intervalle(3)}
soit gen_c = liste(x + 1 pour x dans intervalle(3))
soit imbrique_c = [i + j pour i dans intervalle(2) pour j dans intervalle(2)]
soit filtre_c = [x pour x dans intervalle(6) si x % 2 == 0]

# try/except/else
soit essai_sinon = 0
essayer:
    essai_sinon = entier("7")
sauf ValueError:
    essai_sinon = -1
sinon:
    essai_sinon += 1

# Exception chaining
soit enchainee = Faux
essayer:
    essayer:
        lever ValueError("v")
    sauf ValueError comme ve:
        lever RuntimeError("r") depuis ve
sauf RuntimeError:
    enchainee = Vrai

# Multiple except handlers
soit multi_exc_loc = 0
essayer:
    lever TypeError("t")
sauf ValueError:
    multi_exc_loc = 1
sauf TypeError:
    multi_exc_loc = 2

# Match/case with default
soit valeur_selon = 2
soit resultat_selon = "other"
selon valeur_selon:
    cas 1:
        resultat_selon = "one"
    cas 2:
        resultat_selon = "two"
    defaut:
        resultat_selon = "default"

# Decorator
déf doubleur(func):
    déf enveloppe(*args, **kwargs):
        retour func(*args, **kwargs) * 2
    retour enveloppe

@doubleur
déf dix():
    retour 10

soit resultat_deco = dix()

# Multiple inheritance, static/class methods, property
classe Melange:
    déf melange(self):
        retour 1

classe BaseDeux:
    déf __init__(self, start):
        self.value = start

classe Combine(BaseDeux, Melange):
    @staticmethod
    déf etiquette():
        retour "combined"
    @classmethod
    déf construire(cls, v):
        retour cls(v)
    @property
    déf doublee(self):
        retour self.value * 2

soit combine_obj = Combine.construire(3)
soit propriete = combine_obj.doublee

# Docstring
déf avec_doc():
    """A docstring."""
    retour Vrai

afficher(nombre_hex, nombre_oct, nombre_bin, nombre_sci)
afficher(augmente, bit_et, bit_ou, bit_xou, bit_gauche, bit_droite)
afficher(chaine_a, chaine_b, chaine_c)
afficher(typee, annotee(3, 1.5), ternaire)
afficher(resultat_multi, carre(5))
afficher(liste_c, dico_c, gen_c)
afficher(imbrique_c, filtre_c)
afficher(essai_sinon, enchainee, multi_exc_loc)
afficher(resultat_selon, resultat_deco, propriete)
afficher(avec_doc())

# Assignements augmentés binaires et puissance (v0.6.0)
soit bau_bits = 0b1111
bau_bits &= 0b1010
bau_bits |= 0b0100
bau_bits ^= 0b0011
bau_bits <<= 1
bau_bits >>= 2
soit puiss_aug = 2
puiss_aug **= 4

# Littéral d'octets (v0.6.0)
soit donnees_octets = b"bonjour"
soit taille_octets = longueur(donnees_octets)

# Concaténation, indexation et découpage de chaînes (v0.6.0)
soit chaine_x = "bonjour"
soit chaine_y = " monde"
soit concat_chaine = chaine_x + chaine_y
soit idx_chaine = chaine_x[1]
soit dec_chaine = chaine_x[1:3]

# Littéral de tuple (v0.6.0)
soit tuple_fr = (10, 20, 30)
soit elem_tuple_fr = tuple_fr[1]

# Boucle for sur variable de liste et compréhension de liste (v0.6.0)
soit liste_iter = [10, 20, 30]
soit somme_iter = 0
pour val_iter dans liste_iter:
    somme_iter = somme_iter + val_iter

soit liste_doub_src = [1, 2, 3, 4]
soit liste_doublee = [v * 2 pour v dans liste_doub_src]

# Correspondance étendue : chaîne, Rien, numérique et tuple (v0.6.0)
soit chaine_m = "bonjour"
soit result_chaine_m = "aucun"
selon chaine_m:
    cas "bonjour":
        result_chaine_m = "salut"
    cas "bonsoir":
        result_chaine_m = "bonne_nuit"
    defaut:
        result_chaine_m = "inconnu"

soit val_rien = Rien
soit result_rien = "défini"
selon val_rien:
    cas Rien:
        result_rien = "vide"
    defaut:
        result_rien = "autre"

soit val_num_m = 42
soit result_num_m = 0
selon val_num_m:
    cas 42:
        result_num_m = val_num_m
    defaut:
        result_num_m = 0

soit val_tuple_m = (1, 2)
soit result_tuple_m = "non"
selon val_tuple_m:
    cas (1, 2):
        result_tuple_m = "oui"
    defaut:
        result_tuple_m = "non"

# async def, await, async for, async with (v0.6.0)
asynchrone déf doubler_async(n):
    attendre asyncio.sleep(0)
    retour n * 2

asynchrone déf gen_async_fr():
    pour v dans range(3):
        produire v

asynchrone déf tache_async_pour():
    soit total_async = 0
    asynchrone pour av dans gen_async_fr():
        total_async = total_async + av
    retour total_async

classe ContexteAsyncFr:
    asynchrone déf __aenter__(self):
        retour 5
    asynchrone déf __aexit__(self, exc_type, exc, tb):
        retour Faux

asynchrone déf tache_async_avec():
    asynchrone avec ContexteAsyncFr() comme valeur:
        retour valeur

soit resultat_async = asyncio.run(doubler_async(5))
soit resultat_async_pour = asyncio.run(tache_async_pour())
soit resultat_async_avec = asyncio.run(tache_async_avec())

afficher(bau_bits, puiss_aug)
afficher(taille_octets)
afficher(concat_chaine, idx_chaine, dec_chaine)
afficher(elem_tuple_fr, somme_iter)
afficher(liste_doublee)
afficher(result_chaine_m, result_rien, result_num_m, result_tuple_m)
afficher(resultat_async, resultat_async_pour, resultat_async_avec)
