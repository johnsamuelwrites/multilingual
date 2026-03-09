importar math
desde math importar sqrt como root_fn
importar asyncio

sea contador_global = 3

def aumentar_global():
    global contador_global
    contador_global = contador_global + 2
    devolver contador_global

def crear_contador(inicio):
    sea total = inicio
    def paso():
        nolocal total
        total = total + 1
        devolver total
    devolver paso

sea contador_siguiente = crear_contador(5)
sea primero = contador_siguiente()
sea segundo = contador_siguiente()

con abrir("tmp_complete_en.txt", "w", encoding="utf-8") como escritura:
    escritura.write("ok")

sea texto_archivo = ""
con abrir("tmp_complete_en.txt", "r", encoding="utf-8") como lectura:
    texto_archivo = lectura.read()

sea pares = lista(combinar([1, 2, 3], [4, 5, 6]))
sea unicos = conjunto([1, 1, 2, 3])
sea fijos = tupla([10, 20, 30])
sea primero_lista, *medio_lista, ultimo_lista = [1, 2, 3, 4]
sea combinado = {**{"x": 1}, **{"y": 2}}

def etiquetar(a, /, *, b):
    devolver f"{a}-{b:.1f}"

sea etiqueta = etiquetar(7, b=3.5)
sea semilla = 0
sea valor_morsa = (semilla := semilla + 9)

clase CajaContador:
    def __init__(self, base):
        self.valor = base

clase CajaContadorHija(CajaContador):
    def __init__(self, base):
        superior(CajaContadorHija, self).__init__(base)
        self.valor = self.valor + 1

def producir_tres():
    para indice en rango(3):
        producir indice

sea total_producido = suma(producir_tres())
sea manejado = Falso

intentar:
    si longitud(unicos) > 2:
        lanzar ValueError("boom")
excepto ValueError como error_manejado:
    manejado = Verdadero
finalmente:
    sea raiz = entero(root_fn(16))

sea temporal = 99
eliminar temporal

sea acumulado = 0
para n en rango(6):
    si n == 0:
        pasar
    si n == 4:
        romper
    si n % 2 == 0:
        continuar
    acumulado = acumulado + n

sea bandera_ok = Verdadero y no Falso
afirmar bandera_ok

sea hija = CajaContadorHija(40)

imprimir(aumentar_global())
imprimir(primero, segundo)
imprimir(texto_archivo)
imprimir(longitud(pares), longitud(unicos), fijos[1])
imprimir(primero_lista, medio_lista, ultimo_lista)
imprimir(hija.valor)
imprimir(total_producido, raiz, manejado)
imprimir(combinado["x"] + combinado["y"], etiqueta, valor_morsa)
imprimir(acumulado)
imprimir(contador_global es Nada)

# Loop else clauses
sea elementos_encontrados = Falso
para elemento en rango(3):
    si elemento == 10:
        elementos_encontrados = Verdadero
        romper
sino:
    elementos_encontrados = "not_found"

sea val_while_else = 0
mientras val_while_else < 2:
    val_while_else = val_while_else + 1
sino:
    val_while_else = val_while_else + 10

# Starred unpacking variations
sea a, *resto = [10, 20, 30, 40]
sea *init, b = [10, 20, 30, 40]
sea c, *medio2, d = [10, 20, 30, 40]

# Set comprehension
sea conjunto_cuadrados = {x * x para x en rango(5)}

# Extended builtins
sea resultado_potencia = potencia(2, 8)
sea resultado_divmod = divmod(17, 5)

# Yield from generator
def gen_delegado():
    producir desde rango(3)

sea delegado = lista(gen_delegado())

imprimir(elementos_encontrados, val_while_else)
imprimir(a, resto, init, b, c, medio2, d)
imprimir(ordenado(conjunto_cuadrados))
imprimir(resultado_potencia, resultado_divmod)
imprimir(delegado)

# Numeric literals
sea num_hex = 0xFF
sea num_oct = 0o17
sea num_bin = 0b1010
sea num_cient = 1.5e3

# Augmented assignments
sea aumentado = 10
aumentado += 5
aumentado -= 2
aumentado *= 3
aumentado //= 4
aumentado %= 3

# Bitwise operators
sea bit_y = 0b1010 & 0b1100
sea bit_o = 0b1010 | 0b0101
sea bit_xor = 0b1010 ^ 0b1111
sea bit_izq = 1 << 3
sea bit_der = 64 >> 2

# Chained assignment
sea cadena_a = cadena_b = cadena_c = 0

# Type annotations
sea tipado: entero = 99

def anotado(x: entero, z: flotante) -> cadena:
    devolver cadena(x + z)

# Ternary expression
sea ternario = "yes" si tipado > 0 sino "no"

# Default params, *args, **kwargs
def multi_parametros(base, extra=1, *args, **kwargs):
    devolver base + extra + suma(args)
sea resultado_multi = multi_parametros(10, 2, 3, 4, key=5)

# Lambda
sea cuadrado = lambda x: x * x

# List/dict comprehensions and generator expression
sea lista_c = [x * 2 para x en rango(4)]
sea dicc_c = {cadena(k): k * k para k en rango(3)}
sea gen_c = lista(x + 1 para x en rango(3))
sea anidado_c = [i + j para i en rango(2) para j en rango(2)]
sea filtro_c = [x para x en rango(6) si x % 2 == 0]

# try/except/else
sea intenta_sino = 0
intentar:
    intenta_sino = entero("7")
excepto ValueError:
    intenta_sino = -1
sino:
    intenta_sino += 1

# Exception chaining
sea encadenado = Falso
intentar:
    intentar:
        lanzar ValueError("v")
    excepto ValueError como ve:
        lanzar RuntimeError("r") desde ve
excepto RuntimeError:
    encadenado = Verdadero

# Multiple except handlers
sea multi_excepcion = 0
intentar:
    lanzar TypeError("t")
excepto ValueError:
    multi_excepcion = 1
excepto TypeError:
    multi_excepcion = 2

# Match/case with default
sea valor_seg_n = 2
sea resultado_seg_n = "other"
según valor_seg_n:
    caso 1:
        resultado_seg_n = "one"
    caso 2:
        resultado_seg_n = "two"
    predeterminado:
        resultado_seg_n = "default"

# Decorator
def duplicador(func):
    def envoltura(*args, **kwargs):
        devolver func(*args, **kwargs) * 2
    devolver envoltura

@duplicador
def diez():
    devolver 10

sea resultado_deco = diez()

# Multiple inheritance, static/class methods, property
clase Mezcla:
    def mezcla(self):
        devolver 1

clase BaseDos:
    def __init__(self, start):
        self.value = start

clase Combinado(BaseDos, Mezcla):
    @staticmethod
    def etiqueta():
        devolver "combined"
    @classmethod
    def construir(cls, v):
        devolver cls(v)
    @property
    def doble(self):
        devolver self.value * 2

sea combinado_obj = Combinado.construir(3)
sea propiedad = combinado_obj.doble

# Docstring
def con_doc():
    """A docstring."""
    devolver Verdadero

imprimir(num_hex, num_oct, num_bin, num_cient)
imprimir(aumentado, bit_y, bit_o, bit_xor, bit_izq, bit_der)
imprimir(cadena_a, cadena_b, cadena_c)
imprimir(tipado, anotado(3, 1.5), ternario)
imprimir(resultado_multi, cuadrado(5))
imprimir(lista_c, dicc_c, gen_c)
imprimir(anidado_c, filtro_c)
imprimir(intenta_sino, encadenado, multi_excepcion)
imprimir(resultado_seg_n, resultado_deco, propiedad)
imprimir(con_doc())

# Asignaciones aumentadas bit a bit y potencia (v0.6.0)
sea bau_bits = 0b1111
bau_bits &= 0b1010
bau_bits |= 0b0100
bau_bits ^= 0b0011
bau_bits <<= 1
bau_bits >>= 2
sea pot_aug = 2
pot_aug **= 4

# Literal de bytes (v0.6.0)
sea datos_bytes = b"hello"
sea tam_bytes = longitud(datos_bytes)

# Concatenación, indexación y segmento de cadena (v0.6.0)
sea cadena_x = "hello"
sea cadena_y = " world"
sea concat_cadena = cadena_x + cadena_y
sea idx_cadena = cadena_x[1]
sea seg_cadena = cadena_x[1:3]

# Literal de tupla (v0.6.0)
sea tupla_es = (10, 20, 30)
sea elem_tupla_es = tupla_es[1]

# Bucle for sobre variable de lista y comprensión (v0.6.0)
sea lista_iter = [10, 20, 30]
sea suma_iter = 0
para val_iter en lista_iter:
    suma_iter = suma_iter + val_iter

sea lista_dobl_src = [1, 2, 3, 4]
sea lista_doblada = [v * 2 para v en lista_dobl_src]

# Coincidencia extendida: cadena, Nada, numérico y tupla (v0.6.0)
sea cadena_m = "hello"
sea result_cadena_m = "ninguno"
según cadena_m:
    caso "hello":
        result_cadena_m = "hi"
    caso "bye":
        result_cadena_m = "goodbye"
    predeterminado:
        result_cadena_m = "unknown"

sea val_nada = Nada
sea result_nada = "definido"
según val_nada:
    caso Nada:
        result_nada = "null"
    predeterminado:
        result_nada = "other"

sea val_num_m = 42
sea result_num_m = 0
según val_num_m:
    caso 42:
        result_num_m = val_num_m
    predeterminado:
        result_num_m = 0

sea val_tupla_m = (1, 2)
sea result_tupla_m = "no"
según val_tupla_m:
    caso (1, 2):
        result_tupla_m = "yes"
    predeterminado:
        result_tupla_m = "no"

# async def, await, async for, async with (v0.6.0)
asincrono def doblar_async(n):
    esperar asyncio.sleep(0)
    devolver n * 2

asincrono def gen_async_es():
    para v en range(3):
        producir v

asincrono def tarea_async_para():
    sea total_async = 0
    asincrono para av en gen_async_es():
        total_async = total_async + av
    devolver total_async

clase ContextoAsyncEs:
    asincrono def __aenter__(self):
        devolver 5
    asincrono def __aexit__(self, exc_type, exc, tb):
        devolver Falso

asincrono def tarea_async_con():
    asincrono con ContextoAsyncEs() como valor:
        devolver valor

sea resultado_async = asyncio.run(doblar_async(5))
sea resultado_async_para = asyncio.run(tarea_async_para())
sea resultado_async_con = asyncio.run(tarea_async_con())

imprimir(bau_bits, pot_aug)
imprimir(tam_bytes)
imprimir(concat_cadena, idx_cadena, seg_cadena)
imprimir(elem_tupla_es, suma_iter)
imprimir(lista_doblada)
imprimir(result_cadena_m, result_nada, result_num_m, result_tupla_m)
imprimir(resultado_async, resultado_async_para, resultado_async_con)
