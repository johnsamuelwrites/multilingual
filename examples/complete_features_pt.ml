importe math
de math importe sqrt como root_fn

seja contador_global = 3

defina incrementar_global():
    global contador_global
    contador_global = contador_global + 2
    retorne contador_global

defina criar_contador(inicio):
    seja total = inicio
    defina passo():
        nao_local total
        total = total + 1
        retorne total
    retorne passo

seja proximo_contador = criar_contador(5)
seja primeiro_passo = proximo_contador()
seja segundo_passo = proximo_contador()

com abrir("tmp_complete_en.txt", "w", encoding="utf-8") como escrita:
    escrita.write("ok")

seja texto_arquivo = ""
com abrir("tmp_complete_en.txt", "r", encoding="utf-8") como leitura:
    texto_arquivo = leitura.read()

seja pares_unidos = lista(combinar([1, 2, 3], [4, 5, 6]))
seja valores_unicos = conjunto([1, 1, 2, 3])
seja valores_fixos = tuplo([10, 20, 30])
seja primeiro_elemento, *elementos_meio, ultimo_elemento = [1, 2, 3, 4]
seja mapa_combinado = {**{"x": 1}, **{"y": 2}}

defina formatar_etiqueta(a, /, *, b):
    retorne f"{a}-{b:.1f}"

seja etiqueta_formatada = formatar_etiqueta(7, b=3.5)
seja semente = 0
seja valor_morsa = (semente := semente + 9)

classe CaixaContador:
    defina __init__(self, base):
        self.valor = base

classe CaixaContadorFilha(CaixaContador):
    defina __init__(self, base):
        superclasse(CaixaContadorFilha, self).__init__(base)
        self.valor = self.valor + 1

defina produzir_tres():
    para indice em intervalo(3):
        produza indice

seja total_produzido = soma(produzir_tres())
seja tratado = Falso

tente:
    se comprimento(valores_unicos) > 2:
        lance ValueError("boom")
exceto ValueError como erro_tratado:
    tratado = Verdadeiro
finalmente:
    seja valor_raiz = inteiro(root_fn(16))

seja valor_temporario = 99
apagar valor_temporario

seja acumulacao_laco = 0
para n em intervalo(6):
    se n == 0:
        passe
    se n == 4:
        interrompa
    se n % 2 == 0:
        continue
    acumulacao_laco = acumulacao_laco + n

seja bandeira_ok = Verdadeiro e não Falso
afirmar bandeira_ok

seja caixa_filha = CaixaContadorFilha(40)

imprima(incrementar_global())
imprima(primeiro_passo, segundo_passo)
imprima(texto_arquivo)
imprima(comprimento(pares_unidos), comprimento(valores_unicos), valores_fixos[1])
imprima(primeiro_elemento, elementos_meio, ultimo_elemento)
imprima(caixa_filha.valor)
imprima(total_produzido, valor_raiz, tratado)
imprima(mapa_combinado["x"] + mapa_combinado["y"], etiqueta_formatada, valor_morsa)
imprima(acumulacao_laco)
imprima(contador_global é Nenhum)

# Loop else clauses
seja elementos_encontrados = Falso
para elemento em intervalo(3):
    se elemento == 10:
        elementos_encontrados = Verdadeiro
        interrompa
senão:
    elementos_encontrados = "not_found"

seja valor_laco_enquanto = 0
enquanto valor_laco_enquanto < 2:
    valor_laco_enquanto = valor_laco_enquanto + 1
senão:
    valor_laco_enquanto = valor_laco_enquanto + 10

# Starred unpacking variations
seja a, *resto = [10, 20, 30, 40]
seja *init, b = [10, 20, 30, 40]
seja c, *meio, d = [10, 20, 30, 40]

# Set comprehension
seja conjunto_quadrados = {x * x para x em intervalo(5)}

# Extended builtins
seja resultado_potencia = potencia(2, 8)
seja resultado_divmod = divmod(17, 5)

# Yield from generator
defina gerador_delegante():
    produza de intervalo(3)

seja delegado = lista(gerador_delegante())

imprima(elementos_encontrados, valor_laco_enquanto)
imprima(a, resto, init, b, c, meio, d)
imprima(ordenado(conjunto_quadrados))
imprima(resultado_potencia, resultado_divmod)
imprima(delegado)
