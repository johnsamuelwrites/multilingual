#
# SPDX-FileCopyrightText: 2020 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Setup file for multilingualprogramming
"""

import runpy
try:
    import setuptools
except ImportError:  # pragma: no cover - fallback for lint/test envs
    setuptools = None

version_meta = runpy.run_path("./multilingualprogramming/version.py")
VERSION = version_meta["__version__"]

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

if setuptools is not None:
    setuptools.setup(
        name="multilingualprogramming",
        version=VERSION,
        author="John Samuel",
        author_email="johnsamuelwrites@example.com",
        description="Python application for multilingual programming",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/johnsamuelwrites/multilingual",
        packages=setuptools.find_packages(),
        include_package_data=True,
        package_dir={"multilingualprogramming": "multilingualprogramming"},
        package_data={
            "multilingualprogramming": [
                "resources/*/*.json",
                "locales/*",
                "locales/*/*",
                "locales/*/*/*",
            ]
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
            "Programming Language :: Python :: 3.14",
            "License :: OSI Approved :: GNU General Public License"
            + " v3 or later (GPLv3+)",
            "Operating System :: OS Independent",
        ],
        install_requires=["roman>=3.3"],
        python_requires=">=3.12",
    )
