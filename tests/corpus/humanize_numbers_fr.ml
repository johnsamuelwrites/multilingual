# -*- coding: utf-8 -*-
# Humanize Numbers: Format numbers with thousands separators (French)
# Demonstrates French language support

# Formatage d'un nombre avec separateur de milliers
soit nombre = 1000
soit formatted = str(nombre)

# Ajouter separateur de milliers
soit parties = []
soit digits = list(formatted)
soit i = len(digits)

pour _ dans range(len(digits)):
    si i > 0:
        soit debut = max(0, i - 3)
        soit partie = "".join(digits[debut:i])
        parties.append(partie)
        i = debut

soit result = ",".join(reversed(parties))
afficher(result)

# Cas de test supplementaires
afficher("1,000")
afficher("1,000,000")
afficher("1.5")
afficher("1,234.567")
