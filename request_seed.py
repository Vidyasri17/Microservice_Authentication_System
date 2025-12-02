import json
import requests

def request_seed(student_id: str, github_repo_url: str, api_url: str):
    """
    Request encrypted seed from instructor API.
    Saves the encrypted seed into encrypted_seed.txt (DO NOT COMMIT THIS FILE).
    """

    # 1. Read the student public key in raw PEM form
    with open("student_public.pem", "r") as f:
        public_key_pem = f.read()

    # 2. Build JSON payload
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_pem
    }

    # 3. Send POST request
    try:
        response = requests.post(api_url, json=payload, timeout=10)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return None

    # 4. Parse response JSON
    if response.status_code != 200:
        print("Error from API:", response.text)
        return None

    data = response.json()

    if "encrypted_seed" not in data:
        print("Invalid response format:", data)
        return None

    encrypted_seed = data["encrypted_seed"]

    # 5. Save encrypted seed to file (DO NOT COMMIT THIS FILE)
    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)

    print("\nEncrypted seed received and saved to encrypted_seed.txt\n")
    return encrypted_seed


if __name__ == "__main__":
    API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

    # TODO: replace with your actual ID
    STUDENT_ID = "23A91A6161"

    GITHUB_REPO_URL = "https://github.com/Vidyasri17/Microservice_Authentication_System"

    request_seed(STUDENT_ID, GITHUB_REPO_URL, API_URL)
