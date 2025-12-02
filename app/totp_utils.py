import base64
import pyotp


def hex_to_base32(hex_seed: str) -> str:
    """
    Convert 64-character hex seed → bytes → base32 string.
    """

    # 1. Hex string → raw bytes
    seed_bytes = bytes.fromhex(hex_seed)

    # 2. Bytes → base32 → UTF-8 string (no newlines)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")

    return base32_seed


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current TOTP code from a 64-character hex seed.
    
    Returns:
        6-digit TOTP code string.
    """

    # Convert hex seed to base32
    base32_seed = hex_to_base32(hex_seed)

    # Create TOTP object (SHA-1, 30s period, 6 digits = defaults)
    totp = pyotp.TOTP(base32_seed)

    # Generate current 6-digit code
    code = totp.now()

    return code


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify a TOTP code with ± valid_window period tolerance.
    
    Args:
        hex_seed: 64-character hex seed
        code: 6-digit TOTP code
        valid_window: default 1 = accept ±30 seconds
    """

    # Convert hex → base32
    base32_seed = hex_to_base32(hex_seed)

    # Create TOTP object
    totp = pyotp.TOTP(base32_seed)

    # Verify with time-window tolerance
    return totp.verify(code, valid_window=valid_window)
