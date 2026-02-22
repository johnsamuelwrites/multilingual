# Image Processing Project
# WASM Corpus Projects
# English variant
#
# Demonstrates:
# - Simple image filters (blur, edge detection)
# - Pixel manipulation
# - Image transformation
# - SIMD-suitable operations for WASM

# SPDX-License-Identifier: GPL-3.0-or-later

def create_test_image(width: entier, height: entier) -> list:
    """Create a simple test image (grayscale pixel values)."""
    image = []
    pour y dans intervalle(height):
        row = []
        pour x dans intervalle(width):
            # Create a simple gradient pattern
            pixel = ((x + y) * 255) // (width + height)
            row.ajouter(pixel)
        image.ajouter(row)
    retourne image


def blur_filter(image: list, kernel_size: entier) -> list:
    """Apply simple box blur filter."""
    height = longueur(image)
    si height est 0:
        retourne []

    width = longueur(image[0])
    result = []

    pour y dans intervalle(height):
        row = []
        pour x dans intervalle(width):
            # Calculate average of surrounding pixels
            sum_val = 0
            count = 0

            pour dy dans intervalle(-kernel_size, kernel_size + 1):
                pour dx dans intervalle(-kernel_size, kernel_size + 1):
                    ny = y + dy
                    nx = x + dx

                    si (ny >= 0) et (ny < height) et (nx >= 0) et (nx < width):
                        sum_val = sum_val + image[ny][nx]
                        count = count + 1

            averaged = sum_val // count si count > 0 sinon 0
            row.ajouter(averaged)

        result.ajouter(row)

    retourne result


def edge_detection(image: list) -> list:
    """Simple Sobel edge detection."""
    height = longueur(image)
    si height < 3:
        retourne image

    width = longueur(image[0])
    si width < 3:
        retourne image

    result = []

    pour y dans intervalle(1, height - 1):
        row = []
        pour x dans intervalle(1, width - 1):
            # Simplified Sobel operator
            gx = (image[y-1][x+1] + 2*image[y][x+1] + image[y+1][x+1]) - \
                 (image[y-1][x-1] + 2*image[y][x-1] + image[y+1][x-1])

            gy = (image[y+1][x-1] + 2*image[y+1][x] + image[y+1][x+1]) - \
                 (image[y-1][x-1] + 2*image[y-1][x] + image[y-1][x+1])

            # Calculate magnitude (simplified)
            magnitude = (gx * gx + gy * gy) ** 0.5
            # Clamp to 0-255
            magnitude = entier(magnitude) si magnitude < 256 sinon 255
            row.ajouter(magnitude)

        result.ajouter(row)

    retourne result


def grayscale_to_binary(image: list, threshold: entier) -> list:
    """Convert grayscale image to binary (black and white)."""
    binary = []
    pour row dans image:
        binary_row = []
        pour pixel dans row:
            binary_val = 1 si pixel >= threshold sinon 0
            binary_row.ajouter(binary_val)
        binary.ajouter(binary_row)
    retourne binary


def invert_colors(image: list) -> list:
    """Invert colors (255 - pixel for each pixel)."""
    inverted = []
    pour row dans image:
        inverted_row = []
        pour pixel dans row:
            inverted_row.ajouter(255 - pixel)
        inverted.ajouter(inverted_row)
    retourne inverted


def calculate_histogram(image: list) -> list:
    """Calculate histogram (frequency of each brightness level)."""
    histogram = []
    pour i dans intervalle(256):
        histogram.ajouter(0)

    pour row dans image:
        pour pixel dans row:
            si pixel >= 0 et pixel < 256:
                histogram[pixel] = histogram[pixel] + 1

    retourne histogram


def main():
    # Create test image
    afficher("=== Image Processing Demonstration ===")
    afficher("Creating test image (8x8)...")
    image = create_test_image(8, 8)
    afficher(f"Image created: {longueur(image)}x{longueur(image[0])}")

    # Show original image
    afficher("\nOriginal image (first row):")
    afficher(image[0])

    # Apply blur
    afficher("\n=== Applying Blur Filter ===")
    blurred = blur_filter(image, 1)
    afficher("Blurred image (first row):")
    afficher(blurred[0])

    # Edge detection
    afficher("\n=== Applying Edge Detection ===")
    edges = edge_detection(image)
    afficher(f"Edge detection completed: {longueur(edges)}x{longueur(edges[0])}")
    afficher("Edge map (first row):")
    afficher(edges[0])

    # Color inversion
    afficher("\n=== Inverting Colors ===")
    inverted = invert_colors(image)
    afficher("Inverted image (first row):")
    afficher(inverted[0])

    # Binary conversion
    afficher("\n=== Converting to Binary ===")
    binary = grayscale_to_binary(image, 128)
    afficher("Binary image (first row):")
    afficher(binary[0])

    # Histogram
    afficher("\n=== Calculating Histogram ===")
    hist = calculate_histogram(image)
    # Show first 10 histogram values
    afficher(f"Histogram (first 10 buckets): {hist[0:10]}")

    # Stress test: large image
    afficher("\n=== Stress Test: Processing Large Image ===")
    large_image = create_test_image(32, 32)
    afficher(f"Created {longueur(large_image)}x{longueur(large_image[0])} image")

    blurred_large = blur_filter(large_image, 2)
    afficher("Applied blur filter to large image")

    edges_large = edge_detection(large_image)
    afficher("Applied edge detection to large image")

    afficher("\n✓ All image processing operations completed successfully")


main()
