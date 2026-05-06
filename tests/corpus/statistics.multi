# -*- coding: utf-8 -*-
# Statistics: Basic statistical calculations
# Calculate mean, median, and mode of a dataset

from collections import Counter

# Sample dataset
let numbers = [1, 2, 3, 3, 4, 5, 6, 7, 8, 9]

# Calculate mean
let mean = sum(numbers) / len(numbers)
print(mean)

# Calculate median
let sorted_nums = sorted(numbers)
let n = len(sorted_nums)
let median = sorted_nums[n // 2]
print(median)

# Calculate mode (most frequent element)
let counter = Counter(numbers)
let mode = counter.most_common(1)[0][0]
print(mode)
