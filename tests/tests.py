#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Main file to run all the test suites
"""

import unittest

from tests.mp_numeral_test import MP_Numeral_TestSuite

if __name__ == "__main__":
    mp_numeral_tests = MP_Numeral_TestSuite()
    tests = unittest.TestSuite(
        [mp_numeral_tests]
    )
    unittest.main()