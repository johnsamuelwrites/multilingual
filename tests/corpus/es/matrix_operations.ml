# Operaciones Matriciales - Proyecto WASM Corpus
# Variante española
#
# Demuestra:
# - Multiplicación matricial (cálculo intensivo, punto fuerte WASM)
# - Transposición de matriz
# - Cálculo de determinante
# - Operaciones sensibles al rendimiento

# SPDX-License-Identifier: GPL-3.0-or-later

función crear_matriz_identidad(n: entero) -> lista:
    """Crear una matriz identidad n×n."""
    resultado = []
    para i en rango(n):
        fila = []
        para j en rango(n):
            si i es j:
                fila.añadir(1)
            sino:
                fila.añadir(0)
        resultado.añadir(fila)
    retornar resultado


función crear_matriz_prueba(n: entero) -> lista:
    """Crear una matriz n×n con valores secuenciales."""
    resultado = []
    contador = 1
    para i en rango(n):
        fila = []
        para j en rango(n):
            fila.añadir(contador)
            contador = contador + 1
        resultado.añadir(fila)
    retornar resultado


función multiplicar_matrices(a: lista, b: lista) -> lista:
    """Multiplicar dos matrices.

    Argumentos:
        a: matriz m×n (lista de listas)
        b: matriz n×p (lista de listas)

    Retorna:
        matriz m×p resultante
    """
    m = longitud(a)
    n = longitud(a[0])
    p = longitud(b[0])

    resultado = []
    para i en rango(m):
        fila = []
        para j en rango(p):
            suma = 0
            para k en rango(n):
                suma = suma + (a[i][k] * b[k][j])
            fila.añadir(suma)
        resultado.añadir(fila)

    retornar resultado


función transponer_matriz(matriz: lista) -> lista:
    """Transponer una matriz (intercambiar filas y columnas)."""
    si longitud(matriz) es 0:
        retornar []

    filas = longitud(matriz)
    columnas = longitud(matriz[0])

    resultado = []
    para j en rango(columnas):
        fila = []
        para i en rango(filas):
            fila.añadir(matriz[i][j])
        resultado.añadir(fila)

    retornar resultado


función determinante_2x2(matriz: lista) -> número:
    """Calcular el determinante de una matriz 2×2."""
    retornar (matriz[0][0] * matriz[1][1]) - (matriz[0][1] * matriz[1][0])


función determinante_3x3(matriz: lista) -> número:
    """Calcular el determinante de una matriz 3×3 usando la regla de Sarrus."""
    a = matriz[0][0] * (matriz[1][1] * matriz[2][2] - matriz[1][2] * matriz[2][1])
    b = matriz[0][1] * (matriz[1][0] * matriz[2][2] - matriz[1][2] * matriz[2][0])
    c = matriz[0][2] * (matriz[1][0] * matriz[2][1] - matriz[1][1] * matriz[2][0])

    retornar a - b + c


función norma_frobenius(matriz: lista) -> número:
    """Calcular la norma de Frobenius (raíz de la suma de cuadrados)."""
    suma_cuadrados = 0
    para fila en matriz:
        para elemento en fila:
            suma_cuadrados = suma_cuadrados + (elemento * elemento)

    retornar suma_cuadrados ** 0.5


función principal():
    # Probar matrices 2×2
    imprimir("=== Prueba de Matrices 2x2 ===")
    a2 = [[1, 2], [3, 4]]
    b2 = [[5, 6], [7, 8]]

    resultado2 = multiplicar_matrices(a2, b2)
    imprimir("Resultado de la multiplicación 2x2:")
    para fila en resultado2:
        imprimir(fila)

    # Probar matriz identidad
    imprimir("\n=== Prueba de Matriz Identidad ===")
    identidad = crear_matriz_identidad(3)
    imprimir("Matriz identidad 3x3:")
    para fila en identidad:
        imprimir(fila)

    # Probar transposición
    imprimir("\n=== Prueba de Transposición ===")
    matriz_prueba = crear_matriz_prueba(3)
    imprimir("Matriz de prueba 3x3 original:")
    para fila en matriz_prueba:
        imprimir(fila)

    transpuesta = transponer_matriz(matriz_prueba)
    imprimir("Transpuesta:")
    para fila en transpuesta:
        imprimir(fila)

    # Probar determinante
    imprimir("\n=== Prueba de Determinante ===")
    det2 = determinante_2x2(a2)
    imprimir(f"Det(2x2) = {det2}")

    det3 = determinante_3x3(matriz_prueba)
    imprimir(f"Det(3x3) = {det3}")

    # Probar multiplicación de matrices más grandes
    imprimir("\n=== Prueba de Multiplicación de Matrices Más Grandes ===")
    a_grande = crear_matriz_prueba(4)
    b_grande = crear_matriz_prueba(4)

    resultado_grande = multiplicar_matrices(a_grande, b_grande)
    imprimir(f"Multiplicación matricial 4x4 completada. Primera fila: {resultado_grande[0]}")

    imprimir("\n✓ Todas las operaciones matriciales se completaron exitosamente")


principal()
