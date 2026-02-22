# -*- coding: utf-8 -*-
# List Utilities: Common list operations
# Flatten nested lists, get unique elements, chunk list into groups

# Flatten a nested list
let nested = [[1, 2], [3, 4], [5, 6]]
let flattened = []
for sublist in nested:
    for item in sublist:
        flattened.append(item)
print(flattened)

# Get unique elements while preserving order
let data = [1, 2, 2, 3, 3, 3]
let seen = set()
let unique = []
for item in data:
    if item not in seen:
        seen.add(item)
        unique.append(item)
print(unique)

# Chunk list into groups of size n
let chunk_data = [1, 2, 3, 4, 5]
let chunk_size = 2
let chunks = []
let i = 0
for _ in range(len(chunk_data)):
    if i < len(chunk_data):
        let chunk = chunk_data[i:i + chunk_size]
        chunks.append(chunk)
        i = i + chunk_size
print(chunks)
