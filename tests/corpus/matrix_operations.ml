# Matrix Operations Project
# WASM Corpus Projects
# English variant
#
# Demonstrates:
# - Matrix multiplication (compute-intensive, WASM sweet spot)
# - Matrix transpose
# - Determinant calculation
# - Performance-sensitive operations

# SPDX-License-Identifier: GPL-3.0-or-later

def create_identity_matrix(n: int) -> list:
    """Create n x n identity matrix."""
    result = []
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(1)
            else:
                row.append(0)
        result.append(row)
    return result


def create_test_matrix(n: int) -> list:
    """Create n x n test matrix with sequential values."""
    result = []
    counter = 1
    for i in range(n):
        row = []
        for j in range(n):
            row.append(counter)
            counter = counter + 1
        result.append(row)
    return result


def matrix_multiply(a: list, b: list) -> list:
    """Multiply two matrices."""
    m = len(a)
    n = len(a[0])
    p = len(b[0])

    result = []
    for i in range(m):
        row = []
        for j in range(p):
            sum_val = 0
            for k in range(n):
                sum_val = sum_val + (a[i][k] * b[k][j])
            row.append(sum_val)
        result.append(row)

    return result


def matrix_transpose(matrix: list) -> list:
    """Transpose a matrix (swap rows and columns)."""
    if len(matrix) == 0:
        return []

    rows = len(matrix)
    cols = len(matrix[0])

    result = []
    for j in range(cols):
        row = []
        for i in range(rows):
            row.append(matrix[i][j])
        result.append(row)

    return result


def matrix_determinant_2x2(matrix: list) -> float:
    """Calculate determinant of a 2x2 matrix."""
    return (matrix[0][0] * matrix[1][1]) - (matrix[0][1] * matrix[1][0])


def matrix_determinant_3x3(matrix: list) -> float:
    """Calculate determinant of a 3x3 matrix using rule of Sarrus."""
    a = matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
    b = matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
    c = matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    return a - b + c


def frobenius_norm(matrix: list) -> float:
    """Calculate Frobenius norm of matrix."""
    sum_of_squares = 0
    for row in matrix:
        for element in row:
            sum_of_squares = sum_of_squares + (element * element)
    return sum_of_squares ** 0.5


def main():
    print("=== Testing 2x2 Matrices ===")
    a2 = [[1, 2], [3, 4]]
    b2 = [[5, 6], [7, 8]]

    result2 = matrix_multiply(a2, b2)
    print("2x2 Multiplication result:")
    for row in result2:
        print(row)

    print("\n=== Testing Identity Matrix ===")
    identity = create_identity_matrix(3)
    print("3x3 Identity matrix:")
    for row in identity:
        print(row)

    print("\n=== Testing Transpose ===")
    test_matrix = create_test_matrix(3)
    print("Original 3x3 test matrix:")
    for row in test_matrix:
        print(row)

    transposed = matrix_transpose(test_matrix)
    print("Transposed:")
    for row in transposed:
        print(row)

    print("\n=== Testing Determinant ===")
    det2 = matrix_determinant_2x2(a2)
    print(f"Det(2x2) = {det2}")

    det3 = matrix_determinant_3x3(test_matrix)
    print(f"Det(3x3) = {det3}")

    print("\n=== Testing Larger Matrix Multiplication ===")
    a_large = create_test_matrix(4)
    b_large = create_test_matrix(4)
    result_large = matrix_multiply(a_large, b_large)
    print(f"4x4 matrix multiplication completed. First row: {result_large[0]}")

    print("\nAll matrix operations completed successfully")


main()
