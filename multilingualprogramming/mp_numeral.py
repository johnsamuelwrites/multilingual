#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Functions to handle numbers of multiple languages
"""

import unicodedata

class mp_numeral:
    def __init__(self, numstr:str):
        self.numstr = numstr

    def to_numeral(self):
        return int(self.numstr)

