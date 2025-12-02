#!/usr/bin/env python3
# Cron script to log 2FA codes every minute

import os
import base64
from datetime import datetime, timezone

import pyotp

SEED_PATH = "/data/seed.txt"

def read_seed():
    """Read hex seed from persistent storage."""
    try:
        with open(SEED_PATH, "r") as f:
            hex_seed = f.read().strip()
            return hex_seed
    except FileNotFoundError:
        return None

def hex_to_base32(hex_string: str):
    """Convert hex seed to base32 (TOTP requirement)."""
    raw = bytes.fromhex(hex_string)
    return base64.b32encode(raw).decode("utf-8")

def generate_totp(hex_seed: str):
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed)
    return totp.now()

def main():
    # 1. Read seed
    hex_seed = read_seed()
    if not hex_seed:
        print("Missing seed file at /data/seed.txt")
        return

    # 2. Generate TOTP
    code = generate_totp(hex_seed)

    # 3. Get UTC timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # 4. Output
    print(f"{timestamp} - 2FA Code: {code}")

if __name__ == "__main__":
    main()
