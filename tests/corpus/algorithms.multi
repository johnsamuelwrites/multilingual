# -*- coding: utf-8 -*-
# Algorithms: Simple algorithms (Sieve of Eratosthenes-like, FizzBuzz)

def simple_primes(limit):
    """Generate primes using a simple trial division approach."""
    let primes = []
    for num in range(2, limit + 1):
        let is_prime = True
        for divisor in range(2, num):
            if num % divisor == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes

def fizzbuzz(n):
    """Generate FizzBuzz sequence for numbers 1 to n."""
    let result = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result

# Test primes
let primes = simple_primes(30)
print(" ".join([str(p) for p in primes]))

# Test FizzBuzz
let fb = fizzbuzz(10)
for item in fb:
    print(item)
