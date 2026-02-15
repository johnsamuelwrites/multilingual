#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Shared helpers for datetime resource loading."""

import json
from pathlib import Path


def load_datetime_resource(filename):
    """Load a JSON resource from multilingual datetime resources."""
    resources_dir = Path(__file__).parent.parent / "resources" / "datetime"
    resource_path = resources_dir / filename
    with open(resource_path, "r", encoding="utf-8") as resource_file:
        return json.load(resource_file)
