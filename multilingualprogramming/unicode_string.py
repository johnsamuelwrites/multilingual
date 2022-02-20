#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Functions to represent numbers in multiple languages
"""

import unicodedata

number_strings = ["ZERO", "ONE", "TWO", "THREE", "FOUR",
        "FIVE", "SIX", "SEVEN", "EIGHT", "NINE"]

digit_string = "DIGIT"

def get_number_list(language:str):
    number_list = []
    for number in number_strings:
        number = unicodedata.lookup(language + " " + digit_string + " " +
                number)
        number_list.append(number)
    return (number_list)
