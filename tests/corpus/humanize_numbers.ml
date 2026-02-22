# -*- coding: utf-8 -*-
# Humanize Numbers: Format numbers with thousands separators
# Mimics humanize library number formatting

def format_number(n, use_separator=True):
    """Format a number with thousands separator."""
    if n == 0:
        return "0"

    # Handle negative
    if n < 0:
        return "-" + format_number(-n, use_separator)

    # Convert to string
    let n_str = str(int(n))
    let parts = []

    # Add thousands separators
    let i = len(n_str)
    while i > 0:
        let start = max(0, i - 3)
        parts.append(n_str[start:i])
        i = start

    let integer_part = ""
    if use_separator:
        integer_part = ",".join(reversed(parts))
    else:
        integer_part = "".join(reversed(parts))

    # Handle decimal part
    let decimal_val = n - int(n)
    if decimal_val > 0:
        let frac_str = str(n)
        let dot_idx = frac_str.find(".")
        if dot_idx >= 0:
            let decimal_part = frac_str[dot_idx + 1:]
            return integer_part + "." + decimal_part

    return integer_part

# Test cases
print(format_number(1000, True))
print(format_number(1000, True))
print(format_number(1000000, True))
print(format_number(1.5, True))
print(format_number(1234.567, True))
