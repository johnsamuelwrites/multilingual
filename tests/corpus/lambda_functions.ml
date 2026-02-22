# -*- coding: utf-8 -*-
# Lambda Functions: Functional programming with lambdas
# Demonstrates map, filter, and reduce with lambda expressions

from functools import reduce

# Map: Apply function to all elements
let numbers = [1, 2, 3, 4, 5]
let doubled = list(map(lambda x: x * 2, numbers))
print(doubled)

# Filter: Keep elements that satisfy condition
let evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)

# Reduce: Accumulate values
let sum_result = reduce(lambda x, y: x + y, numbers)
print(sum_result)
