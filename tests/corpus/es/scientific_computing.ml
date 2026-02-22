# Computación Científica - Proyecto WASM Corpus
# Variante española
#
# Demuestra:
# - Simulaciones Monte Carlo
# - Aproximaciones numéricas
# - Cálculos estadísticos
# - Operaciones intensivas en punto flotante ideales para WASM

# SPDX-License-Identifier: GPL-3.0-or-later

función número_flotante_aleatorio(semilla: entero) -> número:
    """Generador de números pseudoaleatorios simple."""
    # Generador congruencial lineal
    a = 1103515245
    c = 12345
    m = 2147483648  # 2^31
    semilla = (a * semilla + c) % m
    retornar (semilla / m)


función estimar_pi_monte_carlo(num_muestras: entero) -> número:
    """Estimar PI usando el método Monte Carlo.

    Generar puntos aleatorios en el cuadrado [0,1] x [0,1].
    Contar cuántos caen en el círculo unitario (x^2 + y^2 <= 1).
    La razón de puntos en el círculo al total aproxima PI/4.
    """
    dentro_círculo = 0
    semilla = 42  # Semilla fija para reproducibilidad

    para i en rango(num_muestras):
        # Generar punto aleatorio
        semilla = (1103515245 * semilla + 12345) % 2147483648
        x = (semilla % 10000) / 10000.0

        semilla = (1103515245 * semilla + 12345) % 2147483648
        y = (semilla % 10000) / 10000.0

        # Verificar si el punto está dentro del círculo unitario
        distancia_al_cuadrado = x * x + y * y
        si distancia_al_cuadrado <= 1.0:
            dentro_círculo = dentro_círculo + 1

    # Estimar PI
    estimación_pi = 4.0 * dentro_círculo / num_muestras
    retornar estimación_pi


función desviación_estándar(valores: lista) -> número:
    """Calcular la desviación estándar de una lista de valores."""
    si longitud(valores) es 0:
        retornar 0.0

    # Calcular la media
    media = 0.0
    para valor en valores:
        media = media + valor
    media = media / longitud(valores)

    # Calcular la varianza
    varianza = 0.0
    para valor en valores:
        diferencia = valor - media
        varianza = varianza + (diferencia * diferencia)
    varianza = varianza / longitud(valores)

    # La desviación estándar es la raíz cuadrada de la varianza
    retornar varianza ** 0.5


función calcular_estadísticas(valores: lista) -> objeto:
    """Calcular varias estadísticas para un conjunto de datos."""
    si longitud(valores) es 0:
        retornar {"media": 0, "desv_est": 0, "mín": 0, "máx": 0}

    # Media
    media = 0.0
    para valor en valores:
        media = media + valor
    media = media / longitud(valores)

    # Mín y máx
    val_mín = valores[0]
    val_máx = valores[0]
    para valor en valores:
        si valor < val_mín:
            val_mín = valor
        si valor > val_máx:
            val_máx = valor

    # Desviación estándar
    desv_est = desviación_estándar(valores)

    retornar {
        "media": media,
        "desv_est": desv_est,
        "mín": val_mín,
        "máx": val_máx,
        "cantidad": longitud(valores),
    }


función aproximación_conteo_primos(n: entero) -> número:
    """Aproximar el número de primos <= n usando el teorema de números primos."""
    # Teorema de números primos: π(n) ≈ n / ln(n)
    si n <= 1:
        retornar 0.0
    si n < 10:
        retornar número(n)

    ln_n = 0.0
    # Aproximación simple de logaritmo
    temp = n
    para _ en rango(10):
        ln_n = ln_n + 1.0 / temp
        temp = temp / 2.718  # Aproximación muy gruesa

    retornar n / ln_n


función aproximación_factorial(n: entero) -> número:
    """Aproximar n! usando la aproximación de Stirling."""
    si n <= 0:
        retornar 1.0
    si n es 1:
        retornar 1.0

    # Stirling: n! ≈ sqrt(2πn) * (n/e)^n
    # Simplificado: ln(n!) ≈ n*ln(n) - n
    ln_factorial = 0.0
    para i en rango(1, n + 1):
        ln_factorial = ln_factorial + (i)  # Muy simplificado

    retornar ln_factorial ** 1.5


función principal():
    imprimir("=== Demostración de Computación Científica ===")

    # Estimar PI
    imprimir("\n1. Estimación de PI usando método Monte Carlo...")
    lista_muestras = [1000, 10000, 100000]

    para muestras en lista_muestras:
        est_pi = estimar_pi_monte_carlo(muestras)
        error = abs(est_pi - 3.14159265359)
        imprimir(f"   Muestras: {muestras:6d}, Estimación PI: {est_pi:.6f}, Error: {error:.6f}")

    # Cálculos estadísticos
    imprimir("\n2. Análisis estadístico...")
    datos_prueba = [1.5, 2.3, 3.1, 2.8, 4.5, 3.2, 2.9, 5.1, 3.8, 4.2]
    stats = calcular_estadísticas(datos_prueba)
    imprimir(f"   Media: {stats['media']:.4f}")
    imprimir(f"   Desv. Est.: {stats['desv_est']:.4f}")
    imprimir(f"   Mín: {stats['mín']:.4f}")
    imprimir(f"   Máx: {stats['máx']:.4f}")
    imprimir(f"   Cantidad: {stats['cantidad']}")

    # Aproximación de números primos
    imprimir("\n3. Aproximación del teorema de números primos...")
    valores_prueba_primos = [10, 100, 1000]
    para n en valores_prueba_primos:
        aprox_primos = aproximación_conteo_primos(n)
        imprimir(f"   Primos estimados <= {n}: {número(aprox_primos):.1f}")

    # Aproximación factorial
    imprimir("\n4. Aproximación factorial (Stirling)...")
    valores_prueba_factorial = [5, 10, 20, 50]
    para n en valores_prueba_factorial:
        aprox_fact = aproximación_factorial(n)
        imprimir(f"   Factorial {n}! ≈ {aprox_fact:.2f}")

    # Prueba de estrés: múltiples simulaciones
    imprimir("\n5. Prueba de estrés: estimaciones múltiples de PI...")
    estimaciones_pi = []
    para ensayo en rango(10):
        est_pi = estimar_pi_monte_carlo(100000)
        estimaciones_pi.añadir(est_pi)

    stats_pi = calcular_estadísticas(estimaciones_pi)
    imprimir(f"   Estimación media de PI: {stats_pi['media']:.6f}")
    imprimir(f"   Desv. Est.: {stats_pi['desv_est']:.6f}")
    imprimir(f"   Rango: [{stats_pi['mín']:.6f}, {stats_pi['máx']:.6f}]")

    # Integración numérica (regla trapezoidal)
    imprimir("\n6. Integración numérica (ejemplo simple)...")
    # Integrar y=x^2 de 0 a 1, debería ser 1/3 ≈ 0.333
    intervalos = 100
    suma = 0.0
    para i en rango(intervalos):
        x1 = i / número(intervalos)
        x2 = (i + 1) / número(intervalos)
        y1 = x1 * x1
        y2 = x2 * x2
        área_trapecio = (y1 + y2) / 2.0 * (x2 - x1)
        suma = suma + área_trapecio

    imprimir(f"   Integral de x^2 de 0 a 1: {suma:.6f} (esperado: 0.333333)")

    imprimir("\n✓ Todas las operaciones de computación científica completadas exitosamente")


principal()
