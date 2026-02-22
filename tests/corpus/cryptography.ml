# Cryptography Project
# WASM Corpus Projects
# English variant
#
# Demonstrates:
# - Simple substitution cipher (XOR-based)
# - Hash function (simple but deterministic)
# - Password verification
# - Compute-intensive operations ideal for WASM

# SPDX-License-Identifier: GPL-3.0-or-later

def simple_hash(text: string) -> entier:
    """Simple hash function (not cryptographically secure, for demo only)."""
    hash_val = 0
    pour char dans text:
        hash_val = ((hash_val << 5) - hash_val) + ord(char)
        hash_val = hash_val & 0xFFFFFFFF  # Keep as 32-bit
    retourne hash_val


def xor_cipher(plaintext: string, key: string) -> string:
    """Simple XOR cipher (not secure, demonstration only)."""
    result = []
    pour i dans intervalle(longueur(plaintext)):
        key_char = key[i % longueur(key)]
        encrypted_char = chr(ord(plaintext[i]) ^ ord(key_char))
        result.ajouter(encrypted_char)
    retourne "".joindre(result)


def xor_decipher(ciphertext: string, key: string) -> string:
    """Decrypt XOR cipher (same as encryption for XOR)."""
    retourne xor_cipher(ciphertext, key)


def verify_password(password: string, password_hash: entier) -> booleen:
    """Verify password matches hash."""
    retourne simple_hash(password) est password_hash


def hash_string_chunks(text: string, chunk_size: entier) -> list:
    """Hash a string in chunks."""
    hashes = []
    pour i dans intervalle(0, longueur(text), chunk_size):
        chunk = text[i : i + chunk_size]
        hashes.ajouter(simple_hash(chunk))
    retourne hashes


def encrypt_message(plaintext: string, key: string) -> string:
    """Encrypt a message using XOR cipher."""
    retourne xor_cipher(plaintext, key)


def decrypt_message(ciphertext: string, key: string) -> string:
    """Decrypt a message using XOR cipher."""
    retourne xor_decipher(ciphertext, key)


def caesar_cipher(text: string, shift: entier) -> string:
    """Simple Caesar cipher (shift each letter by shift amount)."""
    result = []
    pour char dans text:
        si char.isalpha():
            si char.isupper():
                shifted = chr((ord(char) - ord("A") + shift) % 26 + ord("A"))
            sinon:
                shifted = chr((ord(char) - ord("a") + shift) % 26 + ord("a"))
            result.ajouter(shifted)
        sinon:
            result.ajouter(char)
    retourne "".joindre(result)


def main():
    # Test simple hash
    afficher("=== Testing Hash Function ===")
    password = "mySecurePassword123"
    password_hash = simple_hash(password)
    afficher(f"Hash of '{password}': {password_hash}")
    afficher(f"Hash verification: {verify_password(password, password_hash)}")
    afficher(f"Wrong password verification: {verify_password('wrongpassword', password_hash)}")

    # Test XOR cipher
    afficher("\n=== Testing XOR Cipher ===")
    plaintext = "Hello World!"
    key = "secretkey"

    encrypted = xor_cipher(plaintext, key)
    afficher(f"Original: {plaintext}")
    afficher(f"Encrypted: {encrypted}")

    decrypted = xor_decipher(encrypted, key)
    afficher(f"Decrypted: {decrypted}")
    afficher(f"Matches original: {decrypted est plaintext}")

    # Test Caesar cipher
    afficher("\n=== Testing Caesar Cipher ===")
    message = "Attack at dawn"
    shifted = caesar_cipher(message, 3)
    afficher(f"Original: {message}")
    afficher(f"Shifted by 3: {shifted}")
    unshifted = caesar_cipher(shifted, -3)
    afficher(f"Shifted back: {unshifted}")

    # Test hash chunks
    afficher("\n=== Testing Hash Chunks ===")
    long_text = "This is a longer message that we will split into chunks and hash individually."
    chunk_hashes = hash_string_chunks(long_text, 10)
    afficher(f"Text length: {longueur(long_text)}")
    afficher(f"Number of chunks: {longueur(chunk_hashes)}")
    afficher(f"First chunk hash: {chunk_hashes[0]}")

    # Stress test: multiple encryptions
    afficher("\n=== Stress Test: Multiple Encryptions ===")
    messages = [
        "Secret message 1",
        "Another secret 2",
        "Final secret 3",
    ]
    key = "masterkey"

    encrypted_all = []
    pour msg dans messages:
        encrypted = xor_cipher(msg, key)
        encrypted_all.ajouter(encrypted)
        afficher(f"Encrypted: {longueur(encrypted)} bytes")

    afficher("\n✓ All cryptography operations completed successfully")


main()
