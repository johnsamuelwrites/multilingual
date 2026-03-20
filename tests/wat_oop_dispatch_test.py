#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for WAT OOP dispatch: @property, @staticmethod/@classmethod, print
kwargs, and vtable-based dynamic dispatch."""

import unittest

from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.codegen.wat_generator import WATCodeGenerator


def _parse(source):
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()


def _wat(source):
    return WATCodeGenerator().generate(_parse(source))


def _wat_gen(source):
    """Return (wat_text, generator) so state can be inspected."""
    gen = WATCodeGenerator()
    wat = gen.generate(_parse(source))
    return wat, gen


# ---------------------------------------------------------------------------
# @property support
# ---------------------------------------------------------------------------

class TestWATProperty(unittest.TestCase):
    """@property getter is called via attribute access, not field load."""

    _src_radius = """
class Circle:
    def __init__(self, r):
        self.r = r
    @property
    def radius(self):
        return self.r
c = Circle(5)
print(c.radius)
"""

    def test_property_method_registered(self):
        """@property method name maps to a property getter entry."""
        _, gen = _wat_gen(self._src_radius)
        self.assertIn("Circle.radius", gen.property_getters)

    def test_property_access_emits_call(self):
        """c.radius emits a WAT function call, not a raw f64.load."""
        wat = _wat(self._src_radius)
        self.assertIn("call $Circle__radius", wat)

    def test_property_getter_receives_self(self):
        """The call to the property getter passes self (or f64.const 0)."""
        wat = _wat(self._src_radius)
        self.assertIn("Circle__radius", wat)

    def test_property_getter_in_return(self):
        """return self.side inside the getter emits f64.load at the right offset."""
        src = """
class Box:
    def __init__(self, side):
        self.side = side
    @property
    def width(self):
        return self.side
b = Box(10)
print(b.width)
"""
        wat = _wat(src)
        self.assertIn("Box__width", wat)
        self.assertIn("f64.load", wat)

    def test_regular_field_still_uses_load(self):
        """Non-property attribute access still uses f64.load."""
        src = """
class Point:
    def __init__(self, x):
        self.x = x
p = Point(3)
print(p.x)
"""
        wat = _wat(src)
        self.assertIn("f64.load", wat)
        self.assertNotIn("__dispatch_x", wat)

    def test_staticmethod_no_self(self):
        """@staticmethod method has no self pushed at call site."""
        src = """
class Math:
    @staticmethod
    def double(n):
        return n
"""
        wat = _wat(src)
        self.assertIn("Math__double", wat)
        self.assertNotIn("$self", wat)

    def test_classmethod_no_self(self):
        """@classmethod method: cls is first param but no extra self pushed."""
        src = """
class Factory:
    @classmethod
    def create(cls):
        return 1
"""
        wat = _wat(src)
        self.assertIn("Factory__create", wat)


# ---------------------------------------------------------------------------
# print sep= and end= kwargs
# ---------------------------------------------------------------------------

class TestWATPrintSepEnd(unittest.TestCase):
    """print() with sep= and end= keyword arguments."""

    def test_default_sep_uses_print_sep(self):
        """Default separator (space) uses call $print_sep."""
        wat = _wat('print(1, 2)')
        self.assertIn("call $print_sep", wat)

    def test_custom_sep_uses_print_str(self):
        """sep=\",\" interns the comma and calls print_str instead of print_sep."""
        wat = _wat('print(1, 2, sep=",")')
        self.assertNotIn("call $print_sep", wat)
        self.assertIn("call $print_str", wat)
        # Comma is \2c in UTF-8 hex
        self.assertIn("\\2c", wat)

    def test_empty_sep_no_separator_call(self):
        """sep=\"\" emits no separator at all."""
        wat = _wat('print(1, 2, sep="")')
        self.assertNotIn("call $print_sep", wat)

    def test_default_end_uses_print_newline(self):
        """Default end (newline) uses call $print_newline."""
        wat = _wat('print(1)')
        self.assertIn("call $print_newline", wat)

    def test_empty_end_no_newline(self):
        """end=\"\" suppresses the newline call."""
        wat = _wat('print(1, end="")')
        self.assertNotIn("call $print_newline", wat)

    def test_custom_end_uses_print_str(self):
        """end=\"!\" interns the string and calls print_str."""
        wat = _wat('print(1, end="!")')
        self.assertNotIn("call $print_newline", wat)
        self.assertIn("call $print_str", wat)
        # ! is \21 in UTF-8 hex
        self.assertIn("\\21", wat)

    def test_sep_and_end_together(self):
        """sep=\"|\" and end=\"\" both apply simultaneously."""
        wat = _wat('print(1, 2, sep="|", end="")')
        self.assertNotIn("call $print_sep", wat)
        self.assertNotIn("call $print_newline", wat)
        self.assertIn("call $print_str", wat)

    def test_single_arg_no_sep_call(self):
        """Single arg never emits a separator."""
        wat = _wat('print(42)')
        self.assertNotIn("call $print_sep", wat)
        self.assertIn("call $print_newline", wat)


# ---------------------------------------------------------------------------
# Dynamic dispatch / vtable
# ---------------------------------------------------------------------------

class TestWATDynamicDispatch(unittest.TestCase):
    """Vtable-based dynamic dispatch via type tags."""

    _src_animals = """
class Animal:
    def __init__(self):
        self.x = 0
    def speak(self):
        return 1
class Dog(Animal):
    def __init__(self):
        self.x = 0
    def speak(self):
        return 2
def make_noise(obj):
    obj.speak()
"""

    def test_class_ids_assigned(self):
        """Both classes get integer IDs."""
        _, gen = _wat_gen(self._src_animals)
        self.assertIn("Animal", gen.class_ids)
        self.assertIn("Dog", gen.class_ids)
        self.assertNotEqual(
            gen.class_ids["Animal"], gen.class_ids["Dog"]
        )

    def test_dispatch_func_registered(self):
        """Overridden method 'speak' has a dispatch entry."""
        _, gen = _wat_gen(self._src_animals)
        self.assertIn("speak", gen.dispatch_func_names)

    def test_dispatch_func_emitted(self):
        """The WAT module contains the dispatch function."""
        wat = _wat(self._src_animals)
        self.assertIn("__dispatch_speak", wat)

    def test_type_tag_stored_at_alloc(self):
        """Constructor writes class_id via i32.store."""
        wat = _wat(self._src_animals + "\na = Animal()\n")
        self.assertIn("i32.store", wat)

    def test_type_tag_loaded_in_dispatch(self):
        """Dispatch function reads type tag via i32.load."""
        wat = _wat(self._src_animals)
        self.assertIn("i32.load", wat)

    def test_type_tag_8_bytes_before_ptr(self):
        """Type tag is accessed at self_ptr - 8 (i32.const 8, i32.sub)."""
        wat = _wat(self._src_animals)
        self.assertIn("i32.const 8", wat)
        self.assertIn("i32.sub", wat)

    def test_animal_class_id_zero(self):
        """Animal (first class) gets class_id = 0."""
        _, gen = _wat_gen(self._src_animals)
        self.assertEqual(gen.class_ids["Animal"], 0)

    def test_dog_class_id_one(self):
        """Dog (second class) gets class_id = 1."""
        _, gen = _wat_gen(self._src_animals)
        self.assertEqual(gen.class_ids["Dog"], 1)

    def test_dispatch_calls_both_impls(self):
        """Dispatch function references both Animal__speak and Dog__speak."""
        wat = _wat(self._src_animals)
        self.assertIn("Animal__speak", wat)
        self.assertIn("Dog__speak", wat)

    def test_unknown_receiver_uses_dispatch(self):
        """Function param of unknown class type routes through dispatch fn."""
        wat = _wat(self._src_animals)
        self.assertIn("dynamic dispatch speak", wat)

    def test_known_receiver_still_direct(self):
        """When class is statically known, direct call is still used."""
        src = """
class Cat:
    def __init__(self):
        self.x = 0
    def speak(self):
        return 3
c = Cat()
c.speak()
"""
        wat = _wat(src)
        self.assertNotIn("__dispatch_speak", wat)
        self.assertIn("Cat__speak", wat)

    def test_type_tag_in_ctor_comment(self):
        """Constructor comment mentions type_tag allocation."""
        wat = _wat(self._src_animals + "\na = Animal()\n")
        self.assertIn("type_tag=8", wat)

    def test_field_offsets_unchanged(self):
        """Adding type tag does not change field byte offsets (still 0, 8, ...)."""
        src = """
class Point:
    def __init__(self, px, pz):
        self.px = px
        self.pz = pz
"""
        wat = _wat(src)
        self.assertIn("i32.const 0", wat)
        self.assertIn("i32.const 8", wat)

    def test_obj_size_unchanged(self):
        """Object size metadata still reflects only field bytes (not tag bytes)."""
        _, gen = _wat_gen("""
class Pair:
    def __init__(self, a, b):
        self.a = a
        self.b = b
""")
        self.assertEqual(gen.class_obj_sizes.get("Pair"), 16)

    def test_stateless_polymorphic_classes_still_dispatch(self):
        """Overridden stateless methods still get tagged runtime dispatch."""
        src = """
class Animal:
    def speak(self):
        return 1
class Dog(Animal):
    def speak(self):
        return 2
def make_noise(obj):
    obj.speak()
pet = Dog()
make_noise(pet)
"""
        wat = _wat(src)
        self.assertIn("__dispatch_speak", wat)
        self.assertIn("alloc Dog (type_tag=8 + fields=0 bytes)", wat)
        self.assertNotIn("unsupported call: Dog(...)", wat)


if __name__ == "__main__":
    unittest.main()
