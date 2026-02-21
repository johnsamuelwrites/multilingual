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

con abrir("tmp_complete_es.txt", "w", encoding="utf-8") como escritura:
    escritura.write("ok")

sea texto_archivo = ""
con abrir("tmp_complete_es.txt", "r", encoding="utf-8") como lectura:
    texto_archivo = lectura.read()

clase CajaContador:
    def __init__(self, base):
        self.valor = base

clase CajaContadorHija(CajaContador):
    def __init__(self, base):
        superior(CajaContadorHija, self).__init__(base)
        self.valor = self.valor + 1

def producir_tres():
    para i en rango(3):
        producir i

sea pares = list(combinar([1, 2, 3], [4, 5, 6]))
sea unicos = conjunto([1, 1, 2, 3])
sea fijos = tupla([10, 20, 30])
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
imprimir(hija.valor)
imprimir(total_producido, raiz, manejado)
imprimir(acumulado)
imprimir(contador_global es Nada)
