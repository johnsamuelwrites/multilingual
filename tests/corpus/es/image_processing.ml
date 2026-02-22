# Procesamiento de Imágenes - Proyecto WASM Corpus
# Variante española
#
# Demuestra:
# - Filtros de imagen simples (desenfoque, detección de bordes)
# - Manipulación de píxeles
# - Transformación de imagen
# - Operaciones adecuadas para SIMD en WASM

# SPDX-License-Identifier: GPL-3.0-or-later

función crear_imagen_prueba(ancho: entero, alto: entero) -> lista:
    """Crear una imagen de prueba simple (valores de píxeles en escala de grises)."""
    imagen = []
    para y en rango(alto):
        fila = []
        para x en rango(ancho):
            # Crear un patrón de gradiente simple
            píxel = ((x + y) * 255) // (ancho + alto)
            fila.añadir(píxel)
        imagen.añadir(fila)
    retornar imagen


función filtro_desenfoque(imagen: lista, tamaño_kernel: entero) -> lista:
    """Aplicar un filtro de desenfoque simple."""
    alto = longitud(imagen)
    si alto es 0:
        retornar []

    ancho = longitud(imagen[0])
    resultado = []

    para y en rango(alto):
        fila = []
        para x en rango(ancho):
            # Calcular el promedio de los píxeles circundantes
            suma = 0
            cantidad = 0

            para dy en rango(-tamaño_kernel, tamaño_kernel + 1):
                para dx en rango(-tamaño_kernel, tamaño_kernel + 1):
                    ny = y + dy
                    nx = x + dx

                    si (ny >= 0) y (ny < alto) y (nx >= 0) y (nx < ancho):
                        suma = suma + imagen[ny][nx]
                        cantidad = cantidad + 1

            promediado = suma // cantidad si cantidad > 0 sino 0
            fila.añadir(promediado)

        resultado.añadir(fila)

    retornar resultado


función detección_bordes(imagen: lista) -> lista:
    """Detección de bordes Sobel simple."""
    alto = longitud(imagen)
    si alto < 3:
        retornar imagen

    ancho = longitud(imagen[0])
    si ancho < 3:
        retornar imagen

    resultado = []

    para y en rango(1, alto - 1):
        fila = []
        para x en rango(1, ancho - 1):
            # Operador Sobel simplificado
            gx = (imagen[y-1][x+1] + 2*imagen[y][x+1] + imagen[y+1][x+1]) - \
                 (imagen[y-1][x-1] + 2*imagen[y][x-1] + imagen[y+1][x-1])

            gy = (imagen[y+1][x-1] + 2*imagen[y+1][x] + imagen[y+1][x+1]) - \
                 (imagen[y-1][x-1] + 2*imagen[y-1][x] + imagen[y-1][x+1])

            # Calcular magnitud (simplificado)
            magnitud = (gx * gx + gy * gy) ** 0.5
            # Limitar a 0-255
            magnitud = entero(magnitud) si magnitud < 256 sino 255
            fila.añadir(magnitud)

        resultado.añadir(fila)

    retornar resultado


función escala_grises_a_binaria(imagen: lista, umbral: entero) -> lista:
    """Convertir imagen en escala de grises a binaria (blanco y negro)."""
    binaria = []
    para fila en imagen:
        fila_binaria = []
        para píxel en fila:
            valor_binario = 1 si píxel >= umbral sino 0
            fila_binaria.añadir(valor_binario)
        binaria.añadir(fila_binaria)
    retornar binaria


función invertir_colores(imagen: lista) -> lista:
    """Invertir colores (255 - píxel para cada píxel)."""
    invertida = []
    para fila en imagen:
        fila_invertida = []
        para píxel en fila:
            fila_invertida.añadir(255 - píxel)
        invertida.añadir(fila_invertida)
    retornar invertida


función calcular_histograma(imagen: lista) -> lista:
    """Calcular histograma (frecuencia de cada nivel de brillo)."""
    histograma = []
    para i en rango(256):
        histograma.añadir(0)

    para fila en imagen:
        para píxel en fila:
            si píxel >= 0 y píxel < 256:
                histograma[píxel] = histograma[píxel] + 1

    retornar histograma


función principal():
    # Crear imagen de prueba
    imprimir("=== Demostración de Procesamiento de Imágenes ===")
    imprimir("Creando imagen de prueba (8x8)...")
    imagen = crear_imagen_prueba(8, 8)
    imprimir(f"Imagen creada: {longitud(imagen)}x{longitud(imagen[0])}")

    # Mostrar imagen original
    imprimir("\nImagen original (primera fila):")
    imprimir(imagen[0])

    # Aplicar desenfoque
    imprimir("\n=== Aplicación del Filtro de Desenfoque ===")
    desenfocada = filtro_desenfoque(imagen, 1)
    imprimir("Imagen desenfocada (primera fila):")
    imprimir(desenfocada[0])

    # Detección de bordes
    imprimir("\n=== Aplicación de Detección de Bordes ===")
    bordes = detección_bordes(imagen)
    imprimir(f"Detección de bordes completada: {longitud(bordes)}x{longitud(bordes[0])}")
    imprimir("Mapa de bordes (primera fila):")
    imprimir(bordes[0])

    # Inversión de colores
    imprimir("\n=== Inversión de Colores ===")
    invertida = invertir_colores(imagen)
    imprimir("Imagen invertida (primera fila):")
    imprimir(invertida[0])

    # Conversión binaria
    imprimir("\n=== Conversión a Binario ===")
    binaria = escala_grises_a_binaria(imagen, 128)
    imprimir("Imagen binaria (primera fila):")
    imprimir(binaria[0])

    # Histograma
    imprimir("\n=== Cálculo del Histograma ===")
    hist = calcular_histograma(imagen)
    # Mostrar los primeros 10 buckets del histograma
    imprimir(f"Histograma (primeros 10 buckets): {hist[0:10]}")

    # Prueba de estrés: imagen grande
    imprimir("\n=== Prueba de Estrés: Procesamiento de Imagen Grande ===")
    imagen_grande = crear_imagen_prueba(32, 32)
    imprimir(f"Creada {longitud(imagen_grande)}x{longitud(imagen_grande[0])} imagen")

    desenfocada_grande = filtro_desenfoque(imagen_grande, 2)
    imprimir("Filtro de desenfoque aplicado a imagen grande")

    bordes_grandes = detección_bordes(imagen_grande)
    imprimir("Detección de bordes aplicada a imagen grande")

    imprimir("\n✓ Todas las operaciones de procesamiento de imágenes completadas exitosamente")


principal()
