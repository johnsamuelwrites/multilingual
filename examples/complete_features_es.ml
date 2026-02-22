importar math
desde math importar sqrt como root_fn

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
