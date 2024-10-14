#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


# Reference of numeral systems: https://en.wikipedia.org/wiki/List_of_numeral_systems

from multilingualprogramming.numeral.mp_numeral import MPNumeral

## Roman numerals
num1 = MPNumeral("VII")
num2 = MPNumeral("III")

print(num1 + num2)
print(num1 - num2)
print(num1 * num2)
print(num1 // num2)
print(num1 % num2)
print(num1**num2)


## Unicode numerals
num1 = MPNumeral("١٢٣٤٥")
num2 = MPNumeral("൧൩")
print(num1 + num2)
print(num1 - num2)
print(num1 * num2)
print(num1 // num2)
print(num1 % num2)
print(num1**num2)


num1 = MPNumeral("߉")
num2 = MPNumeral("߂")
print(num1 + num2)
print(num1 - num2)
print(num1 * num2)
print(num1 // num2)
print(num1 % num2)
print(num1**num2)

num1 = MPNumeral("𐒡")
num2 = MPNumeral("𐒣")
print(num1 + num2)
print(num1 - num2)
print(num1 * num2)
print(num1 // num2)
print(num1 % num2)
print(num1**num2)
