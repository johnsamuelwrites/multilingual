# -*- coding: utf-8 -*-
# Humanize Numbers: Format numbers with thousands separators (French)
# Mimics humanize library number formatting

def format_nombre(n, use_separator=True):
    if n == 0:
        return "0"

    # Gerer negatif
    if n < 0:
        return "-" + format_nombre(-n, use_separator)

    # Convertir en chaine
    let n_str = str(int(n))
    let parties = []

    # Ajouter separateurs de milliers
    let i = len(n_str)
    while i > 0:
        let debut = max(0, i - 3)
        parties.append(n_str[debut:i])
        i = debut

    if use_separator:
        let partie_entiere = ",".join(reversed(parties))
    else:
        let partie_entiere = "".join(reversed(parties))

    # Gerer partie decimale
    let val_decimal = n - int(n)
    if val_decimal > 0:
        let frac_str = str(n)
        let dot_idx = frac_str.find(".")
        if dot_idx >= 0:
            let decimal_part = frac_str[dot_idx + 1:]
            return partie_entiere + "." + decimal_part

    return partie_entiere

# Cas de test
print(format_nombre(1000, True))
print(format_nombre(1000, True))
print(format_nombre(1000000, True))
print(format_nombre(1.5, True))
print(format_nombre(1234.567, True))
