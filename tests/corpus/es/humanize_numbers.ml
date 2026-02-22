# -*- coding: utf-8 -*-
# Humanize Numbers: format numbers with thousands separators (Spanish corpus)

def formatear_numero(n, separador):
    """Formatear un numero con separador de miles."""
    si n == 0:
        devolver "0"

    si n < 0:
        devolver "-" + formatear_numero(-n, separador)

    sea n_str = str(entero(n))
    sea partes = []
    sea i = longitud(n_str)
    mientras i > 0:
        sea inicio = max(0, i - 3)
        partes.append(n_str[inicio:i])
        i = inicio

    sea parte_entera = ""
    si separador:
        parte_entera = ",".join(reversed(partes))
    sino:
        parte_entera = "".join(reversed(partes))

    sea decimal = n - entero(n)
    si decimal > 0:
        sea frac_str = str(n)
        sea dot_idx = frac_str.find(".")
        si dot_idx >= 0:
            sea parte_decimal = frac_str[dot_idx + 1:]
            devolver parte_entera + "." + parte_decimal

    devolver parte_entera

imprimir(formatear_numero(1000, Verdadero))
imprimir(formatear_numero(1000, Verdadero))
imprimir(formatear_numero(1000000, Verdadero))
imprimir(formatear_numero(1.5, Verdadero))
imprimir(formatear_numero(1234.567, Verdadero))
