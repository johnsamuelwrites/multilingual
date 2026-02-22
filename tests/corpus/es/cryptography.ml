# Criptografía - Proyecto WASM Corpus
# Variante española
#
# Demuestra:
# - Cifrado de sustitución simple (basado en XOR)
# - Función de hachage (simple pero determinista)
# - Verificación de contraseña
# - Operaciones computacionalmente intensivas ideales para WASM

# SPDX-License-Identifier: GPL-3.0-or-later

función hash_simple(texto: cadena) -> entero:
    """Función hash simple (no criptográficamente segura, solo para demo)."""
    valor_hash = 0
    para carácter en texto:
        valor_hash = ((valor_hash << 5) - valor_hash) + ord(carácter)
        valor_hash = valor_hash & 0xFFFFFFFF  # Mantener como 32-bit
    retornar valor_hash


función cifrar_xor(texto_plano: cadena, clave: cadena) -> cadena:
    """Cifrado XOR simple (no seguro, solo para demostración)."""
    resultado = []
    para i en rango(longitud(texto_plano)):
        carácter_clave = clave[i % longitud(clave)]
        carácter_cifrado = chr(ord(texto_plano[i]) ^ ord(carácter_clave))
        resultado.añadir(carácter_cifrado)
    retornar "".unir(resultado)


función descifrar_xor(texto_cifrado: cadena, clave: cadena) -> cadena:
    """Descifrar cifrado XOR (igual que el cifrado para XOR)."""
    retornar cifrar_xor(texto_cifrado, clave)


función verificar_contraseña(contraseña: cadena, hash_contraseña: entero) -> booleano:
    """Verificar que la contraseña coincide con el hash."""
    retornar hash_simple(contraseña) es hash_contraseña


función hash_chunks(texto: cadena, tamaño_chunk: entero) -> lista:
    """Hashear una cadena en chunks."""
    hashes = []
    para i en rango(0, longitud(texto), tamaño_chunk):
        chunk = texto[i : i + tamaño_chunk]
        hashes.añadir(hash_simple(chunk))
    retornar hashes


función cifrar_mensaje(texto_plano: cadena, clave: cadena) -> cadena:
    """Cifrar un mensaje usando cifrado XOR."""
    retornar cifrar_xor(texto_plano, clave)


función descifrar_mensaje(texto_cifrado: cadena, clave: cadena) -> cadena:
    """Descifrar un mensaje usando cifrado XOR."""
    retornar descifrar_xor(texto_cifrado, clave)


función cifrado_caesar(texto: cadena, desplazamiento: entero) -> cadena:
    """Cifrado Caesar simple (desplazar cada letra)."""
    resultado = []
    para carácter en texto:
        si carácter.isalpha():
            si carácter.isupper():
                desplazado = chr((ord(carácter) - ord("A") + desplazamiento) % 26 + ord("A"))
            sino:
                desplazado = chr((ord(carácter) - ord("a") + desplazamiento) % 26 + ord("a"))
            resultado.añadir(desplazado)
        sino:
            resultado.añadir(carácter)
    retornar "".unir(resultado)


función principal():
    # Probar función hash
    imprimir("=== Prueba de Función Hash ===")
    contraseña = "mySecurePassword123"
    hash_contraseña = hash_simple(contraseña)
    imprimir(f"Hash de '{contraseña}': {hash_contraseña}")
    imprimir(f"Verificación de hash: {verificar_contraseña(contraseña, hash_contraseña)}")
    imprimir(f"Verificación contraseña incorrecta: {verificar_contraseña('wrongpassword', hash_contraseña)}")

    # Probar cifrado XOR
    imprimir("\n=== Prueba de Cifrado XOR ===")
    texto_plano = "Hello World!"
    clave = "secretkey"

    texto_cifrado = cifrar_xor(texto_plano, clave)
    imprimir(f"Original: {texto_plano}")
    imprimir(f"Cifrado: {texto_cifrado}")

    texto_descifrado = descifrar_xor(texto_cifrado, clave)
    imprimir(f"Descifrado: {texto_descifrado}")
    imprimir(f"Coincide con original: {texto_descifrado es texto_plano}")

    # Probar cifrado Caesar
    imprimir("\n=== Prueba de Cifrado Caesar ===")
    mensaje = "Attack at dawn"
    desplazado = cifrado_caesar(mensaje, 3)
    imprimir(f"Original: {mensaje}")
    imprimir(f"Desplazado 3: {desplazado}")
    no_desplazado = cifrado_caesar(desplazado, -3)
    imprimir(f"Desplazado de vuelta: {no_desplazado}")

    # Probar hash en chunks
    imprimir("\n=== Prueba de Hash en Chunks ===")
    texto_largo = "This is a longer message that we will split into chunks and hash individually."
    hashes_chunks = hash_chunks(texto_largo, 10)
    imprimir(f"Longitud de texto: {longitud(texto_largo)}")
    imprimir(f"Número de chunks: {longitud(hashes_chunks)}")
    imprimir(f"Hash del primer chunk: {hashes_chunks[0]}")

    # Prueba de estrés: cifrados múltiples
    imprimir("\n=== Prueba de Estrés: Cifrados Múltiples ===")
    mensajes = [
        "Secret message 1",
        "Another secret 2",
        "Final secret 3",
    ]
    clave = "masterkey"

    todos_cifrados = []
    para msg en mensajes:
        texto_cifrado = cifrar_xor(msg, clave)
        todos_cifrados.añadir(texto_cifrado)
        imprimir(f"Cifrado: {longitud(texto_cifrado)} bytes")

    imprimir("\n✓ Todas las operaciones criptográficas completadas exitosamente")


principal()
