# Análisis JSON - Proyecto WASM Corpus
# Variante española
#
# Demuestra:
# - Análisis JSON (procesamiento de cadenas)
# - Serialización JSON
# - Manipulación de estructuras de datos
# - Operaciones intensivas en datos ideales para WASM

# SPDX-License-Identifier: GPL-3.0-or-later

función analizar_json_simple(cadena_json: cadena) -> objeto:
    """Analizar JSON simple (usando el analizador integrado)."""
    importar json
    retornar json.cargas(cadena_json)


función stringify_json(obj: objeto) -> cadena:
    """Convertir un objeto a cadena JSON."""
    importar json
    retornar json.volcados(obj)


función crear_datos_muestra() -> objeto:
    """Crear una estructura de datos de muestra."""
    datos = {
        "usuarios": [
            {
                "id": 1,
                "nombre": "Alice",
                "email": "alice@example.com",
                "roles": ["admin", "usuario"],
            },
            {
                "id": 2,
                "nombre": "Bob",
                "email": "bob@example.com",
                "roles": ["usuario"],
            },
            {
                "id": 3,
                "nombre": "Charlie",
                "email": "charlie@example.com",
                "roles": ["usuario", "moderador"],
            },
        ],
        "metadatos": {
            "versión": "1.0",
            "timestamp": "2024-02-22T10:00:00Z",
            "total_usuarios": 3,
        },
    }
    retornar datos


función filtrar_usuarios_por_rol(usuarios: lista, rol: cadena) -> lista:
    """Filtrar usuarios que tienen un rol específico."""
    filtrados = []
    para usuario en usuarios:
        si "roles" en usuario:
            si rol en usuario["roles"]:
                filtrados.añadir(usuario)
    retornar filtrados


función contar_usuarios_por_rol(usuarios: lista) -> objeto:
    """Contar ocurrencias de cada rol."""
    conteos_rol = {}
    para usuario en usuarios:
        si "roles" en usuario:
            para rol en usuario["roles"]:
                si rol no en conteos_rol:
                    conteos_rol[rol] = 0
                conteos_rol[rol] = conteos_rol[rol] + 1
    retornar conteos_rol


función extraer_correos(usuarios: lista) -> lista:
    """Extraer direcciones de correo de la lista de usuarios."""
    correos = []
    para usuario en usuarios:
        si "email" en usuario:
            correos.añadir(usuario["email"])
    retornar correos


función transformar_nombres_usuarios(usuarios: lista) -> lista:
    """Transformar nombres de usuario a mayúsculas."""
    transformados = []
    para usuario en usuarios:
        copia_usuario = {
            "id": usuario.obtener("id"),
            "nombre": usuario.obtener("nombre", "").mayúscula(),
            "email": usuario.obtener("email"),
        }
        transformados.añadir(copia_usuario)
    retornar transformados


función fusionar_objetos_json(obj1: objeto, obj2: objeto) -> objeto:
    """Fusionar dos objetos JSON."""
    fusionado = obj1.copiar()
    para clave, valor en obj2.elementos():
        fusionado[clave] = valor
    retornar fusionado


función validar_usuario(usuario: objeto) -> booleano:
    """Validar que el objeto usuario tiene los campos requeridos."""
    campos_requeridos = ["id", "nombre", "email"]
    para campo en campos_requeridos:
        si campo no en usuario:
            retornar falso
    retornar verdadero


función principal():
    imprimir("=== Demostración de Análisis JSON ===")

    # Crear y serializar datos de muestra
    imprimir("\n1. Crear datos de muestra...")
    datos = crear_datos_muestra()
    imprimir(f"Estructura de datos creada con {longitud(datos['usuarios'])} usuarios")

    # Convertir a JSON
    imprimir("\n2. Serialización a JSON...")
    cadena_json = stringify_json(datos)
    imprimir(f"Longitud de cadena JSON: {longitud(cadena_json)} caracteres")
    imprimir(f"Primeros 100 caracteres: {cadena_json[0:100]}")

    # Analizar desde JSON
    imprimir("\n3. Análisis JSON de vuelta a objeto...")
    datos_analizados = analizar_json_simple(cadena_json)
    imprimir(f"Análisis exitoso: {longitud(datos_analizados['usuarios'])} usuarios")

    # Operaciones de filtrado
    imprimir("\n4. Filtrado de usuarios por rol...")
    usuarios_admin = filtrar_usuarios_por_rol(datos["usuarios"], "admin")
    imprimir(f"Encontrados {longitud(usuarios_admin)} usuario(s) admin")

    usuarios_moderador = filtrar_usuarios_por_rol(datos["usuarios"], "moderador")
    imprimir(f"Encontrados {longitud(usuarios_moderador)} usuario(s) moderador")

    # Contar roles
    imprimir("\n5. Conteo de roles...")
    conteos_rol = contar_usuarios_por_rol(datos["usuarios"])
    imprimir(f"Distribución de roles: {conteos_rol}")

    # Extraer correos
    imprimir("\n6. Extracción de correos electrónicos...")
    correos = extraer_correos(datos["usuarios"])
    imprimir(f"Correos: {correos}")

    # Transformar datos
    imprimir("\n7. Transformación de nombres de usuario a mayúsculas...")
    usuarios_mayusculas = transformar_nombres_usuarios(datos["usuarios"])
    para usuario en usuarios_mayusculas:
        imprimir(f"  {usuario['nombre']} ({usuario['email']})")

    # Validar usuarios
    imprimir("\n8. Validación de usuarios...")
    conteo_validos = 0
    para usuario en datos["usuarios"]:
        si validar_usuario(usuario):
            conteo_validos = conteo_validos + 1
    imprimir(f"Usuarios válidos: {conteo_validos}/{longitud(datos['usuarios'])}")

    # Fusionar objetos
    imprimir("\n9. Fusión de objetos JSON...")
    nuevos_metadatos = {"autor": "test", "revisión": 2}
    fusionado = fusionar_objetos_json(datos["metadatos"], nuevos_metadatos)
    imprimir(f"Claves de metadatos fusionadas: {longitud(fusionado)}")

    # Prueba de estrés: JSON grande
    imprimir("\n10. Prueba de estrés: procesamiento de JSON grande...")
    datos_grandes = {
        "elementos": [],
    }
    para i en rango(100):
        datos_grandes["elementos"].añadir({
            "id": i,
            "valor": i * 10,
            "procesado": falso,
        })

    json_grande = stringify_json(datos_grandes)
    imprimir(f"JSON grande creado: {longitud(json_grande)} caracteres")

    datos_grandes_analizados = analizar_json_simple(json_grande)
    imprimir(f"JSON grande analizado: {longitud(datos_grandes_analizados['elementos'])} elementos")

    imprimir("\n✓ Todas las operaciones JSON completadas exitosamente")


principal()
