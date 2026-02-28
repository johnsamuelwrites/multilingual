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

# Numeric literals
seja num_hex = 0xFF
seja num_oct = 0o17
seja num_bin = 0b1010
seja num_cient = 1.5e3

# Augmented assignments
seja aumentado = 10
aumentado += 5
aumentado -= 2
aumentado *= 3
aumentado //= 4
aumentado %= 3

# Bitwise operators
seja bit_e = 0b1010 & 0b1100
seja bit_ou = 0b1010 | 0b0101
seja bit_xor = 0b1010 ^ 0b1111
seja bit_esq = 1 << 3
seja bit_dir = 64 >> 2

# Chained assignment
seja cadeia_a = cadeia_b = cadeia_c = 0

# Type annotations
seja tipado: inteiro = 99

defina anotado(x: inteiro, y: real) -> texto:
    retorne texto(x + y)

# Ternary expression
seja ternario = "yes" se tipado > 0 senão "no"

# Default params, *args, **kwargs
defina multi_parametros(base, extra=1, *args, **kwargs):
    retorne base + extra + soma(args)
seja resultado_multi = multi_parametros(10, 2, 3, 4, key=5)

# Lambda
seja quadrado = lambda x: x * x

# List/dict comprehensions and generator expression
seja lista_c = [x * 2 para x em intervalo(4)]
seja dict_c = {texto(k): k * k para k em intervalo(3)}
seja gen_c = lista(x + 1 para x em intervalo(3))
seja aninhado_c = [i + j para i em intervalo(2) para j em intervalo(2)]
seja filtro_c = [x para x em intervalo(6) se x % 2 == 0]

# try/except/else
seja tente_senao = 0
tente:
    tente_senao = inteiro("7")
exceto ValueError:
    tente_senao = -1
senão:
    tente_senao += 1

# Exception chaining
seja encadeado = Falso
tente:
    tente:
        lance ValueError("v")
    exceto ValueError como ve:
        lance RuntimeError("r") de ve
exceto RuntimeError:
    encadeado = Verdadeiro

# Multiple except handlers
seja multi_excecao = 0
tente:
    lance TypeError("t")
exceto ValueError:
    multi_excecao = 1
exceto TypeError:
    multi_excecao = 2

# Match/case with default
seja valor_match = 2
seja resultado_match = "other"
corresponda valor_match:
    caso 1:
        resultado_match = "one"
    caso 2:
        resultado_match = "two"
    padrao:
        resultado_match = "default"

# Decorator
defina duplicador(func):
    defina envoltorio(*args, **kwargs):
        retorne func(*args, **kwargs) * 2
    retorne envoltorio

@duplicador
defina dez():
    retorne 10

seja resultado_deco = dez()

# Multiple inheritance, static/class methods, property
classe Mistura:
    defina mistura(self):
        retorne 1

classe BaseDois:
    defina __init__(self, start):
        self.value = start

classe Combinado(BaseDois, Mistura):
    @staticmethod
    defina rotulo():
        retorne "combined"
    @classmethod
    defina construir(cls, v):
        retorne cls(v)
    @property
    defina dobrado(self):
        retorne self.value * 2

seja combinado_obj = Combinado.construir(3)
seja propriedade = combinado_obj.dobrado

# Docstring
defina com_doc():
    """A docstring."""
    retorne Verdadeiro

imprima(num_hex, num_oct, num_bin, num_cient)
imprima(aumentado, bit_e, bit_ou, bit_xor, bit_esq, bit_dir)
imprima(cadeia_a, cadeia_b, cadeia_c)
imprima(tipado, anotado(3, 1.5), ternario)
imprima(resultado_multi, quadrado(5))
imprima(lista_c, dict_c, gen_c)
imprima(aninhado_c, filtro_c)
imprima(tente_senao, encadeado, multi_excecao)
imprima(resultado_match, resultado_deco, propriedade)
imprima(com_doc())
