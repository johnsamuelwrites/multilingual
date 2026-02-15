#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Examples demonstrating multilingual date/time handling."""

from multilingualprogramming.datetime.mp_date import MPDate
from multilingualprogramming.datetime.mp_time import MPTime

# Create a date and format in multiple languages
date = MPDate(2024, 1, 15)

print("== Same date in multiple languages ==")
for lang in ["en", "fr", "es", "de", "hi", "ar", "zh", "ja"]:
    print(f"  {lang}: {date.to_string(lang)}")

# Parse dates in different languages
print("\n== Parsing dates from different languages ==")
dates_to_parse = [
    "15-January-2024",
    "15-Janvier-2024",
    "15-Enero-2024",
    "15-जनवरी-2024",
    "15-يناير-2024",
]
for datestr in dates_to_parse:
    d = MPDate.from_string(datestr)
    print(f"  '{datestr}' -> {d.year}-{d.month:02d}-{d.day:02d}")

# Time formatting
print("\n== Time in multiple scripts ==")
time = MPTime(14, 30, 0)
print(f"  English (24h): {time.to_string('en')}")
print(f"  Hindi (24h):   {time.to_string('hi')}")
print(f"  Arabic (24h):  {time.to_string('ar')}")
print(f"  English (12h): {time.to_string('en', use_24h=False)}")
print(f"  Japanese (12h): {time.to_string('ja', use_24h=False)}")

# Date arithmetic
print("\n== Date arithmetic ==")
d1 = MPDate(2024, 1, 15)
d2 = d1 + 30
print(f"  {d1.to_string('en')} + 30 days = {d2.to_string('en')}")
print(f"  Difference: {d2 - d1} days")
