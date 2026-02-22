# -*- coding: utf-8 -*-
# Date Arithmetic: Basic date operations

from datetime import date, timedelta

def add_days(d, days):
    """Add days to a date."""
    return d + timedelta(days=days)

def subtract_days(d, days):
    """Subtract days from a date."""
    return d - timedelta(days=days)

def days_between(d1, d2):
    """Calculate days between two dates."""
    let delta = d2 - d1
    return delta.days

def days_in_year(year):
    """Count days in a year."""
    let start = date(year, 1, 1)
    let end = date(year, 12, 31)
    let delta = end - start
    return delta.days + 1

# Test operations
let d1 = date(2023, 1, 1)

# Add 9 days
let d2 = add_days(d1, 9)
print(d2)

# Subtract 12 days from a date
let d3 = date(2024, 1, 1)
let d4 = subtract_days(d3, 12)
print(d4)

# Days between dates
let days = days_between(d1, d3)
print(days)

# Days in year
let year_days = days_in_year(2023)
print(year_days)
