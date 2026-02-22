# -*- coding: utf-8 -*-
# Humanize Numbers: format numbers with thousands separators (French corpus)

def format_nombre(n, separateur):
    """Formater un nombre avec separateur de milliers."""
    si n == 0:
        retour "0"

    si n < 0:
        retour "-" + format_nombre(-n, separateur)

    soit n_str = str(entier(n))
    soit parties = []
    soit i = longueur(n_str)
    tantque i > 0:
        soit debut = max(0, i - 3)
        parties.append(n_str[debut:i])
        i = debut

    soit partie_entiere = ""
    si separateur:
        partie_entiere = ",".join(reversed(parties))
    sinon:
        partie_entiere = "".join(reversed(parties))

    soit decimale = n - entier(n)
    si decimale > 0:
        soit frac_str = str(n)
        soit dot_idx = frac_str.find(".")
        si dot_idx >= 0:
            soit partie_decimale = frac_str[dot_idx + 1:]
            retour partie_entiere + "." + partie_decimale

    retour partie_entiere

afficher(format_nombre(1000, Vrai))
afficher(format_nombre(1000, Vrai))
afficher(format_nombre(1000000, Vrai))
afficher(format_nombre(1.5, Vrai))
afficher(format_nombre(1234.567, Vrai))
