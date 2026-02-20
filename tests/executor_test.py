#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for the program executor (full pipeline)."""

import unittest

from multilingualprogramming.codegen.executor import ProgramExecutor


class ExecutorBasicTestSuite(unittest.TestCase):
    """Test basic execution of multilingual programs."""

    def test_hello_world_english(self):
        source = 'print("Hello, World!")\n'
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "Hello, World!")

    def test_variable_declaration_and_print(self):
        source = """\
let x = 42
print(x)
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "42")

    def test_arithmetic(self):
        source = """\
let a = 10
let b = 20
print(a + b)
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "30")

    def test_string_concatenation(self):
        source = """\
let greeting = "Hello"
let name = "World"
print(greeting + " " + name)
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "Hello World")

    def test_function_definition_and_call(self):
        source = """\
def add(a, b):
    return a + b

print(add(3, 4))
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "7")

    def test_factorial_recursive(self):
        source = """\
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "120")

    def test_for_loop(self):
        source = """\
let total = 0
for i in range(5):
    total = total + i
print(total)
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "10")

    def test_while_loop(self):
        source = """\
let count = 0
while count < 3:
    count = count + 1
print(count)
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "3")

    def test_if_elif_else(self):
        source = """\
let x = 2
if x == 1:
    print("one")
elif x == 2:
    print("two")
else:
    print("other")
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "two")

    def test_class_definition(self):
        source = """\
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count = self.count + 1

let c = Counter()
c.increment()
c.increment()
c.increment()
print(c.count)
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "3")

    def test_list_operations(self):
        source = """\
let items = [1, 2, 3, 4, 5]
print(len(items))
print(items[2])
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        lines = result.output.strip().split("\n")
        self.assertEqual(lines[0], "5")
        self.assertEqual(lines[1], "3")

    def test_try_except(self):
        source = """\
try:
    let x = 1 / 0
except ZeroDivisionError as e:
    print("caught")
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "caught")

    def test_try_except_else(self):
        source = """\
try:
    print("ok")
except ZeroDivisionError as e:
    print("caught")
else:
    print("else")
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        lines = result.output.strip().split("\n")
        self.assertEqual(lines, ["ok", "else"])

    def test_async_for_execution(self):
        source = """\
import asyncio

async def agen():
    for i in range(4):
        yield i

async def main():
    let total = 0
    async for i in agen():
        total = total + i
    return total

print(asyncio.run(main()))
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "6")

    def test_async_with_execution(self):
        source = """\
import asyncio

class AsyncCtx:
    async def __aenter__(self):
        return 7

    async def __aexit__(self, exc_type, exc, tb):
        return False

async def main():
    async with AsyncCtx() as value:
        return value

print(asyncio.run(main()))
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "7")

    def test_nested_functions(self):
        source = """\
def make_adder(n):
    def adder(x):
        return x + n
    return adder

let add5 = make_adder(5)
print(add5(10))
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "15")

    def test_boolean_logic(self):
        source = """\
let a = True
let b = False
if a and not b:
    print("correct")
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "correct")


class ExecutorMultilingualTestSuite(unittest.TestCase):
    """Test execution of programs in different languages.

    Uses exact keywords from keywords.json:
    - French: déf, soit, retour, si, sinon, sinonsi, pour, dans, tantque, afficher
    - Spanish: def, sea, devolver, si, sino, sinosi, para, en, mientras, imprimir
    - German: def, sei, rückgabe, wenn, sonst, sonstwenn, für, in, solange, ausgeben
    - Hindi: परिभाषा, मान, वापसी, अगर, वरना, के_लिए, में, जबतक, छापो
    - Chinese: 函数, 令, 返回, 如果, 否则, 对于, 里, 当, 打印
    - Japanese: 関数, 変数, 戻る, もし, でなければ, 毎, 中, 間, 表示
    """

    def test_french_program(self):
        source = """\
déf factoriel(n):
    si n <= 1:
        retour 1
    retour n * factoriel(n - 1)

afficher(factoriel(6))
"""
        executor = ProgramExecutor(language="fr")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "720")

    def test_french_variables(self):
        source = """\
soit x = 10
soit y = 20
afficher(x + y)
"""
        executor = ProgramExecutor(language="fr")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "30")

    def test_french_for_loop(self):
        source = """\
soit total = 0
pour i dans range(5):
    total = total + i
afficher(total)
"""
        executor = ProgramExecutor(language="fr")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "10")

    def test_spanish_program(self):
        source = """\
def suma(a, b):
    devolver a + b

imprimir(suma(3, 7))
"""
        executor = ProgramExecutor(language="es")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "10")

    def test_german_program(self):
        source = """\
def addiere(a, b):
    rückgabe a + b

ausgeben(addiere(5, 3))
"""
        executor = ProgramExecutor(language="de")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "8")

    def test_hindi_with_devanagari_numerals(self):
        source = """\
मान x = १०
मान y = २०
छापो(x + y)
"""
        executor = ProgramExecutor(language="hi")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "30")

    def test_chinese_program(self):
        source = """\
函数 加法(甲, 乙):
    返回 甲 + 乙

打印(加法(4, 6))
"""
        executor = ProgramExecutor(language="zh")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "10")

    def test_japanese_iterable_first_surface_for_loop(self):
        source = (
            "\u5909\u6570 \u7d50\u679c = 0\n"
            "\u7bc4\u56f2(5) \u5185\u306e \u5404 i \u306b\u5bfe\u3057\u3066:\n"
            "    \u7d50\u679c = \u7d50\u679c + i\n"
            "\u8868\u793a(\u7d50\u679c)\n"
        )
        executor = ProgramExecutor(language="ja")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "10")

    def test_arabic_iterable_first_surface_for_loop(self):
        source = (
            "\u0644\u064a\u0643\u0646 total = 0\n"
            "range(5) \u0636\u0645\u0646 \u0644\u0643\u0644 i:\n"
            "    total = total + i\n"
            "\u0627\u0637\u0628\u0639(total)\n"
        )
        executor = ProgramExecutor(language="ar")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "10")

    def test_spanish_iterable_first_surface_for_loop(self):
        source = (
            "sea total = 0\n"
            "range(5) para i:\n"
            "    total = total + i\n"
            "imprimir(total)\n"
        )
        executor = ProgramExecutor(language="es")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "10")

    def test_portuguese_iterable_first_surface_for_loop(self):
        source = (
            "seja total = 0\n"
            "range(5) para cada i:\n"
            "    total = total + i\n"
            "imprima(total)\n"
        )
        executor = ProgramExecutor(language="pt")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "10")

    def test_japanese_program(self):
        source = """\
関数 足し算(甲, 乙):
    戻る 甲 + 乙

表示(足し算(7, 8))
"""
        executor = ProgramExecutor(language="ja")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "15")


    def test_italian_program(self):
        source = """\
definisci somma(a, b):
    ritorna a + b

stampa(somma(4, 9))
"""
        executor = ProgramExecutor(language="it")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "13")

    def test_portuguese_program(self):
        source = """\
definir soma(a, b):
    retornar a + b

imprimir(soma(5, 8))
"""
        executor = ProgramExecutor(language="pt")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "13")

class ExecutorTranspileTestSuite(unittest.TestCase):
    """Test the transpile-only mode."""

    def test_transpile_returns_python(self):
        source = """\
let x = 42
print(x)
"""
        executor = ProgramExecutor(language="en")
        python_code = executor.transpile(source)
        self.assertIn("x = 42", python_code)
        self.assertIn("print(x)", python_code)

    def test_transpile_french(self):
        source = """\
soit nom = "Alice"
afficher(nom)
"""
        executor = ProgramExecutor(language="fr")
        python_code = executor.transpile(source)
        self.assertIn("nom = 'Alice'", python_code)
        self.assertIn("afficher(nom)", python_code)

    def test_transpile_devanagari_numerals_converted(self):
        source = """\
मान x = ५
"""
        executor = ProgramExecutor(language="hi")
        python_code = executor.transpile(source)
        self.assertIn("x = 5", python_code)

    def test_generated_python_in_result(self):
        source = 'print("test")\n'
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertTrue(result.success, result.errors)
        self.assertIn("print('test')", result.python_source)

    def test_to_core_ir_contains_detected_language(self):
        source = """\
soit x = 1
print(x)
"""
        executor = ProgramExecutor(language="fr")
        core = executor.to_core_ir(source)
        self.assertEqual(core.source_language, "fr")
        self.assertEqual(core.frontend_metadata["frontend_name"], "lexer_parser")


class ExecutorErrorTestSuite(unittest.TestCase):
    """Test error handling in the executor."""

    def test_syntax_error(self):
        source = "if:\n"
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertFalse(result.success)
        self.assertTrue(len(result.errors) > 0)

    def test_runtime_error(self):
        source = """\
let x = 1 / 0
"""
        executor = ProgramExecutor(language="en", check_semantics=False)
        result = executor.execute(source)
        self.assertFalse(result.success)
        self.assertTrue(any("ZeroDivisionError" in e for e in result.errors))

    def test_semantic_error_undefined_name(self):
        source = """\
print(undefined_variable)
"""
        executor = ProgramExecutor(language="en")
        result = executor.execute(source)
        self.assertFalse(result.success)
        self.assertTrue(len(result.errors) > 0)

    def test_output_captured_before_error(self):
        source = """\
print("before")
let x = 1 / 0
"""
        executor = ProgramExecutor(language="en", check_semantics=False)
        result = executor.execute(source)
        self.assertFalse(result.success)
        self.assertIn("before", result.output)
