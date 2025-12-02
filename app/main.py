import os
import base64
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import pyotp

SEED_PATH = "/data/seed.txt"

app = FastAPI()

# -----------------------------
# Models
# -----------------------------
class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str


# -----------------------------
# Helper Functions
# -----------------------------
def load_private_key():
    with open("student_private.pem", "rb") as f:
        key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )
    return key


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    try:
        encrypted_bytes = base64.b64decode(encrypted_seed_b64)

        decrypted = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        hex_seed = decrypted.decode()

        # Validation
        if len(hex_seed) != 64:
            raise ValueError("Invalid seed length")

        allowed = "0123456789abcdef"
        if any(ch not in allowed for ch in hex_seed):
            raise ValueError("Invalid hex seed")

        return hex_seed

    except Exception as e:
        print("Decryption error:", e)
        raise


def generate_totp_code(hex_seed: str) -> str:
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode()

    totp = pyotp.TOTP(base32_seed)
    return totp.now()


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode()

    totp = pyotp.TOTP(base32_seed)
    return totp.verify(code, valid_window=valid_window)


# -----------------------------
# Endpoint 1: POST /decrypt-seed
# -----------------------------
@app.post("/decrypt-seed")
def decrypt_seed_endpoint(req: DecryptRequest):
    try:
        private_key = load_private_key()

        hex_seed = decrypt_seed(req.encrypted_seed, private_key)

        os.makedirs("/data", exist_ok=True)
        with open(SEED_PATH, "w") as f:
            f.write(hex_seed)

        return {"status": "ok"}

    except Exception:
        raise HTTPException(500, "Decryption failed")


# -----------------------------
# Endpoint 2: GET /generate-2fa
# -----------------------------
@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(SEED_PATH):
        raise HTTPException(500, "Seed not decrypted yet")

    with open(SEED_PATH, "r") as f:
        hex_seed = f.read().strip()

    code = generate_totp_code(hex_seed)

    # Remaining time in current 30s window
    now = int(time.time())
    valid_for = 30 - (now % 30)

    return {
        "code": code,
        "valid_for": valid_for
    }


# -----------------------------
# Endpoint 3: POST /verify-2fa
# -----------------------------
@app.post("/verify-2fa")
def verify_2fa(req: VerifyRequest):
    if not req.code:
        raise HTTPException(400, "Missing code")

    if not os.path.exists(SEED_PATH):
        raise HTTPException(500, "Seed not decrypted yet")

    with open(SEED_PATH, "r") as f:
        hex_seed = f.read().strip()

    valid = verify_totp_code(hex_seed, req.code, valid_window=1)

    return {"valid": valid}
