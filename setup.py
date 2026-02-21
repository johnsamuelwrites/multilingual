#
# SPDX-FileCopyrightText: 2020 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Compatibility shim for legacy setuptools workflows.

Project metadata is defined in ``pyproject.toml`` (PEP 621).
"""

from setuptools import setup  # pylint: disable=import-error


if __name__ == "__main__":
    setup()
