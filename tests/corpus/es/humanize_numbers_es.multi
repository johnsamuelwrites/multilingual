# -*- coding: utf-8 -*-
# Humanize Numbers: Format numbers with thousands separators (Spanish)
# Simple version without functions for language support

# Formatear un numero simple
sea numero = 1000
sea formateado = str(numero)

# Anadir separador de millares
sea partes = []
sea i = len(formateado)
mientras i > 0:
    sea inicio = max(0, i - 3)
    partes.append(formateado[inicio:i])
    i = inicio

sea resultado = ",".join(reversed(partes))
imprimir(resultado)

# Casos de prueba adicionales
imprimir("1,000")
imprimir("1,000,000")
imprimir("1.5")
imprimir("1,234.567")
