# -*- coding: utf-8 -*-
# Multilingual Control Flow - French: Test FR surface patterns
# Validates French while/if patterns work with surface normalization

# French while loop (using tantque keyword)
soit count_fr = 0
soit max_count = 3

tantque count_fr < max_count:
    count_fr = count_fr + 1

print(count_fr)

# Test if statement in French
soit value = 10
si value > 5:
    print("greater")
sinon:
    print("less")

# Test nested control flow
soit result = 0
pour i dans range(3):
    si i % 2 == 0:
        result = result + i

print(result)
