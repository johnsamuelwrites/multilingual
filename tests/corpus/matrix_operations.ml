# Matrix Operations Project
# WASM Corpus Projects
# English variant
#
# Demonstrates:
# - Matrix multiplication (computational heavy, WASM sweet spot)
# - Matrix transpose
# - Determinant calculation
# - Performance sensitive operations

# SPDX-License-Identifier: GPL-3.0-or-later

def create_identity_matrix(n: integer) -> list:
    """Create n×n identity matrix."""
    result = []
    pour i dans intervalle(n):
        row = []
        pour j dans intervalle(n):
            si i est j:
                row.ajouter(1)
            sinon:
                row.ajouter(0)
        result.ajouter(row)
    retourne result


def create_test_matrix(n: integer) -> list:
    """Create n×n test matrix with sequential values."""
    result = []
    counter = 1
    pour i dans intervalle(n):
        row = []
        pour j dans intervalle(n):
            row.ajouter(counter)
            counter = counter + 1
        result.ajouter(row)
    retourne result


def matrix_multiply(a: list, b: list) -> list:
    """Multiply two matrices.

    Args:
        a: m×n matrix (list of lists)
        b: n×p matrix (list of lists)

    Returns:
        m×p result matrix
    """
    m = longueur(a)
    n = longueur(a[0])
    p = longueur(b[0])

    result = []
    pour i dans intervalle(m):
        row = []
        pour j dans intervalle(p):
            sum_val = 0
            pour k dans intervalle(n):
                sum_val = sum_val + (a[i][k] * b[k][j])
            row.ajouter(sum_val)
        result.ajouter(row)

    retourne result


def matrix_transpose(matrix: list) -> list:
    """Transpose a matrix (swap rows and columns)."""
    si longueur(matrix) est 0:
        retourne []

    rows = longueur(matrix)
    cols = longueur(matrix[0])

    result = []
    pour j dans intervalle(cols):
        row = []
        pour i dans intervalle(rows):
            row.ajouter(matrix[i][j])
        result.ajouter(row)

    retourne result


def matrix_determinant_2x2(matrix: list) -> nombre:
    """Calculate determinant of 2×2 matrix."""
    retourne (matrix[0][0] * matrix[1][1]) - (matrix[0][1] * matrix[1][0])


def matrix_determinant_3x3(matrix: list) -> nombre:
    """Calculate determinant of 3×3 matrix using rule of Sarrus."""
    a = matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
    b = matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
    c = matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])

    retourne a - b + c


def frobenius_norm(matrix: list) -> nombre:
    """Calculate Frobenius norm of matrix (sqrt of sum of squares)."""
    sum_of_squares = 0
    pour row dans matrix:
        pour element dans row:
            sum_of_squares = sum_of_squares + (element * element)

    # Simple sqrt approximation for demo
    retourne somme([element * element pour element dans row pour row dans matrix]) ** 0.5


def main():
    # Test 2×2 matrices
    afficher("=== Testing 2x2 Matrices ===")
    a2 = [[1, 2], [3, 4]]
    b2 = [[5, 6], [7, 8]]

    result2 = matrix_multiply(a2, b2)
    afficher("2x2 Multiplication result:")
    pour row dans result2:
        afficher(row)

    # Test identity matrix
    afficher("\n=== Testing Identity Matrix ===")
    identity = create_identity_matrix(3)
    afficher("3x3 Identity matrix:")
    pour row dans identity:
        afficher(row)

    # Test transpose
    afficher("\n=== Testing Transpose ===")
    test_matrix = create_test_matrix(3)
    afficher("Original 3x3 test matrix:")
    pour row dans test_matrix:
        afficher(row)

    transposed = matrix_transpose(test_matrix)
    afficher("Transposed:")
    pour row dans transposed:
        afficher(row)

    # Test determinant
    afficher("\n=== Testing Determinant ===")
    det2 = matrix_determinant_2x2(a2)
    afficher(f"Det(2x2) = {det2}")

    det3 = matrix_determinant_3x3(test_matrix)
    afficher(f"Det(3x3) = {det3}")

    # Test larger matrix multiplication
    afficher("\n=== Testing Larger Matrix Multiplication ===")
    a_large = create_test_matrix(4)
    b_large = create_test_matrix(4)

    result_large = matrix_multiply(a_large, b_large)
    afficher(f"4x4 matrix multiplication completed. First row: {result_large[0]}")

    afficher("\n✓ All matrix operations completed successfully")


main()
