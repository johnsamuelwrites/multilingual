# -*- coding: utf-8 -*-
# Performance: Testing with larger data structures
# Tests list operations with 1000 elements

# Create list of 1000 elements
let numbers = list(range(1000))

# Print length
print(len(numbers))

# Print last element
print(numbers[-1])

# Sum first 100 elements
let partial_sum = sum(numbers[0:100])
print(partial_sum)
