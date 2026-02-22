# -*- coding: utf-8 -*-
# Humanize Numbers: Format numbers with thousands separators (Spanish)
# Mimics humanize library number formatting

def formato_numero(n, use_separator=True):
    if n == 0:
        return "0"

    # Manejar negativo
    if n < 0:
        return "-" + formato_numero(-n, use_separator)

    # Convertir a cadena
    let n_str = str(int(n))
    let partes = []

    # Anadir separadores de millares
    let i = len(n_str)
    while i > 0:
        let inicio = max(0, i - 3)
        partes.append(n_str[inicio:i])
        i = inicio

    if use_separator:
        let parte_entera = ",".join(reversed(partes))
    else:
        let parte_entera = "".join(reversed(partes))

    # Manejar parte decimal
    let valor_decimal = n - int(n)
    if valor_decimal > 0:
        let frac_str = str(n)
        let dot_idx = frac_str.find(".")
        if dot_idx >= 0:
            let decimal_part = frac_str[dot_idx + 1:]
            return parte_entera + "." + decimal_part

    return parte_entera

# Casos de prueba
print(formato_numero(1000, True))
print(formato_numero(1000, True))
print(formato_numero(1000000, True))
print(formato_numero(1.5, True))
print(formato_numero(1234.567, True))
