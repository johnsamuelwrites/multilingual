# -*- coding: utf-8 -*-
# Arithmetic de dates (corpus francais)

depuis datetime importer date, timedelta

def ajouter_jours(d, jours):
    """Ajouter des jours a une date."""
    retour d + timedelta(days=jours)

def soustraire_jours(d, jours):
    """Soustraire des jours d'une date."""
    retour d - timedelta(days=jours)

def jours_entre(d1, d2):
    """Calculer le nombre de jours entre deux dates."""
    soit delta = d2 - d1
    retour delta.days

def jours_dans_annee(annee):
    """Compter les jours dans une annee."""
    soit debut = date(annee, 1, 1)
    soit fin = date(annee, 12, 31)
    soit delta = fin - debut
    retour delta.days + 1

soit d1 = date(2023, 1, 1)
soit d2 = ajouter_jours(d1, 9)
afficher(d2)

soit d3 = date(2024, 1, 1)
soit d4 = soustraire_jours(d3, 12)
afficher(d4)

soit jours = jours_entre(d1, d3)
afficher(jours)

soit jours_annee = jours_dans_annee(2023)
afficher(jours_annee)
