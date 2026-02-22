# -*- coding: utf-8 -*-
# Comprehensions: List, dict, and set comprehensions
# Demonstrates concise syntax for creating collections

# List comprehension: squares of numbers
let squares = [x * x for x in range(1, 6)]
print(squares)

# Dict comprehension: number to square mapping
let num_squares = {x: x * x for x in range(1, 4)}
print(num_squares)

# Set comprehension: unique squares
let unique_squares = {x * x for x in range(1, 4)}
print(unique_squares)
