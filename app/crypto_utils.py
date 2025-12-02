import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes


def load_private_key(path: str = "student_private.pem"):
    """
    Load student's RSA private key (PEM format).
    Used for decrypting the encrypted seed from instructor API.
    """
    with open(path, "rb") as f:
        key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    return key


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt the Base64-encoded encrypted seed.

    Algorithm:
        RSA + OAEP padding
        MGF1 = SHA-256
        Hash = SHA-256
        Label = None

    Returns:
        64-character hex seed (string)
    """

    # 1. Base64 decode
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    # 2. RSA OAEP-SHA256 decrypt
    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 3. Convert decrypted bytes → UTF-8 string
    hex_seed = decrypted_bytes.decode()

    # 4. Validate: must be 64-char hex
    if len(hex_seed) != 64:
        raise ValueError("Invalid seed length (must be 64 hex chars)")

    allowed = "0123456789abcdef"
    if any(ch not in allowed for ch in hex_seed):
        raise ValueError("Invalid hex characters in seed")

    return hex_seed
