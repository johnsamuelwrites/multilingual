# -*- coding: utf-8 -*-
# Aritmetica de fechas (corpus espanol)

desde datetime importar date, timedelta

def agregar_dias(d, dias):
    """Agregar dias a una fecha."""
    devolver d + timedelta(days=dias)

def restar_dias(d, dias):
    """Restar dias de una fecha."""
    devolver d - timedelta(days=dias)

def dias_entre(d1, d2):
    """Calcular dias entre dos fechas."""
    sea delta = d2 - d1
    devolver delta.days

def dias_en_anio(anio):
    """Contar dias en un anio."""
    sea inicio = date(anio, 1, 1)
    sea fin = date(anio, 12, 31)
    sea delta = fin - inicio
    devolver delta.days + 1

sea d1 = date(2023, 1, 1)
sea d2 = agregar_dias(d1, 9)
imprimir(d2)

sea d3 = date(2024, 1, 1)
sea d4 = restar_dias(d3, 12)
imprimir(d4)

sea dias = dias_entre(d1, d3)
imprimir(dias)

sea dias_anio = dias_en_anio(2023)
imprimir(dias_anio)
