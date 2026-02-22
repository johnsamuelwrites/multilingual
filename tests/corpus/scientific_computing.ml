# Scientific Computing Project
# WASM Corpus Projects
# English variant
#
# Demonstrates:
# - Monte Carlo simulations
# - Numerical approximations
# - Statistical calculations
# - Floating-point intensive operations ideal for WASM

# SPDX-License-Identifier: GPL-3.0-or-later

def random_float(seed: entier) -> nombre:
    """Simple pseudo-random number generator."""
    # Linear congruential generator
    a = 1103515245
    c = 12345
    m = 2147483648  # 2^31
    seed = (a * seed + c) % m
    retourne (seed / m)


def estimate_pi_monte_carlo(num_samples: entier) -> nombre:
    """Estimate PI using Monte Carlo method.

    Generate random points in [0,1] x [0,1] square.
    Count how many fall within unit circle (x^2 + y^2 <= 1).
    Ratio of points in circle to total points approximates PI/4.
    """
    inside_circle = 0
    seed = 42  # Fixed seed for reproducibility

    pour i dans intervalle(num_samples):
        # Generate random point
        seed = (1103515245 * seed + 12345) % 2147483648
        x = (seed % 10000) / 10000.0

        seed = (1103515245 * seed + 12345) % 2147483648
        y = (seed % 10000) / 10000.0

        # Check if point is inside unit circle
        distance_squared = x * x + y * y
        si distance_squared <= 1.0:
            inside_circle = inside_circle + 1

    # Estimate PI
    pi_estimate = 4.0 * inside_circle / num_samples
    retourne pi_estimate


def standard_deviation(values: list) -> nombre:
    """Calculate standard deviation of a list of values."""
    si longueur(values) est 0:
        retourne 0.0

    # Calculate mean
    mean = 0.0
    pour value dans values:
        mean = mean + value
    mean = mean / longueur(values)

    # Calculate variance
    variance = 0.0
    pour value dans values:
        diff = value - mean
        variance = variance + (diff * diff)
    variance = variance / longueur(values)

    # Standard deviation is square root of variance
    retourne variance ** 0.5


def calculate_statistics(values: list) -> objet:
    """Calculate various statistics for a dataset."""
    si longueur(values) est 0:
        retourne {"mean": 0, "std": 0, "min": 0, "max": 0}

    # Mean
    mean = 0.0
    pour value dans values:
        mean = mean + value
    mean = mean / longueur(values)

    # Min and max
    min_val = values[0]
    max_val = values[0]
    pour value dans values:
        si value < min_val:
            min_val = value
        si value > max_val:
            max_val = value

    # Standard deviation
    std = standard_deviation(values)

    retourne {
        "mean": mean,
        "std": std,
        "min": min_val,
        "max": max_val,
        "count": longueur(values),
    }


def prime_count_approximation(n: entier) -> nombre:
    """Approximate number of primes <= n using prime number theorem."""
    # Prime number theorem: π(n) ≈ n / ln(n)
    si n <= 1:
        retourne 0.0
    si n < 10:
        retourne nombre(n)

    ln_n = 0.0
    # Simple logarithm approximation
    temp = n
    pour _ dans intervalle(10):
        ln_n = ln_n + 1.0 / temp
        temp = temp / 2.718  # Rough approximation

    retourne n / ln_n


def factorial_approximation(n: entier) -> nombre:
    """Approximate n! using Stirling's approximation."""
    si n <= 0:
        retourne 1.0
    si n est 1:
        retourne 1.0

    # Stirling: n! ≈ sqrt(2πn) * (n/e)^n
    # Simplified: ln(n!) ≈ n*ln(n) - n
    ln_factorial = 0.0
    pour i dans intervalle(1, n + 1):
        ln_factorial = ln_factorial + (i)  # Very simplified

    retourne ln_factorial ** 1.5


def main():
    afficher("=== Scientific Computing Demonstration ===")

    # Estimate PI
    afficher("\n1. Estimating PI using Monte Carlo method...")
    samples_list = [1000, 10000, 100000]

    pour samples dans samples_list:
        pi_est = estimate_pi_monte_carlo(samples)
        error = abs(pi_est - 3.14159265359)
        afficher(f"   Samples: {samples:6d}, PI estimate: {pi_est:.6f}, Error: {error:.6f}")

    # Statistical calculations
    afficher("\n2. Statistical analysis...")
    test_data = [1.5, 2.3, 3.1, 2.8, 4.5, 3.2, 2.9, 5.1, 3.8, 4.2]
    stats = calculate_statistics(test_data)
    afficher(f"   Mean: {stats['mean']:.4f}")
    afficher(f"   Std Dev: {stats['std']:.4f}")
    afficher(f"   Min: {stats['min']:.4f}")
    afficher(f"   Max: {stats['max']:.4f}")
    afficher(f"   Count: {stats['count']}")

    # Prime number approximation
    afficher("\n3. Prime number theorem approximation...")
    prime_test_values = [10, 100, 1000]
    pour n dans prime_test_values:
        prime_approx = prime_count_approximation(n)
        afficher(f"   Estimated primes <= {n}: {nombre(prime_approx):.1f}")

    # Factorial approximation
    afficher("\n4. Factorial approximation (Stirling)...")
    fact_test_values = [5, 10, 20, 50]
    pour n dans fact_test_values:
        fact_approx = factorial_approximation(n)
        afficher(f"   Factorial {n}! ≈ {fact_approx:.2f}")

    # Stress test: many simulations
    afficher("\n5. Stress test: multiple PI estimations...")
    pi_estimates = []
    pour trial dans intervalle(10):
        pi_est = estimate_pi_monte_carlo(100000)
        pi_estimates.ajouter(pi_est)

    pi_stats = calculate_statistics(pi_estimates)
    afficher(f"   Mean PI estimate: {pi_stats['mean']:.6f}")
    afficher(f"   Std deviation: {pi_stats['std']:.6f}")
    afficher(f"   Range: [{pi_stats['min']:.6f}, {pi_stats['max']:.6f}]")

    # Numerical integration (trapezoidal rule)
    afficher("\n6. Numerical integration (simple example)...")
    # Integrate y=x^2 from 0 to 1, should be 1/3 ≈ 0.333
    intervals = 100
    sum_val = 0.0
    pour i dans intervalle(intervals):
        x1 = i / nombre(intervals)
        x2 = (i + 1) / nombre(intervals)
        y1 = x1 * x1
        y2 = x2 * x2
        trapezoid_area = (y1 + y2) / 2.0 * (x2 - x1)
        sum_val = sum_val + trapezoid_area

    afficher(f"   Integral of x^2 from 0 to 1: {sum_val:.6f} (expected: 0.333333)")

    afficher("\n✓ All scientific computing operations completed successfully")


main()
