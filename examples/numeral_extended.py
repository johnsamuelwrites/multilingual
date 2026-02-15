#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Examples demonstrating extended numeral features."""

from multilingualprogramming.numeral.mp_numeral import MPNumeral
from multilingualprogramming.numeral.unicode_numeral import UnicodeNumeral
from multilingualprogramming.numeral.complex_numeral import ComplexNumeral
from multilingualprogramming.numeral.fraction_numeral import FractionNumeral
from multilingualprogramming.numeral.numeral_converter import NumeralConverter

# Complex numbers
print("== Complex Numbers ==")
c1 = ComplexNumeral("3+4i")
c2 = ComplexNumeral("1+2i")
print(f"  {c1} + {c2} = {c1 + c2}")
print(f"  {c1} * {c2} = {c1 * c2}")
print(f"  |{c1}| = {abs(c1)}")
print(f"  conjugate({c1}) = {c1.conjugate()}")

# Complex numbers in Malayalam
print("\n== Complex Numbers in Malayalam ==")
c_ml = ComplexNumeral("൩+൪i")
print(f"  {c_ml} -> Python: {c_ml.to_complex()}")

# Fractions
print("\n== Fractions ==")
f1 = FractionNumeral("½")
f2 = FractionNumeral("¼")
print(f"  {f1} + {f2} = {(f1 + f2).to_fraction()}")
print(f"  {f1} * {f2} = {(f1 * f2).to_fraction()}")

f3 = FractionNumeral("3/4")
f4 = FractionNumeral("1/3")
print(f"  {f3} + {f4} = {(f3 + f4).to_fraction()}")

# Fractions in Malayalam
f_ml = FractionNumeral("൩/൪")
print(f"  Malayalam ൩/൪ = {f_ml.to_fraction()}")

# Cross-script conversion
print("\n== Cross-Script Conversion ==")
num = UnicodeNumeral("12345")
print(f"  ASCII:        {num}")
converted = NumeralConverter.convert(num, "MALAYALAM")
print(f"  Malayalam:    {converted}")
converted = NumeralConverter.convert(num, "ARABIC-INDIC")
print(f"  Arabic-Indic: {converted}")
converted = NumeralConverter.convert(num, "BENGALI")
print(f"  Bengali:      {converted}")

# Scientific notation
print("\n== Scientific Notation ==")
num = UnicodeNumeral("12300")
sci = NumeralConverter.to_scientific(num)
print(f"  {num} -> {sci}")
parsed = NumeralConverter.from_scientific(sci)
print(f"  {sci} -> {parsed}")

# Comparison operators
print("\n== Comparison Operators ==")
n1 = UnicodeNumeral("൧൩")  # 13 in Malayalam
n2 = UnicodeNumeral("൨൪")  # 24 in Malayalam
print(f"  {n1} < {n2}? {n1 < n2}")
print(f"  {n1} == {n2}? {n1 == n2}")
print(f"  |{n1}| = {abs(n1)}")

# MPNumeral cross-script conversion
print("\n== MPNumeral Conversion ==")
mp = MPNumeral("12345")
mp_ml = mp.convert_to("MALAYALAM")
print(f"  {mp} -> Malayalam: {mp_ml}")
