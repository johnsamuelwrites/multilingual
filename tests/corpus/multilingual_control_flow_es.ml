# -*- coding: utf-8 -*-
# Multilingual Control Flow - Spanish: Test ES surface patterns
# Validates Spanish mientras/si patterns work with surface normalization

# Spanish while loop (using mientras keyword)
sea count_es = 0
sea max_count = 3

mientras count_es < max_count:
    count_es = count_es + 1

print(count_es)

# Test if statement in Spanish
sea value = 10
si value > 5:
    print("greater")
sino:
    print("less")

# Test nested control flow
sea result = 0
para item en range(3):
    si item % 2 == 0:
        result = result + item

print(result)
