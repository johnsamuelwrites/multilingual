# -*- coding: utf-8 -*-
# Factorielle recursive (corpus francais)

def factorielle(n):
    si n <= 1:
        retour 1
    retour n * factorielle(n - 1)

afficher(factorielle(5))
afficher(factorielle(6))
afficher(factorielle(7))
