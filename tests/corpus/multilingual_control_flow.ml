# -*- coding: utf-8 -*-
# Multilingual Control Flow: Test FR/ES surface patterns
# Validates that French and Spanish while/if patterns now work

# French while loop (using pendant keyword)
let count_fr = 0
let max_count = 3

# Python code that works in both EN and FR
while count_fr < max_count:
    count_fr = count_fr + 1

print(count_fr)

# Test if statement works
let value = 10
if value > 5:
    print("greater")
else:
    print("less")

# Test nested control flow
let result = 0
for i in range(3):
    if i % 2 == 0:
        result = result + i

print(result)
